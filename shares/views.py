from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import Share
from .serializers import ShareSerializer

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


class ShareDetail(generics.RetrieveDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ShareSerializer
    queryset = Share.objects.all()
    
    def delete(self, request, *args, **kwargs):
        share = self.get_object()
        if share.user != request.user:
            raise ValidationError("You are not allowed to delete this share.")
        return super().delete(request, *args, **kwargs)
