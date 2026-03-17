
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

# 1. Custom User Model for Role-Based Access
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('trainer', 'Trainer'),
        ('member', 'Member'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

# 2. Add Service and Branch Models for Frontend Select Options
class Service(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Branch(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# 3. Membership Plans (Packages)
class MembershipPlan(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )
    BILLING_CYCLE_CHOICES = (
        ('Annually', 'Annually'),
        ('Monthly', 'Monthly'),
        ('Weekly', 'Weekly'),
    )
    name = models.CharField(max_length=100, help_text="e.g., Package11, Premium")
    duration_in_days = models.PositiveIntegerField(default=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='Monthly')
    services = models.ManyToManyField(Service, blank=True)

    def __str__(self):
        return f"{self.name} - ₹{self.price}"

# 4. Gym Members
class Member(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'member'})
    assigned_trainer = models.ForeignKey('Trainer', on_delete=models.SET_NULL, null=True, blank=True, related_name='trainees')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Profile Details Mapping to Frontend
    admission_no = models.CharField(max_length=50, blank=True, null=True, unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    id_proof = models.ImageField(upload_to='id_proofs/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    blood_group = models.CharField(max_length=5, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    subscribe_newsletter = models.BooleanField(default=False)
    
    branches = models.ManyToManyField(Branch, blank=True)

    def __str__(self):
        return self.user.get_full_name()

# 5. Member Subscriptions (replaces Member.plan mapping)
class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(default=timezone.localdate)
    valid_until = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def save(self, *args, **kwargs):
        if self.plan and not self.valid_until:
            self.valid_until = self.start_date + timedelta(days=self.plan.duration_in_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.user.username} - {self.plan.name if self.plan else 'No Plan'}"

# 6. Trainers
class Trainer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'trainer'})
    specialization = models.CharField(max_length=100, help_text="e.g., Weightlifting, Cardio, Crossfit")
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    hire_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Trainer: {self.user.get_full_name()}"

# 7. Payment and Billing
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    is_successful = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.member.user.username} - ₹{self.amount} on {self.payment_date.strftime('%Y-%m-%d')}"

# 8. Equipment Inventory Management
class Equipment(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    purchase_date = models.DateField()
    last_maintained = models.DateField(null=True, blank=True)
    condition = models.CharField(max_length=50, choices=[('good', 'Good'), ('needs_repair', 'Needs Repair'), ('out_of_service', 'Out of Service')], default='good')

    def __str__(self):
        return self.name

# 9. Attendance Tracking
class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')

    class Meta:
        unique_together = ('member', 'date')

    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.date} - {self.status}"

# 10. Gym Activities (Classes, Workouts, etc.)
class Activity(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    duration_minutes = models.PositiveIntegerField(default=60)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    capacity = models.PositiveIntegerField(default=20)
    
    def __str__(self):
        return f"{self.name} on {self.date}"