from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for the Report model.
    """
    reporter = serializers.ReadOnlyField(source='reporter.username')

    class Meta:
        model = Report
        fields = ['id', 'reporter', 'post', 'comment', 'reason', 'description', 'status', 'created_at']
        read_only_fields = ['id', 'reporter', 'status', 'created_at']

    def validate(self, data):
        if not data.get('post') and not data.get('comment'):
            raise serializers.ValidationError("A report must be associated with either a post or a comment.")
        return data
