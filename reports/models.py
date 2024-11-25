from django.db import models
from django.contrib.auth.models import User
from posts.models import Post

class Report(models.Model):
    """
    Model for reporting a post with relevant details.
    """
    REASONS = [
        ('inappropriate', 'Inappropriate Content'),
        ('abuse', 'Abuse or Harassment'),
        ('spam', 'Spam or Misleading'),
        ('hate', 'Hate Speech'),
        ('other', 'Other'),
    ]

    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    reason = models.CharField(max_length=20, choices=REASONS)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        default='Pending',
        choices=[('Pending', 'Pending'), ('Reviewed', 'Reviewed')]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report by {self.reporter} on Post {self.post}"
