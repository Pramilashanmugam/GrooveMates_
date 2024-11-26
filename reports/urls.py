from django.urls import path
from reports import views

urlpatterns = [
    path('reports/', views.ReportCreateView.as_view(), name='report-create'),
    path('reports/<int:pk>/', views.ReportListView.as_view(), name='report-list'),
]