from django.db import IntegrityError
from rest_framework import serializers
from shares.models import Share
from posts.models import Post

class ShareSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Share
        fields = ['id', 'user', 'post', 'created_at']
    
    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("The specified post does not exist.")
        return value
