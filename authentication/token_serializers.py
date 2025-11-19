from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Custom validation for email-based login
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                               username=email, password=password)

            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            # Check if user has 2FA enabled
            if hasattr(user, 'is_2fa_enabled') and user.is_2fa_enabled:
                # Return that 2FA is needed
                return {
                    'user_id': user.id,
                    'message': '2FA required'
                }

            # If no 2FA, generate tokens
            refresh = self.get_token(user)

            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        else:
            raise serializers.ValidationError('Email and password required')

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['user_id'] = user.id

        return token