from rest_framework import generics, permissions
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsCommentOwner  # Import your custom permission

class CommentList(generics.ListCreateAPIView):
    """
    List all comments or create a new comment if the user is authenticated.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        """
        Set the owner of the comment to the logged-in user before saving.
        """
        serializer.save(owner=self.request.user)

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve a comment by ID, or update or delete it if the user is the owner.
    """
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentOwner]  # Apply permissions here

    def perform_update(self, serializer):
        """
        Allow updating of a comment while keeping the owner unchanged.
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Perform the delete action on the comment instance.
        """
        instance.delete()
