from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from posts.models import Post
from posts.serializers import PostSerializer
from shares.models import Share
from shares.serializers import ShareSerializer
from drf_api.permissions import IsOwnerOrReadOnly

class ShareList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ShareSerializer
    queryset = Share.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        post = serializer.validated_data['post']
        
        if Share.objects.filter(user=user, post=post).exists():
            raise ValidationError("You have already shared this post.")
        
        serializer.save(user=user)

        # Increment the share_count for the post
        post.share_count += 1
        post.save()

        return share

class ShareDetail(generics.RetrieveDestroyAPIView):
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
    List all posts shared by a specific user.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Post.objects.none()
        return Post.objects.filter(share_posts__user=user).distinct()
