from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions
from .models import Category, UpoharPost, UpoharImage, UpoharRequest
from .serializers import (
    CategorySerializer, UpoharPostSerializer, UpoharImageSerializer, UpoharRequestSerializer
)
from .filters import UpoharPostFilter
from .paginations import StandardResultsSetPagination
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from .models import UpoharRequest, UpoharPost
from .serializers import UpoharRequestSerializer

from rest_framework import viewsets, permissions
from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


from rest_framework.exceptions import PermissionDenied
class UpoharPostViewSet(viewsets.ModelViewSet):
    queryset = UpoharPost.objects.all()
    serializer_class = UpoharPostSerializer
    filterset_class = UpoharPostFilter
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'status']
    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ['donor', 'exchanger']:
           raise PermissionDenied("Only donors or exchangers can create Upohar posts.")
      
        serializer.save(donor=user)
        



class UpoharImageViewSet(viewsets.ModelViewSet):
    queryset = UpoharImage.objects.all()
    serializer_class = UpoharImageSerializer
    permission_classes = [permissions.IsAuthenticated]

class UpoharRequestViewSet(viewsets.ModelViewSet):
    """
    Handle all Upohar Request operations:
    - Donor can view requests for their gifts
    - Requester can create new requests
    - Donor can approve/reject requests
    - Donor or requester can mark a request as complete
    """
    queryset = UpoharRequest.objects.all()
    serializer_class = UpoharRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    # 🔹 Filter requests depending on the user role
    def get_queryset(self):
        user = self.request.user

        # Handle anonymous user safely
        if not user.is_authenticated:
            return UpoharRequest.objects.none()

        # Donor or Both → show requests for gifts they posted
        if getattr(user, 'role', None) in ['donor', 'both']:
            return UpoharRequest.objects.filter(gift__donor=user)

        # Requester → show only their own requests
        return UpoharRequest.objects.filter(requester=user)

    # 🔹 Prevent donor from requesting their own gift
    def perform_create(self, serializer):
        gift = serializer.validated_data.get('gift')
        user = self.request.user
        if gift.donor == user:
            raise PermissionDenied("You cannot request your own gift.")
        serializer.save(requester=user)

    # 🔹 List requests created by the logged-in requester
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        queryset = UpoharRequest.objects.filter(requester=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 🔹 List pending requests for donor's gifts
    @action(detail=False, methods=['get'])
    def pending(self, request):
        queryset = UpoharRequest.objects.filter(gift__donor=request.user, status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 🔹 Donor approves a request
    @action(detail=True, methods=['post'], url_path='approve')
    def approve_request(self, request, pk=None):
        upohar_request = self.get_object()
        gift = upohar_request.gift

        # কেবল সেই donor approve করতে পারবে যে gift এর মালিক
        if gift.donor != request.user:
            raise PermissionDenied("You are not allowed to approve this request.")

        # আগে অন্য কোনো request approved আছে কি না চেক
        if UpoharRequest.objects.filter(gift=gift, status='approved').exists():
            return Response({"detail": "This gift has already been approved for another requester."},
                            status=status.HTTP_400_BAD_REQUEST)

        # এখন এই request approve করো
        upohar_request.status = 'approved'
        upohar_request.save()

        # অন্য সব pending request 'rejected' করে দাও
        UpoharRequest.objects.filter(gift=gift).exclude(id=upohar_request.id).update(status='rejected')

        return Response({"detail": "Request approved successfully."}, status=status.HTTP_200_OK)

    # 🔹 Donor rejects a request
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        req = self.get_object()
        if req.gift.donor != request.user:
            return Response({'detail': 'Only donor can reject this request.'}, status=status.HTTP_403_FORBIDDEN)
        req.status = 'rejected'
        req.save()
        return Response({'detail': 'Request rejected successfully.'})

    # 🔹 Donor or requester marks request as complete
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        req = self.get_object()
        if req.gift.donor != request.user and req.requester != request.user:
            return Response({'detail': 'Only donor or requester can mark as complete.'}, status=status.HTTP_403_FORBIDDEN)
        req.status = 'completed'
        req.save()
        return Response({'detail': 'Request marked as completed.'})


# class UpoharRequestViewSet(viewsets.ModelViewSet):
#     queryset = UpoharRequest.objects.all()  # 🔹 needed for router
#     serializer_class = UpoharRequestSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [filters.OrderingFilter]
#     ordering_fields = ['created_at']

#     def get_queryset(self):
#         user = self.request.user
#         if user.role in ['donor', 'both']:
#             return UpoharRequest.objects.filter(gift__donor=user)
#         return UpoharRequest.objects.none()

#     def perform_create(self, serializer):
#         gift = serializer.validated_data.get('gift')
#         user = self.request.user
#         if gift.donor == user:
#             raise PermissionDenied("You cannot request your own gift.")
#         serializer.save(requester=user)