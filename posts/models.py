from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Post(models.Model):
    """
    Post model representing an event created by a user.

    Attributes:
        owner (ForeignKey): The user who created the post.
        created_at (DateTimeField): Timestamp when the post was created.
        updated_at (DateTimeField): Timestamp when the post was last updated.
        event (CharField): Name of the event (max length: 255).
        description (TextField): Optional description of the event
        (can be blank).
        location (CharField): Location of the event (max length: 255).
        date (DateField): Date of the event, defaults to the current date.
        time (TimeField): Time of the event, defaults to the current time.
        image (ImageField): Optional image for the event. Uploaded to
                            'images/' by default, with a fallback to a
                            default image ('../default_post_xxhr8e').
        image_filter (CharField): Filter applied to the event image. Users
                                  can choose from predefined filters like
                                  'Hudson', 'Lo-Fi', etc. Default is 'Normal'.
        share_posts (ManyToManyField): Represents users who have shared the
                                       post,linked through the `Share` model.

    Meta:
        - Posts are ordered by creation time in descending order
        (`-created_at`).

    Methods:
        __str__: Returns a string representation of the post, displaying its
                 ID and event name.
    """

    image_filter_choices = [
        ('_1977', '1977'), ('brannan', 'Brannan'),
        ('earlybird', 'Earlybird'), ('hudson', 'Hudson'),
        ('inkwell', 'Inkwell'), ('lofi', 'Lo-Fi'),
        ('kelvin', 'Kelvin'), ('normal', 'Normal'),
        ('nashville', 'Nashville'), ('rise', 'Rise'),
        ('toaster', 'Toaster'), ('valencia', 'Valencia'),
        ('walden', 'Walden'), ('xpro2', 'X-pro II')
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now, blank=True)
    time = models.TimeField(default=timezone.now, blank=True)
    image = models.ImageField(
        upload_to='images/', default='../default_post_xxhr8e', blank=True
    )
    image_filter = models.CharField(
        max_length=32, choices=image_filter_choices, default='normal'
    )
    share_posts = models.ManyToManyField(
        User, through='shares.Share', related_name='post_share'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.id} {self.event}'
