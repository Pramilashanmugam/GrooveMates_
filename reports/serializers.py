from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for the Report model to handle serialization and validation.
    This serializer handles the conversion of Report model instances
    to JSON format and vice versa, and includes necessary validation logic
    for creating and updating reports. The 'reporter' field is automatically
    populated with the username of the user who created the report.
    """

    # retrieve the 'username' of the user who submitted the report.
    reporter = serializers.ReadOnlyField(source='reporter.username')

    class Meta:
        model = Report
        # Define the fields that will be serialized/deserialized.
        fields = [
            'id',
            'reporter',
            'post',
            'reason',
            'description',
            'status',
            'created_at'
             ]
        read_only_fields = ['created_at']

    def validate_reason(self, value):
        """
        Custom validation for the 'reason' field to ensure a valid reason
        is provided.
        This function can be used to enforce any additional logic or
        restrictions on the 'reason' field (e.g., ensuring the reason is
        from a predefined list).
        """
        valid_reasons = ['inappropriate', 'abuse', 'spam', 'hate', 'other']
        if value not in valid_reasons:
            raise serializers.ValidationError(
                f"Invalid reason. Valid options are: "
                f"{', '.join(valid_reasons)}."
            )
        return value

    def validate(self, data):
        """
        Custom validation for the entire report creation process.
        You can add additional checks here, such as ensuring that a report
        is not created more than once for the same post by the same user.
        """
        # Example: prevent multiple reports for the same post by the same user
        if Report.objects.filter(
            reporter=self.context['request'].user,
            post=data['post']
        ).exists():
            raise serializers.ValidationError(
                "You have already reported this post."
            )
        return data
