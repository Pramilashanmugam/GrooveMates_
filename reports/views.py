from rest_framework import generics, permissions
from .models import Report
from .serializers import ReportSerializer

class ReportCreateView(generics.CreateAPIView):
    """
    View for creating a new report.
    """
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

class ReportListView(generics.ListAPIView):
    """
    View for admins to list all reports.
    """
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Report.objects.all()
