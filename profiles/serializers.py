from rest_framework import serializers
from .models import Profile
from followers.models import Follower


class ProfileSerializer(serializers.ModelSerializer):
    """
    ProfileSerializer serializes the Profile model and provides additional
    fields for user interaction.
    Fields:
    - `owner`: A read-only field that displays the username of the profile
      owner. It's derived from the 'owner.username' attribute of the Profile
      model.
    - `is_owner`: A boolean field that indicates whether the current request
      user is the owner of the profile. It is determined using the
      `get_is_owner` method.
    - `following_id`: Shows the ID of the following relationship if the current
      user follows the profile owner; otherwise, it returns `None`.
    Methods:
    - `get_is_owner`: Compares the current request user with the profile owner
      and returns `True` if they match; otherwise, `False`.
    - `get_following_id`: Retrieves the ID of the following relationship if it
      exists; otherwise, returns `None`.
    Meta:
    - `model`: The Profile model.
    - `fields`: Specifies which fields to include in the serialized output.
      These fields include `id`, `owner`, `created_at`, `updated_at`, `name`,
      `description`, `image`, `is_owner`, and `following_id`.
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    following_id = serializers.SerializerMethodField()
    posts_count = serializers.ReadOnlyField()
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.owner

    def get_following_id(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            following = Follower.objects.filter(
                owner=user, followed=obj.owner
            ).first()
            return following.id if following else None
        return None

    class Meta:
        model = Profile
        fields = [
            'id', 'owner', 'created_at', 'updated_at', 'name',
            'description', 'image', 'is_owner', 'following_id',
        ]
