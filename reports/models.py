from django.db import models
from django.contrib.auth.models import User
from posts.models import Post


class Report(models.Model):
    """
    Model for reporting a post by a user with relevant details such as reason,
    description, status, and creation timestamp.

    Attributes:
        REASONS (list): A list of predefined reasons for reporting a post.
        reporter (ForeignKey): The user who is reporting the post.
        post (ForeignKey): The post that is being reported.
        reason (CharField): The reason for reporting the post
        (choices from REASONS).
        description (TextField): Optional description of the report.
        status (CharField): The status of the report
        (either 'Pending' or 'Reviewed').
        created_at (DateTimeField): Timestamp when the report was created.
    """
    # Predefined list of reasons for reporting a post
    REASONS = [
        ('inappropriate', 'Inappropriate Content'),
        ('abuse', 'Abuse or Harassment'),
        ('spam', 'Spam or Misleading'),
        ('hate', 'Hate Speech'),
        ('other', 'Other'),
    ]

    # Foreign key reference to the user who is reporting
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports'  # Reverse relationship from User to Report
    )
    # Foreign key reference to the post being reported
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reports'  # Reverse relationship from Post to Report
    )
    # The reason for the report, constrained to the choices defined in REASONS
    reason = models.CharField(max_length=20, choices=REASONS)

    # Optional description providing more details about the report
    description = models.TextField(blank=True, null=True)

    # report status, either 'Pending' or 'Reviewed' with default as 'Pending'
    status = models.CharField(
        max_length=20,
        default='Pending',
        choices=[('Pending', 'Pending'), ('Reviewed', 'Reviewed')]
    )

    # Timestamp when the report is created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ordering reports by creation date, with the most recent first
        ordering = ['-created_at']

    def __str__(self):
        """
        String representation of the Report model, showing the reporter's
        username and the reported post's title.
        """
        return f"Report by {self.reporter} on Post {self.post}"
