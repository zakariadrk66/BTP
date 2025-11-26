# authentication/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
import jwt
from .models import CustomUser

class TwoFactorAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip middleware for auth endpoints to avoid circular dependency
        if request.path.startswith('/api/auth/'):
            return None

        # Skip middleware for all API endpoints - let DRF handle JWT authentication
        if request.path.startswith('/api/'):
            return None

        # Apply 2FA check only to regular web requests (not API)
        # Add your web interface 2FA logic here if needed
        # For now, we'll allow all non-API requests without 2FA
        # (You can implement web-specific 2FA logic here later)
        
        return None