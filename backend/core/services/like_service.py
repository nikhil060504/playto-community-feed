from django.db import transaction, IntegrityError
from django.contrib.contenttypes.models import ContentType
from core.models import Like, Post, Comment


@transaction.atomic
def toggle_like(user, content_object):
    """
    Atomically toggle like status on a post or comment.
    
    This function handles the critical race condition problem:
    - Uses database-level unique constraint to prevent double-likes
    - Wraps everything in a transaction for atomicity
    - Returns whether the item is now liked and the karma change
    
    Args:
        user: User object giving the like
        content_object: Post or Comment being liked
    
    Returns:
        tuple: (is_liked: bool, karma_change: int)
            - is_liked: True if like was added, False if removed
            - karma_change: +5/+1 for adding like, -5/-1 for removing
    
    Example:
        >>> post = Post.objects.get(id=1)
        >>> is_liked, karma = toggle_like(request.user, post)
        >>> print(f"Liked: {is_liked}, Karma change: {karma}")
    """
    content_type = ContentType.objects.get_for_model(content_object)
    
    # Determine karma value based on content type
    karma_value = 5 if isinstance(content_object, Post) else 1
    
    try:
        # Try to create a new like - this will fail if it already exists
        like = Like.objects.create(
            user=user,
            content_type=content_type,
            object_id=content_object.id,
            content_author=content_object.author,
            karma_value=karma_value
        )
        
        # Successfully created like - update denormalized count
        content_object.like_count += 1
        content_object.save(update_fields=['like_count'])
        
        return True, karma_value
        
    except IntegrityError:
        # Like already exists (unique constraint violation)
        # This means we should remove the like (unlike)
        Like.objects.filter(
            user=user,
            content_type=content_type,
            object_id=content_object.id
        ).delete()
        
        # Update denormalized count
        content_object.like_count -= 1
        content_object.save(update_fields=['like_count'])
        
        return False, -karma_value
