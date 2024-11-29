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
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ShareSerializer
    queryset = Share.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        post = serializer.validated_data['post']

        if Share.objects.filter(user=user, post=post).exists():
            raise ValidationError("You have already shared this post.")

        serializer.save(user=user)

class ShareDetail(generics.RetrieveDestroyAPIView):
    """
    View to retrieve or delete a specific share.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ShareSerializer
    queryset = Share.objects.all()

    def delete(self, request, *args, **kwargs):
        share = self.get_object()
        if share.user != request.user:
            raise ValidationError("You are not allowed to delete this share.")
        return super().delete(request, *args, **kwargs)

class UserSharedPostsView(generics.ListAPIView):
    """
    List posts shared by the authenticated user or by a specific profile.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer

    def get_queryset(self):
        profile_id = self.request.query_params.get("profile_id")
        user = None

        if profile_id:
            user = User.objects.filter(profile__id=profile_id).first()

        if not user:
            user = self.request.user

        if not user.is_authenticated:
            return Post.objects.none()

        return Post.objects.filter(shared_posts__user=user).distinct()
