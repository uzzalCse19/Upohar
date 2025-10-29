from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .views import (
    DonorDashboardView, ReceiverDashboardView, AdminDashboardView,
    AnalyticsDashboardView, SummaryDashboardView, TrendsDashboardView
)
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('api/dashboard/donor/', DonorDashboardView.as_view()),
    path('api/dashboard/receiver/', ReceiverDashboardView.as_view()),
    path('api/dashboard/admin/', AdminDashboardView.as_view()),
    path('api/dashboard/analytics/', AnalyticsDashboardView.as_view()),
    path('api/dashboard/summary/', SummaryDashboardView.as_view()),
    path('api/dashboard/trends/', TrendsDashboardView.as_view()),
]
