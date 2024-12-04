from django.db.models import Count
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_api.permissions import IsOwnerOrReadOnly
from .models import Post
from .serializers import PostSerializer


class PostList(generics.ListCreateAPIView):
    """
    API view to list all posts or create a new post.
    - List all posts, with filtering, searching, and ordering options.
    - Authenticated users can create posts.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comment', distinct=True),
        share_count=Count('share_posts', distinct=True)
    ).order_by('-created_at')
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = [
        # Filter posts by followers of the owner
        'owner__followed__owner__profile',
        'likes__owner__profile',  # Filter posts by users who liked them
        'owner__profile',  # Filter posts by the owner's profile
    ]
    search_fields = [
        'owner__username',  # Search by the username of the owner
        'event',  # Search by the event field in the post
        'date',  # Search by the date field in the post
    ]
    ordering_fields = [
        'likes_count',  # Order by the number of likes
        'comments_count',  # Order by the number of comments
        'share_count',  # Order by the number of shares
        'likes__created_at',  # Order by the creation date of likes
    ]

    def perform_create(self, serializer):
        """
        Override perform_create to associate the post with the logged-in user.
        """
        serializer.save(owner=self.request.user)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single post.
    - Only the owner of the post can edit or delete it.
    """
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Post.objects.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comment', distinct=True),
        share_count=Count('share_posts', distinct=True)
    ).order_by('-created_at')
