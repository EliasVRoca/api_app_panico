from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import CustomUser
from .serializers import UserSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['users'],
        summary="Listar usuarios",
        description="Devuelve la lista de todos los usuarios del sistema. Solo accesible por administradores."
    ),
    retrieve=extend_schema(
        tags=['users'],
        summary="Obtener usuario",
        description="Devuelve los datos de un usuario por su ID.",
        parameters=[OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH)]
    ),
    create=extend_schema(
        tags=['users'],
        summary="Crear usuario (admin)",
        description="Crea un usuario directamente desde el panel administrativo."
    ),
    update=extend_schema(tags=['users'], summary="Actualizar usuario completo"),
    partial_update=extend_schema(tags=['users'], summary="Actualizar usuario parcialmente (PATCH)"),
    destroy=extend_schema(tags=['users'], summary="Eliminar usuario"),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset           = CustomUser.objects.all()
    serializer_class   = UserSerializer
    permission_classes = [IsAdminUser]
