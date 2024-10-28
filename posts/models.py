from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Post(models.Model):
    """
    Post model represents an event created by a user ('owner').
    Attributes:
    - owner: A ForeignKey linking to the User model. Indicates the user who
    created the post.
    - created_at: A DateTimeField automatically storing the date and time the
    post was created.
    - updated_at: A DateTimeField automatically updating the date and time when
    the post is edited.
    - event: A CharField for the name of the event, with a maximum length of
    255 characters.
    - description: An optional TextField for the event's description. Can be
    left blank.
    - location: A CharField representing the event's location, with a maximum
    length of 255 characters.
    - date: A DateField storing the event's date, defaulting to the current
    date if not provided.
    - time: A TimeField storing the event's time, defaulting to the current
    time if not provided.
    - image: An optional ImageField for the event's image, uploaded to the
    'images/' directory by default.
              If no image is provided, a default image
              ('../default_post_xxhr8e') is used.
    image_filter:
    A CharField representing the type of filter to be applied to the post's
    image. The filter choices include a variety of predefined filters,
    allowing users to select from popular image styles. The default filter
    is 'Normal'.
    Example usage:
    - A user may choose a filter like 'Hudson' to give their image a distinct
    visual effect.
    Meta:
    - The posts are ordered in descending order of their creation time
    (`-created_at`).
    Methods:
    - __str__: Returns a string representation of the post, displaying its
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

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.id} {self.event}'


