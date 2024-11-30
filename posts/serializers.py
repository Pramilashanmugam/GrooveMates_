from rest_framework import serializers
from shares.models import Share
from posts.models import Post
from likes.models import Like
from datetime import datetime, timedelta


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.

    This serializer converts Post instances into JSON format and vice versa,
    making it suitable for API views. It includes fields for user-related
    data and validations to ensure data integrity.

    Fields:
    - `id`: The primary key of the post.
    - `owner`: Read-only field that displays the username of the post owner.
    - `created_at`: Timestamp of when the post was created.
    - `updated_at`: Timestamp of the last update made to the post.
    - `event`: The name of the event associated with the post.
    - `description`: The description of the post, which can be left blank.
    - `image`: The image associated with the post, uploaded to a specified
    path.
    - `location`: The location where the event takes place.
    - `date`: The date of the event, validated to ensure it is not in the past
      or more than 10 years in the future.
    - `time`: The time of the event, validated to ensure it is not in the past
      for today's date.
    - `is_owner`: A boolean field indicating whether the currently
    authenticated user is the owner of the post.
    - `profile_id`: Read-only field showing the ID of the owner's profile.
    - `profile_image`: Read-only field showing the URL of the owner's profile
    image.
    - `like_id`: The ID of the Like object if the authenticated user liked the
      post; otherwise, None.

    Methods:
    - `validate_image`: Validates the image size and dimensions to ensure they
      meet specified criteria (max size of 2MB and max dimensions of
      4096x4096).
    - `validate_date`: Validates the date to ensure it is not in the past or
      more than 10 years in the future.
    - `validate_time`: Validates the time to ensure it is not in the past
      for the current date.
    - `get_is_owner`: Checks if the authenticated user is the owner of the
      post and returns a boolean value.
    - `get_like_id`: Retrieves the ID of the Like object associated with the
      authenticated user if they liked the post; otherwise, returns None.

    Meta:
    - `model`: The Post model.
    - `fields`: Specifies which fields to include in the serialized output.

    Example Usage:
    - Serializing a Post instance will yield a dictionary containing all
      specified fields, ready to be returned in an API response.
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

    class Meta:
        model = Post
        fields = [
            'id', 'owner', 'created_at', 'updated_at', 'event',
            'description', 'image', 'location', 'date', 'time', 'is_owner',
            'profile_id', 'profile_image', 'image_filter', 'like_id',
            'likes_count', 'comments_count', 'share_count','shared_by'
        ]
