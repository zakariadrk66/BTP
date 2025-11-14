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
    # Use the custom serializer to handle login
    serializer = CustomTokenObtainPairSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        result = serializer.validated_data
        
        # Check if 2FA is required
        if 'message' in result and result['message'] == '2FA required':
            return Response({
                'message': '2FA required',
                'user_id': result['user_id']
            }, status=status.HTTP_202_ACCEPTED)
        
        return Response(result, status=status.HTTP_200_OK)
    except serializers.ValidationError:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def setup_2fa(request):
    user = request.user
    device, created = TOTPDevice.objects.get_or_create(user=user, name="default")
    
    if not device.confirmed:
        # Generate QR code
        qr_url = device.config_url
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code = base64.b64encode(buffer.getvalue()).decode()
        
        return Response({
            'qr_code': qr_code,
            'secret_key': device.key
        })
    else:
        return Response({'message': '2FA already set up'}, status=status.HTTP_400_BAD_REQUEST)

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
def disable_2fa(request):
    user = request.user
    device = user.totpdevice_set.first()
    if device:
        device.delete()
        user.is_2fa_enabled = False
        user.save()
    return Response({'message': '2FA disabled successfully'})

@api_view(['GET'])
def check_2fa_status(request):
    """Check if current user has 2FA enabled"""
    user = request.user
    return Response({
        'is_2fa_enabled': user.is_2fa_enabled
    })