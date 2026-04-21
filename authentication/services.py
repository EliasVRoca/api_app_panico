from typing import Dict, Any
from django.conf import settings
from django.core.exceptions import ValidationError
from google.oauth2 import id_token
from google.auth.transport import requests
from users.models import CustomUser

import uuid

def user_create(email: str, username: str, password: str = None, **extra_fields) -> CustomUser:
    """
    Service for creating a new user. 
    Enforces business logic.
    """
    if not email:
        raise ValidationError('Email must be provided.')
    if not username:
        raise ValidationError('Username must be provided.')
        
    user = CustomUser(email=email, username=username, **extra_fields)
    
    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()
        
    user.full_clean()
    user.save()
    
    return user

def user_get_or_create(*, email: str, **extra_data) -> tuple[CustomUser, bool]:
    user = CustomUser.objects.filter(email=email).first()
    
    if user:
        return user, False
    
    # Generate a unique username for Google OAuth users
    base_username = email.split('@')[0]
    username = base_username
    while CustomUser.objects.filter(username=username).exists():
        username = f"{base_username}{uuid.uuid4().hex[:4]}"
        
    return user_create(email=email, username=username, **extra_data), True

def google_validate_id_token(id_token_str: str) -> Dict[str, Any]:
    """
    Validates a Google OAuth ID Token.
    Returns the decoded token info if valid, or raises ValueError.
    """
    # Assuming the client application receives an id_token and sends it to the API
    try:
        # If you have a specific GOOGLE_OAUTH2_CLIENT_ID, you can pass audience=CLIENT_ID here.
        # But we leave it flexible so it accepts any valid Google token from your frontend.
        # It's recommended to define GOOGLE_OAUTH2_CLIENT_ID in settings and use it.
        client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', None)
        
        idinfo = id_token.verify_oauth2_token(
            id_token_str, 
            requests.Request(), 
            client_id
        )
        
        # Verify provider
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
            
        return idinfo
    except Exception as e:
        raise ValueError(f"The token is either invalid or has expired: {str(e)}")
