from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import CustomUser, Application, RefreshToken


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that uses email instead of username
    """
    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField()
        del self.fields['username']

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        return token

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                              username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        attrs['user'] = user
        return attrs


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'created_at', 'last_login')
        read_only_fields = ('id', 'created_at', 'last_login')


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for Application model
    """
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def validate_status(self):
        status = self.validated_data.get('status')
        
        # If we're updating an existing application
        if self.instance and self.instance.pk:
            # Prevent skipping from WISHLIST directly to OFFER
            if self.instance.status == 'WISHLIST' and status == 'OFFER':
                raise serializers.ValidationError(
                    "Cannot move directly from Wishlist to Offer. Please update through the application process."
                )
        
        return status


class RefreshTokenSerializer(serializers.ModelSerializer):
    """
    Serializer for RefreshToken model
    """
    class Meta:
        model = RefreshToken
        fields = ('id', 'created_at', 'expires_at', 'is_revoked', 'device_info', 'ip_address')
        read_only_fields = ('id', 'created_at', 'expires_at', 'is_revoked')


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords don't match.")
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value