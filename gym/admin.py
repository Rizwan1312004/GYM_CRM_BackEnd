from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, MembershipPlan, Member, Trainer, Payment, Equipment, Service, Branch, Subscription

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Gym Info', {'fields': ('role', 'phone_number')}),
    )

admin.site.register(Service)
admin.site.register(Branch)

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_in_days', 'price', 'status', 'billing_cycle')
    search_fields = ('name',)
    list_filter = ('status', 'billing_cycle')

class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 1

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'city', 'gender')
    list_filter = ('status', 'branches')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    inlines = [SubscriptionInline]

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'salary')
    search_fields = ('user__username', 'specialization')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'payment_date', 'method', 'is_successful')
    list_filter = ('is_successful', 'method', 'payment_date')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'condition', 'last_maintained')
    list_filter = ('condition',)
    search_fields = ('name',)