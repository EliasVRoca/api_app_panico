from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Role
from .serializers import RoleSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['roles'],
        summary="Listar roles",
        description="Devuelve todos los roles del sistema. Solo accesible por administradores."
    ),
    retrieve=extend_schema(
        tags=['roles'],
        summary="Obtener rol por ID",
        parameters=[OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH)]
    ),
    create=extend_schema(
        tags=['roles'],
        summary="Crear rol",
        description="Crea un nuevo rol. Solo administradores."
    ),
    update=extend_schema(tags=['roles'], summary="Actualizar rol completo (PUT)"),
    partial_update=extend_schema(tags=['roles'], summary="Actualizar rol parcialmente (PATCH)"),
    destroy=extend_schema(tags=['roles'], summary="Eliminar rol"),
)
class RoleViewSet(viewsets.ModelViewSet):
    queryset           = Role.objects.all()
    serializer_class   = RoleSerializer
    permission_classes = [IsAdminUser]
