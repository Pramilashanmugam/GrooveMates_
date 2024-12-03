from django.db import models
from django.contrib.auth.models import User
from posts.models import Post


class Share(models.Model):
    """
    Model representing a share action on a post by a user.

    This model tracks the association between a user and a post that the user
    has shared. It also records the timestamp of when the share was created.

    Attributes:
        - `user`: A foreign key to the `User` model representing the user who
        shared the post.
        - `post`: A foreign key to the `Post` model representing the post that
        was shared.
        - `created_at`: A timestamp indicating when the share was created.

    Meta:
        - `ordering`: Orders shares in descending order of creation date.
        - `unique_together`: Ensures a user can share a specific post only
        once.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shares",  # Allows reverse lookup from User to shares
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        # Allows reverse lookup from Post to shared shares
        related_name="shared_posts",
    )
    # Automatically sets the creation timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Orders shares by the most recent first
        # Ensures a user cannot share the same post multiple times
        unique_together = ['user', 'post']

    def __str__(self):
        """
        String representation of the Share instance.

        Returns:
            str: A string in the format "username shared 'post_title'".
        """
        return f"{self.user.username} shared '{self.post.event}'"
