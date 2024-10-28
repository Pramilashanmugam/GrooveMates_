from rest_framework import serializers
from posts.models import Post
from datetime import datetime, timedelta


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.
    This serializer is responsible for converting Post instances into JSON
    format and vice versa,
    making it suitable for API views. It also includes additional fields for
    user-related data.
    Fields:
    - owner: Read-only field that displays the username of the user who owns
    the post.
    - is_owner: A boolean field that indicates whether the currently
    authenticated user is the owner of the post.
    - profile_id: Read-only field that shows the ID of the owner's profile.
    - profile_image: Read-only field that shows the URL of the owner's profile
    image.
    - id: The primary key of the Post.
    - created_at: The timestamp of when the post was created.
    - updated_at: The timestamp of the last update made to the post.
    - event: The event name (CharField) related to the post.
    - description: The description of the post, which can be left blank.
    - image: The image associated with the post, with a default set if none is
    provided.
    - location: The location where the event takes place.
    - date: The date of the event.
    - time: The time of the event.
    Meta:
    - The model associated with this serializer is the Post model.
    - The `fields` attribute specifies the fields to be serialized and
    deserialized.
    """

    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    profile_id = serializers.ReadOnlyField(source='owner.profile.id')
    profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')
    date = serializers.DateField()
    time = serializers.TimeField()

    def validate_image(self, value):
        if value.size > 1024 * 1024 * 2:
            raise serializers.ValidationError('Image size is larger than 2MB')
        if value.image.width > 4096:
            raise serializers.ValidationError(
                'Image width is larger than 4096px'
                )
        if value.image.height > 4096:
            raise serializers.ValidationError(
                'Image height is larger than 4096px'
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

    class Meta:
        model = Post
        fields = [
            'id', 'owner', 'created_at', 'updated_at', 'event',
            'description', 'image', 'location', 'date', 'time', 'is_owner',
            'profile_id', 'profile_image', 'image_filter'
        ]
