from rest_framework import serializers
from shares.models import Share
from posts.models import Post
from likes.models import Like
from datetime import datetime, timedelta


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model, converting Post instances to and from JSON
    format for API interactions.

    This serializer includes user-related fields, validations, and computed
    fields to enhance API responses with detailed information about posts
    and user interactions.

    Fields:
        - `id`: Primary key of the post.
        - `owner`: Read-only field showing the username of the post owner.
        - `created_at`: Timestamp indicating when the post was created.
        - `updated_at`: Timestamp indicating the last update to the post.
        - `event`: The name of the event associated with the post.
        - `description`: Optional description of the post.
        - `image`: Image associated with the post, with validation for size
        and dimensions.
        - `location`: Location of the event.
        - `date`: Event date, validated to ensure it is not in the past or
        more than 10 years in the future.
        - `time`: Event time, validated to ensure it is not in the past for
        today's date.
        - `is_owner`: Boolean indicating if the authenticated user owns the
        post.
        - `profile_id`: Read-only field for the profile ID of the post owner.
        - `profile_image`: Read-only field for the profile image URL of the
        post owner.
        - `image_filter`: Filter applied to the post's image.
        - `like_id`: ID of the Like object if the authenticated user has liked
        the post; otherwise, None.
        - `likes_count`: Total count of likes on the post.
        - `comments_count`: Total count of comments on the post.
        - `share_count`: Total count of shares of the post.
        - `shared_by`: Username of the user who shared the post, if applicable.
        - `is_shared_by_user`: Boolean indicating if the authenticated user
        has shared the post.

    Methods:
        - `validate_image(value)`: Ensures the image is below 2MB and within
        4096x4096 dimensions.
        - `validate_date(value)`: Ensures the date is valid and within allowed
        bounds (not in the past or more than 10 years in the future).
        - `validate_time(value)`: Ensures the time is not in the past for
        today's date.
        - `get_is_owner(obj)`: Determines if the authenticated user owns the
        post.
        - `get_like_id(obj)`: Retrieves the Like ID for the authenticated user,
        if they liked the post.
        - `get_shared_by(obj)`: Retrieves the username of the user who shared
        the post.
        - `get_is_shared_by_user(obj)`: Checks if the authenticated user has
        shared the post.

    Meta:
        - `model`: The Post model.
        - `fields`: Specifies all included fields for serialization.

    Usage:
        - Serialize Post instances to JSON for API responses.
        - Validate and deserialize JSON data into Post instances for creating
        or updating posts.
    """

    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    profile_id = serializers.ReadOnlyField(source='owner.profile.id')
    profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')
    like_id = serializers.SerializerMethodField()
    date = serializers.DateField(format="%d %b %Y")
    time = serializers.TimeField(format="%H:%M")
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    share_count = serializers.ReadOnlyField()
    shared_by = serializers.SerializerMethodField()
    is_shared_by_user = serializers.SerializerMethodField()

    def validate_image(self, value):
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError('Image size larger than 2MB!')
        if value.image.height > 4096:
            raise serializers.ValidationError(
                'Image height larger than 4096px!'
            )
        if value.image.width > 4096:
            raise serializers.ValidationError(
                'Image width larger than 4096px!'
            )
        return value

    def validate_date(self, value):
        today = datetime.now().date()
        ten_years_from_now = today + timedelta(days=3650)

        if value < today:
            raise serializers.ValidationError(
                "The date cannot be in the past."
            )
        if value > ten_years_from_now:
            raise serializers.ValidationError(
                "The date cannot be more than 10 years in the future."
            )
        return value

    def validate_time(self, value):
        today = datetime.now().date()
        current_time = datetime.now().time()
        # Check if the date is today and the time is in the past
        if (
            self.initial_data.get('date') == str(today) and
            value < current_time
        ):
            raise serializers.ValidationError(
                "The time cannot be in the past for today's date."
            )
        return value

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.owner

    def get_like_id(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            like = Like.objects.filter(
                owner=user, post=obj
            ).first()
            return like.id if like else None
        return None

    def get_shared_by(self, obj):
        # Get the user who shared this post
        share = Share.objects.filter(post=obj).first()
        if share:
            return share.user.username
        return None

    def get_is_shared_by_user(self, obj):
        user = self.context['request'].user
        return Share.objects.filter(user=user, post=obj).exists()

    class Meta:
        model = Post
        fields = [
            'id', 'owner', 'created_at', 'updated_at', 'event',
            'description', 'image', 'location', 'date', 'time', 'is_owner',
            'profile_id', 'profile_image', 'image_filter', 'like_id',
            'likes_count', 'comments_count', 'share_count', 'shared_by',
            'is_shared_by_user'
        ]
