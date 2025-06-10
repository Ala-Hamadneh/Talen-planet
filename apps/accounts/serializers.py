from rest_framework import serializers
from .models import User, UserRoles,EmailVerificationCode
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from django.contrib.auth.password_validation import validate_password


from .utils import generate_verification_code
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoles
        fields = ['role_id', 'role_name']

class UserRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoles
        fields = ['role_id', 'role_name']

class UserSerializer(serializers.ModelSerializer):
    role = UserRolesSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)


    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'role', 'role_id', 'profile_picture',
            'bio', 'created_at', 'updated_at',
            'is_staff', 'is_superuser', 'password',
            'average_rating', 'reviews_count','is_active','is_verified'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        role_id = validated_data.pop('role_id')

        # Prevent any attempt to create an admin account
        validated_data['is_staff'] = False
        validated_data['is_superuser'] = False

        # Only allow roles Buyer or Seller
        try:
            role = UserRoles.objects.get(pk=role_id)
            if role.role_name.lower() not in ['buyer', 'seller']:
                raise serializers.ValidationError({'role_id': 'Only Buyer or Seller roles are allowed.'})
        except UserRoles.DoesNotExist:
            raise serializers.ValidationError({'role_id': 'Invalid role ID.'})

        user = User(**validated_data)
        user.role = role

        if password:
            user.set_password(password)
        else:
            raise serializers.ValidationError({'password': 'Password is required.'})

        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        validated_data.pop('role_id', None)
        validated_data.pop('is_superuser', None)
        validated_data.pop('is_staff', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        validate_password(value)
        return value
    
    def validate(self, data):
        """
        Check that the new password and confirmation match.
        """
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({
                'confirm_new_password': "New passwords don't match."
            })
        return data

# class PasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=True)



class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self, request):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        reset_link = f"https://preview--planet-freelance-hub.lovable.app/reset-password/{uid}/{token}/"
        
        user.email_user(
            subject="Password Reset",
            message=f"Click the link below to reset your password:\n{reset_link}",
            from_email=None,
        )

    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['user_id'] = user.id
        token['username'] = user.username
        token['email'] = user.email
        token['is_admin'] = user.is_superuser
        token['user_role'] = user.role.role_name if user.role else None  # ✅ Add this
        token['is_staff'] = user.is_staff
        return token
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_verified:
            raise AuthenticationFailed("Please verify your email first.")

        return data
    

class EmailVerificationRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        code = generate_verification_code()

        # Optional: remove old codes for this email
        EmailVerificationCode.objects.filter(email=validated_data['email']).delete()

        verification = EmailVerificationCode.objects.create(
            email=validated_data['email'],
            code=code
        )

        send_mail(
            subject="Your Verification Code",
            message=f"Your verification code is: {code}. It will expire in 2 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[validated_data['email']],
            fail_silently=False,
        )

        return verification  # ✅ Now DRF is satisfied

    
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailVerificationConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            record = EmailVerificationCode.objects.filter(
                email=data['email'],
                code=data['code']
            ).latest('created_at')
        except EmailVerificationCode.DoesNotExist:
            raise serializers.ValidationError("Invalid verification code.")

        if record.is_expired():
            raise serializers.ValidationError("Verification code has expired.")

        # Mark user as verified
        try:
            user = User.objects.get(email=data['email'])
            user.is_verified = True
            user.save()
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        return data


class PublicUserProfileSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    profile_picture = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture', 'bio', 'average_rating']
