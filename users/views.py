from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from .permissions import IsAdminOrReadOnly, IsDonorOrReceiver
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import (
    BasicUserSerializer, UpoharPostSerializer,
    UpoharRequestSerializer, AnalyticsSummarySerializer
)
from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from upohars.models import UpoharPost, UpoharRequest
from users.models import User
from upohars.models import UpoharPost, UpoharRequest
from django.db.models import Count

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count
from django.db.models.functions import TruncMonth

from .models import User
from .serializers import (
    UserSerializer, BasicUserSerializer, UpoharPostSerializer, UpoharRequestSerializer
)
from .permissions import IsAdminOrReadOnly, IsSelfOrAdmin
from upohars.models import UpoharPost, UpoharRequest


# User CRUD
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'

    # GET /api/users/me/
    def retrieve(self, request, *args, **kwargs):
        if self.kwargs.get('id') == 'me':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return super().retrieve(request, *args, **kwargs)


# Donor Dashboard
class DonorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        posts = UpoharPost.objects.filter(donor=user)
        requests = UpoharRequest.objects.filter(gift__donor=user)
        data = {
            'user': BasicUserSerializer(user).data,
            'donated_gifts': UpoharPostSerializer(posts, many=True).data,
            'requests': UpoharRequestSerializer(requests, many=True).data,
            'total_donated': posts.count(),
            'total_completed': posts.filter(status='completed').count(),
        }
        return Response(data)


# Receiver Dashboard
class ReceiverDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        received = UpoharPost.objects.filter(receiver=user)
        requested = UpoharRequest.objects.filter(requester=user)
        data = {
            'user': BasicUserSerializer(user).data,
            'received_gifts': UpoharPostSerializer(received, many=True).data,
            'requests': UpoharRequestSerializer(requested, many=True).data,
        }
        return Response(data)


# Admin Dashboard
class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        posts = UpoharPost.objects.all()
        requests = UpoharRequest.objects.all()
        data = {
            'users': BasicUserSerializer(users, many=True).data,
            'posts': UpoharPostSerializer(posts, many=True).data,
            'requests': UpoharRequestSerializer(requests, many=True).data,
        }
        return Response(data)


# Analytics Dashboard
class AnalyticsDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        summary = {
            'total_active_users': User.objects.filter(status='active').count(),
            'total_donors': User.objects.filter(role='donor').count(),
            'total_receivers': User.objects.filter(role='receiver').count(),
            'total_exchangers': User.objects.filter(role='exchanger').count(),
            'total_upohar_posts': UpoharPost.objects.count(),
            'total_completed_posts': UpoharPost.objects.filter(status='completed').count(),
            'total_requests': UpoharRequest.objects.count(),
            'total_pending': UpoharRequest.objects.filter(status='pending').count(),
            'total_approved': UpoharRequest.objects.filter(status='approved').count(),
            'total_rejected': UpoharRequest.objects.filter(status='rejected').count(),
        }
        return Response(summary)


# Summary Dashboard (User-specific)
class SummaryDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        total_posts = UpoharPost.objects.filter(donor=user).count()
        completed = UpoharPost.objects.filter(donor=user, status='completed').count()
        pending_requests = UpoharRequest.objects.filter(gift__donor=user, status='pending').count()
        approved_requests = UpoharRequest.objects.filter(gift__donor=user, status='approved').count()
        data = {
            'total_posts': total_posts,
            'completed': completed,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
        }
        return Response(data)


