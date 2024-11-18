from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsCommentOwner


class CommentList(generics.ListCreateAPIView):
    """
    API view to list all comments or create a new comment.

    - Allows any user to view comments.
    - Authenticated users can create new comments.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Comment.objects.filter(parent=None)  # Top-level comments only
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post']

    def perform_create(self, serializer):
        """
        Automatically set the logged-in user as the owner of the comment.
        """
        serializer.save(owner=self.request.user)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a comment.

    - Any user can retrieve a comment.
    - Only the owner of the comment can update or delete it.
    """
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsCommentOwner
        ]

    def perform_update(self, serializer):
        """
        Save updates to the comment without altering its owner.
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete the comment instance.
        """
        instance.delete()