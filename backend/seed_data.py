"""
Seed script to populate the database with sample data for testing.
Run with: python manage.py shell < seed_data.py
Or: python manage.py shell
     exec(open('seed_data.py').read())
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from core.models import User, Post, Comment, Like
from django.contrib.contenttypes.models import ContentType

print("🌱 Starting database seed...")

# Clear existing data (optional - be careful!)
print("Clearing existing data...")
Like.objects.all().delete()
Comment.objects.all().delete()
Post.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

# Create users
print("Creating users...")
users_data = [
    {'username': 'alice', 'email': 'alice@example.com', 'bio': 'Love coding and coffee ☕'},
    {'username': 'bob', 'email': 'bob@example.com', 'bio': 'Full-stack developer'},
    {'username': 'charlie', 'email': 'charlie@example.com', 'bio': 'Python enthusiast 🐍'},
    {'username': 'diana', 'email': 'diana@example.com', 'bio': 'Open source contributor'},
    {'username': 'eve', 'email': 'eve@example.com', 'bio': 'Tech blogger and mentor'},
]

users = {}
for user_data in users_data:
    user = User.objects.create_user(
        password='password123',  # Same password for all test users
        **user_data
    )
    users[user.username] = user
    print(f"  Created user: {user.username}")

# Create posts
print("\nCreating posts...")
posts_data = [
    {'author': 'alice', 'content': 'Just finished building a Django REST API! The journey from models to deployment was challenging but rewarding. 🚀'},
    {'author': 'bob', 'content': 'Hot take: TypeScript is overrated for small projects. Sometimes vanilla JS is all you need!'},
    {'author': 'charlie', 'content': 'Finally understood how async/await works in Python. asyncio is a game changer for I/O bound tasks!'},
    {'author': 'diana', 'content': 'Contributed to my first major open source project today. The maintainers were so welcoming! ❤️'},
    {'author': 'eve', 'content': 'Writing a blog post about N+1 query problems and how to solve them. Django ORM tips coming soon!'},
]

posts = []
for post_data in posts_data:
    author = users[post_data['author']]
    post = Post.objects.create(
        author=author,
        content=post_data['content']
    )
    posts.append(post)
    print(f"  Created post by {author.username}")

# Create comments
print("\nCreating comments with threading...")
comments = []

# Comments on Alice's post
c1 = Comment.objects.create(
    author=users['bob'],
    post=posts[0],
    content="Great work! What challenges did you face with race conditions?"
)
comments.append(c1)

c2 = Comment.objects.create(
    author=users['alice'],
    post=posts[0],
    parent=c1,
    content="Good question! I used database constraints and atomic transactions to prevent double-likes."
)
comments.append(c2)

c3 = Comment.objects.create(
    author=users['charlie'],
    post=posts[0],
    parent=c2,
    content="Smart approach! I've seen similar patterns with unique_together constraints."
)
comments.append(c3)

# Comments on Bob's post
c4 = Comment.objects.create(
    author=users['diana'],
    post=posts[1],
    content="Disagree! Type safety catches so many bugs before runtime."
)
comments.append(c4)

c5 = Comment.objects.create(
    author=users['eve'],
    post=posts[1],
    content="Both have their place. Use the right tool for the job!"
)
comments.append(c5)

# Comments on Charlie's post
c6 = Comment.objects.create(
    author=users['alice'],
    post=posts[2],
    content="Have you tried httpx for async HTTP requests? It's amazing!"
)
comments.append(c6)

c7 = Comment.objects.create(
    author=users['charlie'],
    post=posts[2],
    parent=c6,
    content="Yes! httpx is like requests but async. Perfect combo."
)
comments.append(c7)

print(f"  Created {len(comments)} comments")

# Create likes (some recent, some old for leaderboard testing)
print("\nCreating likes...")

# Helper function to create likes
def create_like(user, content_obj, hours_ago=0):
    """Create a like with a specific timestamp"""
    content_type = ContentType.objects.get_for_model(content_obj)
    karma_value = 5 if isinstance(content_obj, Post) else 1
    
    like = Like.objects.create(
        user=user,
        content_type=content_type,
        object_id=content_obj.id,
        content_author=content_obj.author,
        karma_value=karma_value
    )
    
    # Manually set created_at for testing
    if hours_ago > 0:
        like.created_at = timezone.now() - timedelta(hours=hours_ago)
        like.save()
    
    # Update denormalized like_count
    content_obj.like_count += 1
    content_obj.save(update_fields=['like_count'])
    
    return like

# Recent likes (last 24 hours) - these should appear in leaderboard
create_like(users['bob'], posts[0], hours_ago=2)    # Alice gets 5 karma
create_like(users['charlie'], posts[0], hours_ago=5) # Alice gets 5 karma
create_like(users['diana'], posts[0], hours_ago=12)  # Alice gets 5 karma
create_like(users['eve'], posts[0], hours_ago=20)    # Alice gets 5 karma

create_like(users['alice'], posts[3], hours_ago=3)   # Diana gets 5 karma
create_like(users['charlie'], posts[3], hours_ago=8) # Diana gets 5 karma

create_like(users['alice'], c4, hours_ago=6)         # Diana gets 1karma
create_like(users['bob'], c4, hours_ago=10)          # Diana gets 1 karma

# Old likes (> 24 hours ago) - these should NOT appear in leaderboard
create_like(users['alice'], posts[1], hours_ago=30)  # Bob gets 5 (old)
create_like(users['diana'], posts[2], hours_ago=48)  # Charlie gets 5 (old)

print("  Created recent and old likes for leaderboard testing")

# Summary
print("\n✅ Database seeded successfully!")
print(f"   Users: {User.objects.count()}")
print(f"   Posts: {Post.objects.count()}")
print(f"   Comments: {Comment.objects.count()}")
print(f"   Likes: {Like.objects.count()}")

print("\n📊 Top users by 24h karma:")
from core.services import get_top_users_24h
top_users = get_top_users_24h(limit=5)
for i, user in enumerate(top_users, 1):
    print(f"   {i}. {user.username}: {user.karma_24h} karma")

print("\n🔐 Test credentials:")
print("   All users have password: password123")
print("   Try logging in as: alice, bob, charlie, diana, or eve")
