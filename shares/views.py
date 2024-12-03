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
    List posts shared by the authenticated user or by a specific profile.

    Methods:
        - `GET`: Retrieves a list of posts shared by the authenticated user or
                 by a specific profile ID (if provided in query params).

    Query Parameters:
        - `profile_id` (optional): Filters shared posts by the specified
                                   profile's ID.

    Permissions:
        - Authenticated users can view shared posts.

    Returns:
        A queryset of posts shared by the specified profile or the
        authenticated user.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer

    def get_queryset(self):
        """
        Filter posts based on the authenticated user or a specific profile ID.

        If a profile ID is provided in the query parameters, retrieves posts
        shared by the user associated with that profile. Otherwise, retrieves
        posts shared by the authenticated user.

        Returns:
            QuerySet: A queryset of shared posts.

        Raises:
            None: Returns an empty queryset if the user is unauthenticated.
        """
        profile_id = self.request.query_params.get("profile_id")
        user = None

        if profile_id:
            # Attempt to retrieve the user associated with the given profile ID
            user = User.objects.filter(profile__id=profile_id).first()

        if not user:
            # Default to the logged-in user if no profile ID is provided
            user = self.request.user

        if not user.is_authenticated:
            # Return an empty queryset for unauthenticated users
            return Post.objects.none()

        # Retrieve and return posts shared by the specified user
        return Post.objects.filter(shared_posts__user=user).distinct()
