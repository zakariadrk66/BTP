from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.protected_url = reverse('protected')
        
        # Create a test user
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )

    def test_user_registration(self):
        """Test that a user can register"""
        response = self.client.post(self.register_url, {
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        """Test that a user can login"""
        response = self.client.post(self.login_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_protected_endpoint_without_auth(self):
        """Test that protected endpoint requires authentication"""
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_auth(self):
        """Test that protected endpoint works with valid token"""
        # First, login to get tokens
        login_response = self.client.post(self.login_url, self.user_data)
        token = login_response.data['access']
        
        # Then access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)