from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.urls import resolve
from django.conf import settings
import jwt
from .models import CustomUser

class TwoFactorAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip middleware for auth endpoints to avoid circular dependency
        if request.path.startswith('/api/auth/'):
            return None
            
        # Define which endpoints require authentication
        auth_required = not any([
            request.path == '/api/auth/login/',
            request.path == '/api/auth/register/',
            request.path == '/api/auth/verify-2fa/',
        ])
        
        if auth_required and request.path.startswith('/api/'):
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'error': 'Authorization header required'}, status=401)
            
            token = auth_header.split(' ')[1]
            
            try:
                payload = jwt.decode(token, settings.SIMPLE_JWT['VERIFYING_KEY'], algorithms=['HS256'])
                user_id = payload.get('user_id')
                
                try:
                    user = CustomUser.objects.get(id=user_id)
                    
                    # Check if user has 2FA enabled
                    if user.totpdevice_set.filter(confirmed=True).exists():
                        # Verify if 2FA is verified for this session (simplified approach)
                        # In a real app, you might store this in session or another token
                        pass
                    
                    request.user = user
                except CustomUser.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=401)
                    
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        
        return None