# Trends Dashboard
class TrendsDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts_by_month = (
            UpoharPost.objects
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        requests_by_status = (
            UpoharRequest.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )

        return Response({
            'posts_by_month': list(posts_by_month),
            'requests_by_status': list(requests_by_status),
        })



# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAdminOrReadOnly]
#     lookup_field = 'id'
    
#     # GET /api/users/me/
#     def retrieve(self, request, *args, **kwargs):
#         if self.kwargs.get('id') == 'me':
#             serializer = self.get_serializer(request.user)
#             return Response(serializer.data)
#         return super().retrieve(request, *args, **kwargs)


# # Dashboard ViewSet



# class DonorDashboardView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         user = request.user
#         posts = UpoharPost.objects.filter(donor=user)
#         requests = UpoharRequest.objects.filter(gift__donor=user)
#         data = {
#             'user': BasicUserSerializer(user).data,
#             'donated_gifts': UpoharPostSerializer(posts, many=True).data,
#             'requests': UpoharRequestSerializer(requests, many=True).data,
#             'total_donated': posts.count(),
#             'total_completed': posts.filter(status='completed').count(),
#         }
#         return Response(data)

# class ReceiverDashboardView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         user = request.user
#         received = UpoharPost.objects.filter(receiver=user)
#         requested = UpoharRequest.objects.filter(requester=user)
#         data = {
#             'user': BasicUserSerializer(user).data,
#             'received_gifts': UpoharPostSerializer(received, many=True).data,
#             'requests': UpoharRequestSerializer(requested, many=True).data,
#         }
#         return Response(data)

# class AdminDashboardView(APIView):
#     permission_classes = [IsAdminUser]
#     def get(self, request):
#         users = User.objects.all()
#         posts = UpoharPost.objects.all()
#         requests = UpoharRequest.objects.all()
#         data = {
#             'users': BasicUserSerializer(users, many=True).data,
#             'posts': UpoharPostSerializer(posts, many=True).data,
#             'requests': UpoharRequestSerializer(requests, many=True).data,
#         }
#         return Response(data)

# class AnalyticsDashboardView(APIView):
#     permission_classes = [IsAdminUser]
#     def get(self, request):
#         summary = {
#             'total_active_users': User.objects.filter(status='active').count(),
#             'total_donors': User.objects.filter(role__in=['donor','both']).count(),
#             'total_receivers': User.objects.filter(role__in=['receiver','both']).count(),
#             'total_upohar_posts': UpoharPost.objects.count(),
#             'total_completed_posts': UpoharPost.objects.filter(status='completed').count(),
#             'total_requests': UpoharRequest.objects.count(),
#             'total_pending': UpoharRequest.objects.filter(status='pending').count(),
#             'total_approved': UpoharRequest.objects.filter(status='approved').count(),
#             'total_rejected': UpoharRequest.objects.filter(status='rejected').count(),
#         }
#         return Response(summary)

# class SummaryDashboardView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         user = request.user
#         total_posts = UpoharPost.objects.filter(donor=user).count()
#         completed = UpoharPost.objects.filter(donor=user, status='completed').count()
#         pending_requests = UpoharRequest.objects.filter(gift__donor=user, status='pending').count()
#         approved_requests = UpoharRequest.objects.filter(gift__donor=user, status='approved').count()
#         data = {
#             'total_posts': total_posts,
#             'completed': completed,
#             'pending_requests': pending_requests,
#             'approved_requests': approved_requests
#         }
#         return Response(data)





# class TrendsDashboardView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Use TruncMonth (works on SQLite & PostgreSQL)
#         posts_by_month = (
#             UpoharPost.objects
#             .annotate(month=TruncMonth('created_at'))
#             .values('month')
#             .annotate(count=Count('id'))
#             .order_by('month')
#         )

#         requests_by_status = (
#             UpoharRequest.objects
#             .values('status')
#             .annotate(count=Count('id'))
#             .order_by('status')
#         )

#         return Response({
#             'posts_by_month': list(posts_by_month),
#             'requests_by_status': list(requests_by_status),
#         })


# class TrendsDashboardView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         posts_by_month = (
#             UpoharPost.objects
#             .extra({'month': "date_trunc('month', created_at)"})
#             .values('month')
#             .annotate(count=Count('id'))
#             .order_by('month')
#         )
#         requests_by_status = (
#             UpoharRequest.objects
#             .values('status')
#             .annotate(count=Count('id'))
#             .order_by('status')
#         )
#         return Response({
#             'posts_by_month': list(posts_by_month),
#             'requests_by_status': list(requests_by_status),
#         })