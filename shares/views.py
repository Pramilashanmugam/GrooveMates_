from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from posts.models import Post
from posts.serializers import PostSerializer
from shares.models import Share
from shares.serializers import ShareSerializer
from django.contrib.auth.models import User


class ShareList(generics.ListCreateAPIView):
    """
    View to list all shares or create a new share.

    Methods:
        - `GET`: Returns a list of all shares.
        - `POST`: Creates a new share for the logged-in user.
          Prevents duplicate shares for the same post by the same user.

    Permissions:
        - Read-only access for unauthenticated users.
        - Authenticated users can create new shares.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ShareSerializer
    queryset = Share.objects.all()

    def perform_create(self, serializer):
        """
        Validate and save the new share instance.

        Ensures that the same user does not share the same post more than once.

        Args:
            serializer (ShareSerializer): The serializer instance containing
                                          the validated data.

        Raises:
            ValidationError: If the user has already shared the specified post.
        """
        user = self.request.user
        post = serializer.validated_data['post']

        # Check if the share already exists for this user and post
        if Share.objects.filter(user=user, post=post).exists():
            raise ValidationError("You have already shared this post.")

        # Save the share instance with the logged-in user
        serializer.save(user=user)


class ShareDetail(generics.RetrieveDestroyAPIView):
    """
    View to retrieve or delete a specific share.

    Methods:
        - `GET`: Retrieves the details of a specific share by its ID.
        - `DELETE`: Deletes the share if it belongs to the authenticated user.

    Permissions:
        - Authenticated users can retrieve or delete their shares.
        - Prevents unauthorized deletion attempts.

    Raises:
        ValidationError: If a user attempts to delete a share they do not own.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ShareSerializer
    queryset = Share.objects.all()

    def delete(self, request, *args, **kwargs):
        """
        Override the delete method to enforce ownership.

        Ensures that a user can only delete shares they own.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A confirmation response on successful deletion.

        Raises:
            ValidationError: If the user is not the owner of the share.
        """
        share = self.get_object()

        # Check if the share belongs to the logged-in user
        if share.user != request.user:
            raise ValidationError("You are not allowed to delete this share.")

        # Proceed with deletion
        return super().delete(request, *args, **kwargs)


class UserSharedPostsView(generics.ListAPIView):
    """
    Lists posts shared by the logged-in user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        """
        Retrieves posts shared by the logged-in user.
        """
        user = self.request.user

        # Get all shares by the logged-in user
        shared_posts = Share.objects.filter(user=user)

        # Extract related post IDs from the Share model
        post_ids = shared_posts.values_list('post_id', flat=True)

        # Return Post queryset filtered by the post IDs
        return Post.objects.filter(id__in=post_ids)





