from rest_framework import generics, filters as drf_filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import MembershipPlan, Member, Subscription, Service, Attendance, Activity, Trainer, CustomUser
from .serializers import MembershipPlanSerializer, MemberSerializer, SubscriptionSerializer, ServiceSerializer, AttendanceSerializer, ActivitySerializer, TrainerSerializer, RegisterSerializer
from rest_framework import permissions
from .permissions import IsAdminOrReadOnly

class TrainerListAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = Trainer.objects.all()
    serializer_class = TrainerSerializer

class TrainerDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = Trainer.objects.all()
    serializer_class = TrainerSerializer


class ActivityListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = Activity.objects.all().order_by('-date', '-time')
    serializer_class = ActivitySerializer

class ActivityDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

class AttendanceListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        queryset = Attendance.objects.all()
        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        
        if month and year:
            queryset = queryset.filter(date__year=year, date__month=month)
            
        return queryset

class AttendanceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class MembershipPlanListCreate(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = MembershipPlan.objects.all()
    serializer_class = MembershipPlanSerializer

class MemberListAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = MemberSerializer

    def get_queryset(self):
        queryset = Member.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query)
            ).distinct()
        return queryset

class MemberDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    def perform_destroy(self, instance):
        user = instance.user
        if user:
            user.delete()
        else:
            instance.delete()

class MembershipPlanDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = MembershipPlan.objects.all()
    serializer_class = MembershipPlanSerializer

class SubscriptionListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

class SubscriptionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

class ServiceListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ServiceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class DashboardStatsView(APIView):
    def get(self, request):
        total_members = Member.objects.count()
        total_packages = MembershipPlan.objects.count()
        # Count subscriptions instead of active members
        total_subscriptions = Subscription.objects.filter(status='active').count()
        # Count total services available instead of trainers
        total_services = Service.objects.count()

        return Response({
            'total_subscriptions': total_subscriptions,
            'total_services': total_services,
            'total_packages': total_packages,
            'total_members': total_members,
        })

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer