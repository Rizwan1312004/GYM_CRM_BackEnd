from django.urls import path
from . import views

urlpatterns = [
    path('api/register/', views.RegisterView.as_view(), name='register'),

    # Packages (Membership Plans)
    path('api/packages/', views.MembershipPlanListCreate.as_view(), name='package-list'),
    path('api/packages/<int:pk>/', views.MembershipPlanDetailAPIView.as_view(), name='package-detail'),
    
    # Members
    path('api/members/', views.MemberListAPIView.as_view(), name='member-list'),
    path('api/members/<int:pk>/', views.MemberDetailAPIView.as_view(), name='member-detail'),

    # Trainers
    path('api/trainers/', views.TrainerListAPIView.as_view(), name='trainer-list'),
    path('api/trainers/<int:pk>/', views.TrainerDetailAPIView.as_view(), name='trainer-detail'),

    # Subscriptions
    path('api/subscriptions/', views.SubscriptionListCreateAPIView.as_view(), name='subscription-list'),
    path('api/subscriptions/<int:pk>/', views.SubscriptionDetailAPIView.as_view(), name='subscription-detail'),
    
    # Dashboard
    path('api/dashboard-stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),

    # Services
    path('api/services/', views.ServiceListCreateAPIView.as_view(), name='service-list'),
    path('api/services/<int:pk>/', views.ServiceDetailAPIView.as_view(), name='service-detail'),

    # Attendance
    path('api/attendance/', views.AttendanceListCreateAPIView.as_view(), name='attendance-list'),
    path('api/attendance/<int:pk>/', views.AttendanceDetailAPIView.as_view(), name='attendance-detail'),

    # Activities
    path('api/activities/', views.ActivityListCreateAPIView.as_view(), name='activity-list'),
    path('api/activities/<int:pk>/', views.ActivityDetailAPIView.as_view(), name='activity-detail'),
]