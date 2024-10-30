from django.db import models
from django.contrib.auth.models import User
from posts.models import Post
from comments.models import Comment  # Assuming you have a Comment model


class Report(models.Model):
    """
    Model for reporting abusive content, which can be related to a specific
    post or comment.
    Attributes:
        reporter (User): The user who reported the content.
        post (Post): The post that was reported, if applicable.
        comment (Comment): The comment that was reported, if applicable.
        reason (str): The reason for the report (abuse, spam, hate, other).
        description (str): Optional details about the report.
        status (str): The status of the report (Pending, Reviewed).
        created_at (datetime): The timestamp when the report was created.
    """
    REASONS = [
        ('abuse', 'Abuse or Harassment'),
        ('spam', 'Spam or Misleading'),
        ('hate', 'Hate Speech'),
        ('other', 'Other'),
    ]

    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports"
        )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports"
        )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports"
        )
    reason = models.CharField(max_length=20, choices=REASONS)
    description = models.TextField(blank=True)  # Optional
    status = models.CharField(
        max_length=20,
        default='Pending',
        choices=[('Pending', 'Pending'), ('Reviewed', 'Reviewed')]
        )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.post:
            target = self.post
        elif self.comment:
            target = self.comment
        else:
            target = "No target"
        return f"Report by {self.reporter} on {target}"
