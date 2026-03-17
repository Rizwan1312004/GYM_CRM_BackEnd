from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import MembershipPlan, Service, Branch, Subscription, Member, Attendance, Activity, Trainer, CustomUser
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
from rest_framework import viewsets
from .models import MembershipPlan, Member

class TrainerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Trainer
        fields = ['id', 'user', 'name', 'specialization']
        
class ActivitySerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source='trainer.user.get_full_name', read_only=True)

    class Meta:
        model = Activity
        fields = ['id', 'name', 'description', 'date', 'time', 'duration_minutes', 'trainer', 'trainer_name', 'capacity']
    
class AttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'member', 'member_name', 'date', 'status']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name']

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name']

class MembershipPlanSerializer(serializers.ModelSerializer):
    # Retrieve nested services
    services_details = ServiceSerializer(source='services', many=True, read_only=True)
    
    # Aliases for frontend
    amount = serializers.DecimalField(source='price', max_digits=10, decimal_places=2, required=False)
    billingCycle = serializers.ChoiceField(source='billing_cycle', choices=MembershipPlan.BILLING_CYCLE_CHOICES, required=False)
    
    # We will receive services from frontend as list of dicts: [{'value': 'boxing', 'label': 'Boxing'}]
    services = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = MembershipPlan
        fields = ['id', 'name', 'duration_in_days', 'price', 'amount', 'description', 'status', 'billing_cycle', 'billingCycle', 'services', 'services_details']
        extra_kwargs = {
            'price': {'required': False},
            'billing_cycle': {'required': False}
        }
        
    def _handle_services(self, instance, services_data):
        if services_data is not None:
            instance.services.clear()
            for service_dict in services_data:
                label = service_dict.get('label')
                if label:
                    service_obj, _ = Service.objects.get_or_create(name=label)
                    instance.services.add(service_obj)

    def create(self, validated_data):
        services_data = validated_data.pop('services', None)
        plan = super().create(validated_data)
        self._handle_services(plan, services_data)
        return plan

    def update(self, instance, validated_data):
        services_data = validated_data.pop('services', None)
        plan = super().update(instance, validated_data)
        if services_data is not None:
             self._handle_services(plan, services_data)
        return plan

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = MembershipPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(queryset=MembershipPlan.objects.all(), source='plan', write_only=True, required=False, allow_null=True)
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    package_name = serializers.CharField(source='plan.name', read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'member', 'member_name', 'plan', 'plan_id', 'package_name', 'start_date', 'valid_until', 'status']

    def create(self, validated_data):
        plan = validated_data.pop('plan', None)
        subscription = Subscription.objects.create(plan=plan, **validated_data)
        return subscription

class MemberSerializer(serializers.ModelSerializer):
    # Flatten User basic info for easier access / write
    name = serializers.CharField(source='user.first_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    
    # Frontend aliases
    subscribeNewsletter = serializers.BooleanField(source='subscribe_newsletter', required=False)
    contactNumber = serializers.CharField(source='user.phone_number', required=False)
    bloodGroup = serializers.CharField(source='blood_group', required=False)
    dateOfBirth = serializers.DateField(source='date_of_birth', required=False, allow_null=True)
    idProof = serializers.ImageField(source='id_proof', required=False, allow_null=True)
    admissionNo = serializers.CharField(source='admission_no', required=False, allow_null=True, allow_blank=True)
    
    # Nested relationships
    branches = BranchSerializer(many=True, read_only=True)
    subscriptions = SubscriptionSerializer(many=True, read_only=True)

    class Meta:
        model = Member
        fields = [
            'id', 'admission_no', 'admissionNo', 'name', 'email', 'avatar', 'id_proof', 'idProof', 'date_of_birth', 'dateOfBirth', 'status', 'blood_group', 'bloodGroup',
            'emergency_contact', 'address', 'city', 'state', 'gender', 
            'subscribe_newsletter', 'subscribeNewsletter', 
            'contactNumber', 'branches', 'subscriptions'
        ]

    def _update_user_fields(self, user, validated_data):
        user_data = validated_data.pop('user', {})
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
            # If username is empty, set it
            if not user.username:
                 user.username = user_data.get('email', user_data['first_name'].lower().replace(' ', '') + '_test')
        if 'email' in user_data:
            user.email = user_data['email']
            if not user.username:
                 user.username = user_data['email']
        if 'phone_number' in user_data:
            user.phone_number = user_data['phone_number']
        
        user.save()

    def create(self, validated_data):
        from .models import CustomUser
        
        user_data = validated_data.pop('user', {})
        
        # Determine username
        username = user_data.get('first_name', '').lower().replace(' ', '')
        if not username:
             username = user_data.get('email', 'new_member').split('@')[0]
        
        # Ensure unique username
        base_username = username
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
             username = f"{base_username}{counter}"
             counter += 1

        # Create the user object
        user = CustomUser(
            username=username,
            role='member',
            first_name=user_data.get('first_name', ''),
            email=user_data.get('email', ''),
            phone_number=user_data.get('phone_number', '')
        )
        
        # FIX: Set an unusable password so the account is secure until the user sets one
        user.set_unusable_password()
        user.save()

        member = Member.objects.create(user=user, **validated_data)
        return member   
        
    def update(self, instance, validated_data):
        self._update_user_fields(instance.user, validated_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        # Allow returning standard name/email/contactNumber fields on READ
        ret = super().to_representation(instance)
        ret['name'] = instance.user.get_full_name() or instance.user.username
        ret['email'] = instance.user.email
        ret['contactNumber'] = instance.user.phone_number
        return ret

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'email', 'password')

    def create(self, validated_data):
        username = validated_data.get('first_name', '').lower().replace(' ', '')
        if not username:
             username = validated_data.get('email', 'new_user').split('@')[0]
             
        base_username = username
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
             username = f"{base_username}{counter}"
             counter += 1

        user = CustomUser.objects.create_user(
            username=username,
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            password=validated_data['password']
        )
        return user


class MembershipPlanViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipPlanSerializer
    
    def get_queryset(self):
        # prefetch_related grabs all nested many-to-many services in one extra query
        return MembershipPlan.objects.prefetch_related('services').all()


class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    
    def get_queryset(self):
        # select_related joins the User table (OneToOne/ForeignKey)
        # prefetch_related grabs the ManyToMany and Reverse ForeignKey relations
        return Member.objects.select_related('user').prefetch_related(
            'branches', 
            'subscriptions__plan' # Grabs the subscription and the nested plan inside it
        ).all()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['role'] = user.role
        return token

    def validate(self, attrs):
        login_input = attrs.get('username', '')
        try:
            # Look up by username, email, or first_name
            user = CustomUser.objects.get(
                Q(username__iexact=login_input) |
                Q(email__iexact=login_input) |
                Q(first_name__iexact=login_input)
            )
            # Replace what was given with the real username so JWT can find the user
            attrs['username'] = user.username
            
        except CustomUser.DoesNotExist:
            # Let simplejwt handle the "Invalid credentials" error normally
            pass 
            
        except CustomUser.MultipleObjectsReturned:
            # FIX: Catch the collision and tell the user how to fix it
            raise serializers.ValidationError({
                "detail": "Multiple accounts found with this name. Please log in using your registered email address instead."
            })
            
        return super().validate(attrs)
