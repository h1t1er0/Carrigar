from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import json
import os

# Create your views here.

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=400)
        
        # Authenticate user
        user = authenticate(username=user.username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True, 
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}".strip() or user.username
                }
            })
        else:
            return JsonResponse({'success': False, 'message': 'Invalid password'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def signup_view(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        is_company = data.get('is_company', False)
        company_name = data.get('company_name', '')
        gst_number = data.get('gst_number', '')
        business_address = data.get('business_address', '')
        address = data.get('address', '')
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'User with this email already exists'}, status=400)
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name.split()[0] if name else '',
            last_name=' '.join(name.split()[1:]) if name and len(name.split()) > 1 else ''
        )
        # Update profile fields
        profile = user.userprofile
        profile.phone_number = phone
        profile.is_company = is_company
        profile.company_name = company_name
        profile.gst_number = gst_number
        profile.business_address = business_address
        profile.address = address
        profile.save()
        # Login user
        login(request, user)
        return JsonResponse({
            'success': True,
            'message': 'Account created successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip() or user.username
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def logout_view(request):
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out successfully'})

def login_page(request):
    """Serve the login page"""
    return render(request, 'accounts/login.html')

def check_auth(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
            }
        })
    else:
        return JsonResponse({'authenticated': False})

def google_login(request):
    """Initiate Google OAuth login"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_OAUTH2_REDIRECT_URI],
            }
        },
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
    )
    
    flow.redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    request.session['google_oauth_state'] = state
    return redirect(authorization_url)

def google_callback(request):
    """Handle Google OAuth callback"""
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_OAUTH2_REDIRECT_URI],
                }
            },
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
        )
        
        flow.redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI
        
        # Exchange authorization code for tokens
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)
        
        # Get user info from Google
        credentials = flow.credentials
        id_info = id_token.verify_oauth2_token(
            credentials.id_token, 
            requests.Request(), 
            settings.GOOGLE_OAUTH2_CLIENT_ID
        )
        
        email = id_info['email']
        name = id_info.get('name', '')
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        
        # Check if user exists, create if not
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        
        if created:
            # Set a random password for Google users
            user.set_password(User.objects.make_random_password())
            user.save()
        
        # Login user
        login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Google login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip() or user.username
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Google login failed: {str(e)}'}, status=400)

@login_required
def profile_view(request):
    profile = request.user.userprofile
    return render(request, 'accounts/profile.html', {'profile': profile})

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def profile_update(request):
    try:
        data = json.loads(request.body)
        profile = request.user.userprofile
        profile.phone_number = data.get('phone_number', profile.phone_number)
        profile.is_company = data.get('is_company', profile.is_company)
        profile.company_name = data.get('company_name', profile.company_name)
        profile.gst_number = data.get('gst_number', profile.gst_number)
        profile.business_address = data.get('business_address', profile.business_address)
        profile.address = data.get('address', profile.address)
        profile.save()
        # Optionally update user name
        if 'first_name' in data:
            request.user.first_name = data['first_name']
        if 'last_name' in data:
            request.user.last_name = data['last_name']
        request.user.save()
        return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
