from django.contrib.auth import authenticate
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer

from .services import user_create, google_validate_id_token, user_get_or_create
from django.core.exceptions import ValidationError


# ─────────────────────────────────────────────────────────────────────────────
# Shared serializers used by @extend_schema (must be module-level for drf-spectacular)
# ─────────────────────────────────────────────────────────────────────────────

class LoginInputSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Nombre de usuario o correo electrónico")
    password = serializers.CharField(write_only=True, help_text="Contraseña")


class LoginResponseSerializer(serializers.Serializer):
    access  = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    user    = inline_serializer(name='LoginUser', fields={
        'id':       serializers.IntegerField(),
        'email':    serializers.EmailField(),
        'username': serializers.CharField(),
    })


class RegisterInputSerializer(serializers.Serializer):
    email        = serializers.EmailField(help_text="Correo electrónico único")
    username     = serializers.CharField(help_text="Nombre de usuario único")
    phone_number = serializers.CharField(required=False, allow_blank=True, help_text="Teléfono (opcional)")
    password     = serializers.CharField(write_only=True, help_text="Contraseña")


class RegisterResponseSerializer(serializers.Serializer):
    access  = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    user    = inline_serializer(name='RegisterUser', fields={
        'id':    serializers.IntegerField(),
        'email': serializers.EmailField(),
    })


class GoogleLoginInputSerializer(serializers.Serializer):
    id_token = serializers.CharField(help_text="Google OAuth2 ID Token recibido desde el cliente")


class GoogleLoginResponseSerializer(serializers.Serializer):
    access  = serializers.CharField()
    refresh = serializers.CharField()
    is_new  = serializers.BooleanField(help_text="True si el usuario fue creado en este login")
    user    = inline_serializer(name='GoogleUser', fields={
        'id':    serializers.IntegerField(),
        'email': serializers.EmailField(),
    })


# ─────────────────────────────────────────────────────────────────────────────
# Mixin
# ─────────────────────────────────────────────────────────────────────────────

class CustomTokenMixin:
    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Views
# ─────────────────────────────────────────────────────────────────────────────

class LoginApi(APIView, CustomTokenMixin):
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=['auth'],
        summary="Login (username o email)",
        description="Permite autenticarse usando el nombre de usuario **o** el correo electrónico en el campo `username`.",
        request=LoginInputSerializer,
        responses={
            200: LoginResponseSerializer,
            401: OpenApiResponse(description="Credenciales inválidas"),
            403: OpenApiResponse(description="Cuenta inactiva"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )

        if not user:
            return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({'error': 'Cuenta inactiva.'}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'user': {'id': user.id, 'email': user.email, 'username': user.username},
            **self.get_tokens_for_user(user),
        }, status=status.HTTP_200_OK)


class UserRegistrationApi(APIView, CustomTokenMixin):
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=['auth'],
        summary="Registro de usuario",
        description="Crea un nuevo usuario con tier **free** por defecto y devuelve los tokens JWT.",
        request=RegisterInputSerializer,
        responses={
            201: RegisterResponseSerializer,
            400: OpenApiResponse(description="Datos inválidos o usuario ya existente"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = user_create(**serializer.validated_data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'user': {'id': user.id, 'email': user.email},
            **self.get_tokens_for_user(user),
        }, status=status.HTTP_201_CREATED)


class GoogleLoginApi(APIView, CustomTokenMixin):
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=['auth'],
        summary="Login con Google",
        description="Autentica o registra al usuario usando un ID Token de Google OAuth2.",
        request=GoogleLoginInputSerializer,
        responses={
            200: GoogleLoginResponseSerializer,
            400: OpenApiResponse(description="Token de Google inválido o expirado"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = GoogleLoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            google_data      = google_validate_id_token(serializer.validated_data['id_token'])
            email            = google_data.get('email')
            user, is_new     = user_get_or_create(email=email)

            return Response({
                'user':   {'id': user.id, 'email': user.email},
                'is_new': is_new,
                **self.get_tokens_for_user(user),
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
