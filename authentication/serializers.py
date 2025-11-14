from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser
from django_otp.plugins.otp_totp.models import TOTPDevice

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Invalid credentials')
        else:
            raise serializers.ValidationError('Email and password required')

class TwoFactorSetupSerializer(serializers.Serializer):
    qr_code = serializers.CharField(read_only=True)
    secret_key = serializers.CharField(read_only=True)

class TwoFactorVerifySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=6)