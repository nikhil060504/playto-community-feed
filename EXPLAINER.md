# How I Solved the Three Technical Challenges

This document explains my approach to the three main problems in this assignment. I'll try to keep it practical and explain not just *what* I did, but *why* certain approaches work better than others.

---

## Problem 1: Loading Comment Threads Without Killing the Database

### The Issue

Imagine a post with 50 comments, some of which have replies. The naive way to load this would be:

1. Get the post
2. Get all comments for that post
3. For each comment, get the author
4. For each comment, check if it has replies
5. For those replies, get their authors
6. ...and so on

You end up with hundreds of database queries, which is terrible for performance. This is called the "N+1 problem" - you do 1 query for the parent, then N queries for the children.

### How I Fixed It

Django has tools specifically for this: `select_related` and `prefetch_related`. The idea is to load all the data you need in just a few queries upfront, then access it from memory.

Here's the comment model:

```python
class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies')
    content = models.TextField()
    depth = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0
        super().save(*args, **kwargs)
```

The `parent` field points to another comment (or null for top-level comments). This is called an "adjacency list" - it's simple and works well with Django's ORM.

Then when fetching comments, I do this:

```python
def get_post_comments_tree(post):
    root_comments = Comment.objects.filter(
        post=post,
        parent=None
    ).select_related('author').prefetch_related(
        Prefetch(
            'replies',
            queryset=Comment.objects.select_related('author').prefetch_related(
                'replies__author',
            ).order_by('created_at')
        )
    ).order_by('created_at')
    
    return root_comments
```

What this does:
- Gets all root comments (those without a parent)
- Uses `select_related('author')` to join with the users table in one query
- Uses `prefetch_related` to fetch all replies in a separate query
- Recursively prefetches authors for nested replies

The result? About 3-4 queries total, no matter how many comments there are. Django loads everything into memory, and then the serializer just accesses cached data.

### Why Not Use MPTT?

There's a library called django-mptt that uses a different tree structure (Modified Preorder Tree Traversal). It's faster for reads, but:
- Way more complex to understand
- Harder to modify (moving/deleting nodes requires renumbering)
- Overkill for a simple comment thread that only goes 3-4 levels deep

For this use case, the adjacency list with proper prefetching is simpler and good enough.

---

## Problem 2: Calculating a 24-Hour Leaderboard

### The Requirement

Show the top 5 users by karma earned in the last 24 hours. The catch: I can't just store a `daily_karma` field on the User model and update it whenever someone gets a like. It has to be calculated dynamically from the like history.

### Why This Is Tricky

Every like has a timestamp. To get someone's 24-hour karma, I need to:
1. Find all likes on their content
2. Filter to only likes from the last 24 hours
3. Sum up the karma values (5 for post likes, 1 for comment likes)
4. Do this for every user and sort by the total

If you do this wrong, you'll end up querying the database separately for each user, which is slow.

### The Solution

I use Django's aggregation features to do this in a single query:

```python
from django.utils import timezone
from datetime import timedelta

def get_top_users_24h(limit=5):
    time_threshold = timezone.now() - timedelta(hours=24)
    
    top_users = User.objects.filter(
        likes_received__created_at__gte=time_threshold
    ).annotate(
        karma_24h=Sum('likes_received__karma_value')
    ).order_by('-karma_24h')[:limit]
    
    return top_users
```

Here's what happens:
- `likes_received__created_at__gte=time_threshold` filters to only recent likes
- `annotate(karma_24h=Sum(...))` groups by user and sums their karma
- `order_by('-karma_24h')` sorts descending
- `[:limit]` grabs the top 5

Django translates this to a SQL query that looks roughly like:

```sql
SELECT user.*, SUM(like.karma_value) AS karma_24h
FROM user
INNER JOIN like ON user.id = like.content_author_id
WHERE like.created_at >= '2024-01-30 22:00:00'
GROUP BY user.id
ORDER BY karma_24h DESC
LIMIT 5;
```

One query, done.

### Why Store karma_value on Each Like?

The Like model stores whether it was for a post (5 points) or a comment (1 point):

```python
class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes_given')
    content_author = models.ForeignKey(User, related_name='likes_received')
    karma_value = models.IntegerField()  # 5 or 1
    created_at = models.DateTimeField(auto_now_add=True)
    # ... generic foreign key stuff
```

This way, when summing karma, I don't need to check whether each like is on a post or a comment - the value is already there. It's a small denormalization that makes the query simpler.

---

## Problem 3: Preventing Duplicate Likes (Race Conditions)

