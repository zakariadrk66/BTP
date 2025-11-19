from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """A simple protected view to test authentication"""
    return Response({
        'message': f'Hello {request.user.email}, you are authenticated!',
        'user_id': request.user.id
    })