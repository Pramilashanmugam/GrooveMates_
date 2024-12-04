from django.db import IntegrityError
from rest_framework import serializers
from shares.models import Share
from posts.models import Post
from posts.serializers import PostSerializer


class ShareSerializer(serializers.ModelSerializer):
    """
    Serializer for the Share model.

    Provides serialization and validation logic for Share objects.
    Ensures that the `post` being shared exists and that the `user` field
    is read-only.
    Fields:
        - `id`: The unique identifier of the share.
        - `user`: The username of the user who shared the post (read-only).
        - `post`: The post being shared.
        - `created_at`: The timestamp when the share was created.
    """
    # Ensures the user field is read-only
    user = serializers.ReadOnlyField(source='user.username')
    post = PostSerializer(read_only=True)  # Use nested PostSerializer to show post details


    class Meta:
        model = Share
        # Specify the fields to include in the serialized output
        fields = ['id', 'user', 'post', 'created_at']

    def validate_post(self, value):
        """
        Custom validation for the `post` field.

        Ensures the post being shared exists in the database.

        Args:
            value (Post): The post instance to validate.

        Returns:
            Post: The validated post instance.

        Raises:
            serializers.ValidationError: If the specified post does not exist.
        """
        # Check if the post exists in the database
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(
                "The specified post does not exist."
                )

        return value  # Return the validated post instance
