"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

def api_root_view(request):
    """
    Returns a list of available API endpoints.
    """
    return JsonResponse({
        "message": "Welcome to the Django REST API",
        "available_urls": {
            "admin": "/admin/",
            "auth": {
                "login": "/api/auth/login/",
                "token_refresh": "/api/auth/token/refresh/",
                "register": "/api/auth/register/",
                "google_login": "/api/auth/google-login/",
            },
            "api_routers_root": "/api/",
            "users": "/api/users/",
            "roles": "/api/roles/",
            "contacts": "/api/contacts/",
            "panic": {
                "activate": "/api/panic/activate/",
                "history": "/api/panic/history/",
            },
            "docs": {
                "swagger_ui": "/api/docs/swagger/",
                "redoc_ui": "/api/docs/redoc/",
                "schema_file": "/api/schema/"
            }
        }
    })

urlpatterns = [
    path('', api_root_view, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/', include('users.urls')),
    path('api/', include('roles.urls')),
    path('api/', include('contacts.urls')),
    path('api/panic/', include('panic.urls')),
    
    # OpenAPI Schema Generation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # UI Documentation (Swagger / Redoc)
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
