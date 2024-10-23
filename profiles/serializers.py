from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    ProfileSerializer serializes the Profile model and provides additional
    fields for user interaction.
    Fields:
    - `owner`: A read-only field that displays the username of the profile
    owner. It's derived from the 'owner.username' attribute of the Profile
    model.
    - `is_owner`: A boolean field that indicates whether the current request
    user
    is the owner of the profile. It is determined using the `get_is_owner`
    method.
    Methods:
    - `get_is_owner`: This method compares the current request user with the
    profile owner and returns `True` if they match, otherwise `False`.
    Meta:
    - `model`: The Profile model.
    - `fields`: Specifies which fields to include in the serialized output.
    These fields include `id`, `owner`, `created_at`, `updated_at`, `name`,
    `description`, `image`, and `is_owner`.
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.owner

    class Meta:
        model = Profile
        fields = [
            'id', 'owner', 'created_at', 'updated_at', 'name',
            'description', 'image', 'is_owner'
        ]
