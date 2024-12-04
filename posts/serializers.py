from rest_framework import serializers
from shares.models import Share
from posts.models import Post
from likes.models import Like
from datetime import datetime, timedelta


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.
    Converts Post instances to and from JSON for API interactions,
    with validations and computed fields for user-specific details.
    """

    # Read-only fields for displaying data without modification
    owner = serializers.ReadOnlyField(source='owner.username')
    profile_id = serializers.ReadOnlyField(source='owner.profile.id')
    profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')

    # Computed fields based on user interactions
    is_owner = serializers.SerializerMethodField()
    like_id = serializers.SerializerMethodField()
    shared_by = serializers.SerializerMethodField()
    is_shared_by_user = serializers.SerializerMethodField()

    # Read-only aggregate data fields
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    share_count = serializers.ReadOnlyField()

    # Formatting fields for date and time
    date = serializers.DateField(format="%d %b %Y")
    time = serializers.TimeField(format="%H:%M")

    def validate_image(self, value):
        """
        Validates the uploaded image:
        - Ensures it is less than 2MB.
        - Confirms that height and width are within 4096px.
        """
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
        """
        Validates the date field:
        - Ensures the date is not in the past.
        - Ensures the date is not more than 10 years in the future.
        """
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
        """
        Validates the time field:
        - Ensures the time is not in the past if the date is today.
        """
        today = datetime.now().date()
        current_time = datetime.now().time()
        if (
            self.initial_data.get('date') == str(today) and
            value < current_time
        ):
            raise serializers.ValidationError(
                "The time cannot be in the past for today's date."
            )
        return value

    def get_is_owner(self, obj):
        """
        Checks if the authenticated user is the owner of the post.
        """
        request = self.context['request']
        return request.user == obj.owner

    def get_like_id(self, obj):
        """
        Retrieves the ID of the Like object if the authenticated user
        has liked the post; returns None otherwise.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            like = Like.objects.filter(
                owner=user, post=obj
            ).first()
            return like.id if like else None
        return None

    def get_shared_by(self, obj):
        shares = Share.objects.filter(post=obj)
        shared_users = [share.user.username for share in shares]
        return shared_users if shared_users else []  # Return an empty list instead of None



    def get_is_shared_by_user(self, obj):
        """
        Checks if the authenticated user has shared the post.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return Share.objects.filter(user=user, post=obj).exists()
        return False  # Return False if the user is not authenticated

    class Meta:
        model = Post
        fields = [
            'id', 'owner', 'created_at', 'updated_at', 'event',
            'description', 'image', 'location', 'date', 'time', 'is_owner',
            'profile_id', 'profile_image', 'image_filter', 'like_id',
            'likes_count', 'comments_count', 'share_count', 'shared_by',
            'is_shared_by_user'
        ]
