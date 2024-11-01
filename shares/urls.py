from django.urls import path
from shares import views

urlpatterns = [
    path('shares/', views.ShareList.as_view(), name='share-list'),
    path('shares/<int:pk>/', views.ShareDetail.as_view(), name='share-detail'),
]
