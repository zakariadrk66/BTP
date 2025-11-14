from django.urls import path
from . import views
from .test_views import protected_view

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('setup-2fa/', views.setup_2fa, name='setup_2fa'),
    path('verify-2fa-setup/', views.verify_2fa_setup, name='verify_2fa_setup'),
    path('verify-2fa-login/', views.verify_2fa_login, name='verify_2fa_login'),
    path('disable-2fa/', views.disable_2fa, name='disable_2fa'),
    path('check-2fa-status/', views.check_2fa_status, name='check_2fa_status'),
    path('protected/', protected_view, name='protected'),

]