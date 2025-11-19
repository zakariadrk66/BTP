from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import devices_for_user
import qrcode
from io import BytesIO
import base64
from .serializers import UserRegistrationSerializer, UserLoginSerializer, TwoFactorSetupSerializer, TwoFactorVerifySerializer
from .models import CustomUser
from .token_serializers import CustomTokenObtainPairSerializer
import json 
from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Check if user has 2FA enabled
        if user.is_2fa_enabled:
            # Generate and send 2FA code via email
            otp_code = user.generate_email_2fa_code()
            
            # Send email with OTP (you'll need to configure email settings)
            try:
                send_mail(
                    'Your 2FA Code',
                    f'Your 2FA code is: {otp_code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except:
                return Response({'error': 'Failed to send 2FA email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'message': '2FA code sent to email',
                'user_id': user.id
            }, status=status.HTTP_202_ACCEPTED)
        
        # If no 2FA, generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def setup_email_2fa(request):
    user = request.user
    user.is_2fa_enabled = True
    user.save()
    return Response({'message': 'Email 2FA enabled'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def verify_2fa_setup(request):
    """Verify the initial 2FA setup with the token from the authenticator app"""
    user = request.user
    token = request.data.get('token')
    
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get the unconfirmed device for this user
    device = user.totpdevice_set.filter(confirmed=False).first()
    
    if not device:
        # If no unconfirmed device exists, check if they already have a confirmed one
        if user.totpdevice_set.filter(confirmed=True).exists():
            return Response({'error': '2FA already set up'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Create a new device if none exists
            device = user.totpdevice_set.create(name="default")
    
    # Verify the token
    if device.verify_token(token):
        device.confirmed = True
        device.save()
        user.is_2fa_enabled = True
        user.save()
        return Response({'message': '2FA setup successfully verified'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_2fa_login(request):
    """Verify 2FA token during login process"""
    user_id = request.data.get('user_id')
    token = request.data.get('token')
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    device = user.totpdevice_set.filter(confirmed=True).first()
    if device and device.verify_token(token):
        # Generate JWT tokens after successful 2FA
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_2fa(request):
    """Verify 2FA code sent to email during login"""
    user_id = request.data.get('user_id')
    otp_code = request.data.get('otp_code')
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if the code is correct and not expired
    if (user.email_2fa_code == otp_code and 
        user.email_2fa_expires and 
        user.email_2fa_expires > datetime.now()):
        
        # Clear the code after successful verification
        user.email_2fa_code = None
        user.email_2fa_expires = None
        user.save()
        
        # Generate JWT tokens after successful 2FA
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid or expired OTP code'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def disable_2fa(request):
    user = request.user
    user.is_2fa_enabled = False
    user.email_2fa_code = None
    user.email_2fa_expires = None
    user.save()
    return Response({'message': '2FA disabled successfully'})

@api_view(['GET'])
def check_2fa_status(request):
    """Check if current user has 2FA enabled"""
    user = request.user
    return Response({
        'is_2fa_enabled': user.is_2fa_enabled
    })

@api_view(['GET'])
def check_2fa_status(request):
    """Check if current user has 2FA enabled"""
    user = request.user
    return Response({
        'is_2fa_enabled': user.is_2fa_enabled
    })