### The Scenario

User clicks "like" on a post. In the few milliseconds it takes to process that request, they click again. Or even worse: two different users click "like" at the exact same moment.

Without proper handling, you could end up with duplicate like records in the database, which would:
- Give the post author double karma
- Make the like count wrong
- Break the uniqueness assumption

### The Broken Approach

Here's what doesn't work:

```python
def like_post(user, post):
    existing_like = Like.objects.filter(user=user, post=post).first()
    if existing_like:
        existing_like.delete()
    else:
        Like.objects.create(user=user, post=post)
```

The problem: between checking if a like exists and creating it, another request can sneak in. Both requests check, both see no existing like, both create a new one.

### The Fix: Database Constraints + Atomic Transactions

Step 1: Add a unique constraint at the database level:

```python
class Like(models.Model):
    # ... fields ...
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_type', 'object_id'],
                name='unique_like_per_user_per_content'
            )
        ]
```

This makes it physically impossible to have duplicate likes. If you try to insert a duplicate, the database throws an `IntegrityError`.

Step 2: Handle the error gracefully in the code:

```python
from django.db import transaction, IntegrityError

@transaction.atomic
def toggle_like(user, content_object):
    content_type = ContentType.objects.get_for_model(content_object)
    karma_value = 5 if isinstance(content_object, Post) else 1
    
    try:
        # Optimistically try to create the like
        like = Like.objects.create(
            user=user,
            content_type=content_type,
            object_id=content_object.id,
            content_author=content_object.author,
            karma_value=karma_value
        )
        
        # Success - update the like count
        content_object.like_count += 1
        content_object.save(update_fields=['like_count'])
        
        return True, karma_value
        
    except IntegrityError:
        # Like already exists, so remove it (unlike)
        Like.objects.filter(
            user=user,
            content_type=content_type,
            object_id=content_object.id
        ).delete()
        
        content_object.like_count -= 1
        content_object.save(update_fields=['like_count'])
        
        return False, -karma_value
```

Why this works:
- We first try to create a like, assuming it doesn't exist
- If it does exist, the database constraint catches it and raises an error
- We catch that error and delete the existing like instead
- The `@transaction.atomic` decorator ensures everything happens as a single unit

Even if two requests arrive at the exact same moment, the database serializes them. One succeeds in creating the like, the other gets the IntegrityError and deletes it.

### What AI Got Wrong

When I first asked ChatGPT how to handle this, it suggested:

```python
if Like.objects.filter(user=user, post=post).exists():
    # unlike
else:
    # like
```

This has the same race condition! The check and the create aren't atomic. 

I had to:
1. Add the database constraint myself
2. Wrap everything in a transaction
3. Use try-except to handle the race condition gracefully

This is a good example of where AI gives you code that works 99% of the time, but fails under concurrent load. You need to understand the underlying concepts to catch these edge cases.

---

## Testing This Stuff

### N+1 Prevention

Enable SQL logging in Django settings and watch the console when you load a post with comments. You should see about 3-4 queries total. If you see dozens of queries, something's wrong.

### Leaderboard

Create some likes with different timestamps (or manually set `created_at` in the database). The leaderboard should only count likes from the last 24 hours. I verified this by creating likes for alice from today and likes that are 26 hours old - only the recent ones counted.

### Race Conditions

This is harder to test manually, but you can:
- Open two browser tabs
- Click "like" in both at the same time
- Check the database - there should be exactly one like record

Or use curl to send simultaneous requests:

```bash
curl -X POST http://localhost:8000/api/posts/1/like/ -H "Authorization: Bearer TOKEN" &
curl -X POST http://localhost:8000/api/posts/1/like/ -H "Authorization: Bearer TOKEN" &
```

Again, only one like should exist afterward.

---

## Key Takeaways

What I learned from this:

1. **Django's ORM is powerful but not magic.** You need to understand `select_related` vs `prefetch_related`, when to annotate vs filter, and how your ORM queries translate to SQL.

2. **Database constraints are your friend.** Application-level validation can have race conditions. Database constraints are atomic and enforced by the DB itself.

3. **AI is great for boilerplate, bad at edge cases.** It'll give you working code for the happy path, but won't catch concurrency issues, N+1 problems, or security vulnerabilities. You still need to know the fundamentals.

4. **Performance matters.** The difference between 3 queries and 100 queries is the difference between a snappy app and one that falls over under load.

The code works, but more importantly, I understand *why* it works and what would break if you changed certain parts. That's what I'm hoping to demonstrate with this project.
