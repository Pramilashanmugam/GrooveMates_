from rest_framework import generics, permissions
from .models import Report
from .serializers import ReportSerializer
from drf_api.permissions import IsOwnerOrReadOnly  # Assuming you have this permission

class ReportList(generics.ListCreateAPIView):
    """
    List all reports or create a new report if logged in.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportSerializer
    queryset = Report.objects.all()

    def perform_create(self, serializer):
        """
        Sets the reporter to the logged-in user before saving.
        """
        serializer.save(reporter=self.request.user)


class ReportDetail(generics.RetrieveUpdateAPIView):
    """
    Retrieve a specific report by ID or update it (e.g., change status) if admin.
    """
    permission_classes = [permissions.IsAdminUser]  # Admin-only view for reviewing reports
    serializer_class = ReportSerializer
    queryset = Report.objects.all()

