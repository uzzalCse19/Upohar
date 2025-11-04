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
    BasicUserSerializer
 
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
from upohars.serializers import UpoharPostSerializer, UpoharRequestSerializer
from .models import User
from .serializers import (
    UserSerializer, BasicUserSerializer, 
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


# upohar/admin_views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from users.models import User
from users.serializers import AdminUserSerializer, BasicUserSerializer
from .serializers import UpoharPostAdminSerializer, UpoharRequestAdminSerializer, UpoharImageSerializer
from upohars.models import UpoharPost, UpoharRequest, UpoharImage
from .permissions import IsAdminUserStrict, IsAdminOrReadOnly
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- User Management ---
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUserStrict]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'email']
    filterset_fields = ['role', 'status']
    ordering_fields = ['date_joined', 'total_donations']

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        user = self.get_object()
        status_val = request.data.get('status')
        if status_val not in dict(User.STATUS_CHOICES).keys():
            return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        user.status = status_val
        user.save()
        return Response(AdminUserSerializer(user).data)

    @action(detail=True, methods=['post'])
    def toggle_staff(self, request, pk=None):
        user = self.get_object()
        user.is_staff = not user.is_staff
        user.save()
        return Response(AdminUserSerializer(user).data)

# --- Post Management ---
class UpoharPostAdminViewSet(viewsets.ModelViewSet):
    queryset = UpoharPost.objects.select_related('donor', 'category').prefetch_related('images').all()
    serializer_class = UpoharPostAdminSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'type', 'category__id']
    search_fields = ['title', 'description', 'donor__email', 'donor__name']
    ordering_fields = ['created_at', 'status']

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        post = self.get_object()
        st = request.data.get('status')
        if st not in dict(UpoharPost.STATUS_CHOICES).keys():
            return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        post.status = st
        post.save()
        return Response(UpoharPostAdminSerializer(post).data)

# --- Images ---
class UpoharImageAdminViewSet(viewsets.ModelViewSet):
    queryset = UpoharImage.objects.select_related('gift').all()
    serializer_class = UpoharImageSerializer
    permission_classes = [IsAdminOrReadOnly]

# --- Request Management ---
class UpoharRequestAdminViewSet(viewsets.ModelViewSet):
    queryset = UpoharRequest.objects.select_related('gift', 'requester').all()
    serializer_class = UpoharRequestAdminSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['requester__email', 'gift__title']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        req = self.get_object()
        if req.status != 'pending':
            return Response({'detail': 'Already handled'}, status=status.HTTP_400_BAD_REQUEST)
        req.status = 'approved'
        req.save()
        # set other pending to rejected
        UpoharRequest.objects.filter(gift=req.gift).exclude(id=req.id).update(status='rejected')
        return Response(UpoharRequestAdminSerializer(req).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        req = self.get_object()
        req.status = 'rejected'
        req.save()
        return Response(UpoharRequestAdminSerializer(req).data)
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count
from django.db.models.functions import TruncMonth
from users.models import User
from upohars.models import UpoharPost, UpoharRequest

class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        dashboard_data = {
            "user_stats": {
                "total_users": User.objects.count(),
                "active_users": User.objects.filter(status='active').count(),
                "suspended_users": User.objects.filter(status='suspended').count(),
                "donors": User.objects.filter(role='donor').count(),
                "receivers": User.objects.filter(role='receiver').count(),
                "exchangers": User.objects.filter(role='exchanger').count(),
            },
            "post_stats": {
                "total_posts": UpoharPost.objects.count(),
                "available_posts": UpoharPost.objects.filter(status='available').count(),
                "requested_posts": UpoharPost.objects.filter(status='requested').count(),
                "completed_posts": UpoharPost.objects.filter(status='completed').count(),
                "donation_posts": UpoharPost.objects.filter(type='donation').count(),
                "exchange_posts": UpoharPost.objects.filter(type='exchange').count(),
            },
            "request_stats": {
                "total_requests": UpoharRequest.objects.count(),
                "pending_requests": UpoharRequest.objects.filter(status='pending').count(),
                "approved_requests": UpoharRequest.objects.filter(status='approved').count(),
                "rejected_requests": UpoharRequest.objects.filter(status='rejected').count(),
            },
            "trends": {
                "posts_by_month": list(
                    UpoharPost.objects.annotate(month=TruncMonth('created_at'))
                    .values('month').annotate(count=Count('id')).order_by('month')
                ),
                "requests_by_status": list(
                    UpoharRequest.objects.values('status')
                    .annotate(count=Count('id')).order_by('status')
                ),
            },
            "recent_activities": {
                "latest_users": list(User.objects.order_by('-date_joined').values('name', 'email', 'role')[:5]),
                "latest_posts": list(UpoharPost.objects.order_by('-created_at').values('title', 'type', 'status')[:5]),
                "latest_requests": list(UpoharRequest.objects.order_by('-created_at')
                                        .values('gift__title', 'requester__email', 'status')[:5]),
            }
        }

        return Response(dashboard_data)


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