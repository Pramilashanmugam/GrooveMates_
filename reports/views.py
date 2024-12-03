from rest_framework import generics
from .models import Report
from .serializers import ReportSerializer
from drf_api.permissions import IsAdminOrCreateOnly


class ReportCreateView(generics.ListCreateAPIView):
    """
    View for creating a new report and listing all reports.

    This view provides the functionality to both list all reports and create a
    new report.
    The `perform_create` method ensures that the current user is set as the
    reporter when creating a report.

    Attributes:
        - `serializer_class`: The serializer used for converting the Report
        model to/from JSON.
        - `permission_classes`: Defines permissions required for the view.
        Only allows creation by authenticated users or admins.
        - `queryset`: Defines the base queryset to retrieve reports for
        listing.

    Methods:
        - `perform_create`: Overridden to automatically set the `reporter`
        field to the current authenticated user when a new report is created.
    """
    serializer_class = ReportSerializer
    # Custom permission class to control access
    permission_classes = [IsAdminOrCreateOnly]
    # Defines the base queryset for the list view
    queryset = Report.objects.all()

    def perform_create(self, serializer):
        """
        Override perform_create to set the current user as the reporter.

        This ensures that the `reporter` field in the Report model is
        automatically populated with the user making the request
        (authenticated user).
        """
        serializer.save(reporter=self.request.user)


class ReportListView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, or deleting a specific report.

    This view allows actions like retrieving a single report, updating it,
    or deleting it.
    Only users with the correct permissions (admin or specific user) can
    perform update or delete actions.

    Attributes:
        - `serializer_class`: The serializer used for converting the Report
        model to/from JSON.
        - `permission_classes`: Defines permissions required for the view.
        Admins and the creator of the report can modify it.

    Methods:
        - `get_queryset`: Returns all reports for listing, can be overridden
        to filter specific reports if needed.
    """
    serializer_class = ReportSerializer
    # Custom permission class to control access
    permission_classes = [IsAdminOrCreateOnly]

    def get_queryset(self):
        """
        Retrieve the queryset of reports.

        Returns:
            queryset: A queryset of all reports. This method could be extended
            to filter reports based on specific criteria
            (e.g., current user, status, etc.).
        """
        return Report.objects.all()
