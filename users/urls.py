from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, DonorDashboardView, ReceiverDashboardView,
    AdminDashboardView, AnalyticsDashboardView, SummaryDashboardView,
    TrendsDashboardView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/donor/', DonorDashboardView.as_view()),
    path('dashboard/receiver/', ReceiverDashboardView.as_view()),
    path('dashboard/admin/', AdminDashboardView.as_view()),
    path('dashboard/analytics/', AnalyticsDashboardView.as_view()),
    path('dashboard/summary/', SummaryDashboardView.as_view()),
    path('dashboard/trends/', TrendsDashboardView.as_view()),
]
