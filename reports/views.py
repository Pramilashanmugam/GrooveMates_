from rest_framework import generics
from .models import Report
from .serializers import ReportSerializer
from drf_api.permissions import IsAdminOrCreateOnly

class ReportCreateView(generics.ListCreateAPIView):
    """
    View for creating a new report and listing reports.
    """
    serializer_class = ReportSerializer
    permission_classes = [IsAdminOrCreateOnly]
    queryset = Report.objects.all()

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

class ReportListView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, or deleting a specific report.
    """
    serializer_class = ReportSerializer
    permission_classes = [IsAdminOrCreateOnly]

    def get_queryset(self):
        return Report.objects.all()
