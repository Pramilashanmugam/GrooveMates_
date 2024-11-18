from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework import serializers
from .models import Comment
from profiles.models import Profile


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model, with support for nested replies and
    validation to restrict reply depth.
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    profile_id = serializers.ReadOnlyField(source='owner.profile.id')
    profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        request = self.context.get('request', None)
        return request and request.user == obj.owner if request else False

    def get_created_at(self, obj):
        return naturaltime(obj.created_at)

    def get_updated_at(self, obj):
        return naturaltime(obj.updated_at)

    def get_replies(self, obj):
        """
        Fetch nested replies for a comment, excluding the parent comment itself.
        """
        # Explicitly filter replies to ensure only direct children are included
        replies = obj.replies.filter(parent=obj).order_by('-created_at')
        return CommentSerializer(replies, many=True, context=self.context).data


    def validate(self, data):
        parent = data.get('parent')
        if parent and parent.parent:
            raise serializers.ValidationError({
                'parent': "Replies cannot be more than one level deep."
            })
        if parent and parent == self.instance:  # Prevent self-reference
            raise serializers.ValidationError({
                'parent': "A comment cannot be a reply to itself."
            })
        return data


    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Comment
        fields = [
            'id',
            'owner',
            'is_owner',
            'profile_id',
            'profile_image',
            'post',
            'created_at',
            'updated_at',
            'description',
            'parent',
            'likes_count',
            'dislikes_count',
            'replies',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'likes_count',
            'dislikes_count',
        ]
