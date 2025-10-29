from django.urls import path, include
from rest_framework.routers import DefaultRouter
from upohars.views import (
    CategoryViewSet, UpoharPostViewSet, UpoharImageViewSet, UpoharRequestViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'upohars', UpoharPostViewSet)
router.register(r'upohars/images', UpoharImageViewSet)
router.register(r'requests', UpoharRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
