from rest_framework import serializers
from .models import Comment
from profiles.models import Profile  # Assuming there's a Profile model associated with the user

class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    profile_id = serializers.ReadOnlyField(source='owner.profile.id')  # Assuming a related profile exists
    profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')  # Assuming profile has an image field

    class Meta:
        model = Comment
        fields = [
            'id',
            'owner',
            'is_owner',
            'profile_id',
            'profile_image',
            'post',
            'created_at',
            'updated_at',
            'description',
            'parent',
            'likes_count',
            'dislikes_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'likes_count', 'dislikes_count']

    def get_is_owner(self, obj):
        """
        Check if the logged-in user is the owner of the comment.
        """
        request = self.context.get('request', None)
        return request and request.user == obj.owner if request else False

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)