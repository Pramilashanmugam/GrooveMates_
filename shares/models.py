from django.db import models
from django.contrib.auth.models import User
from posts.models import Post

class Share(models.Model):
    """
    Model representing a share action on a post by a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shares")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="shared_posts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'post']  # Ensure user can share a post only once

    def __str__(self):
        return f"{self.user.username} shared '{self.post.event}'"