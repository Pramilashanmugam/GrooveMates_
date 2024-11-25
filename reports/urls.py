from django.urls import path
from reports import views

urlpatterns = [
    path('reports/', views.ReportCreateView.as_view(), name='report-create'),
    path('reports/admin/', views.ReportListView.as_view(), name='report-list'),
]