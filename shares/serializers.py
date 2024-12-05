from django.db import IntegrityError
from rest_framework import serializers
from shares.models import Share
from posts.models import Post
from posts.serializers import PostSerializer


class ShareSerializer(serializers.ModelSerializer):
    """
    Serializer for the Share model.

    This serializer provides the logic for serializing and validating `Share`
    objects. It ensures that the `user` field is read-only and that the
    `post` being shared exists in the database.

    Fields:
        - `id`: The unique identifier of the share.
        - `user`: The username of the user who shared the post (read-only).
        - `post`: The post being shared (must exist in the database).
        - `created_at`: The timestamp when the share was created.
    """
    # Read-only field for the user's username
    user = serializers.ReadOnlyField(source='user.username')
    # Ensure the post exists
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Share
        fields = ['id', 'user', 'post', 'created_at']

    def validate_post(self, value):
        """
        Custom validation for the `post` field.

        Ensures the `post` being shared exists in the database.

        Args:
            value (Post): The post instance to validate.

        Returns:
            Post: The validated post instance if it exists.

        Raises:
            serializers.ValidationError: If the specified post does not exist.
        """
        # Check if the post exists in the database
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(
                "The specified post does not exist."
            )

        return value  # Return the validated post instance
