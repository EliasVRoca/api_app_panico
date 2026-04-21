from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Contact
from .serializers import ContactSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['contacts'],
        summary="Listar contactos",
        description=(
            "Devuelve los contactos de emergencia del usuario autenticado, "
            "ordenados por prioridad (1 = más prioritario)."
        )
    ),
    retrieve=extend_schema(
        tags=['contacts'],
        summary="Obtener contacto por ID",
        parameters=[OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH)]
    ),
    create=extend_schema(
        tags=['contacts'],
        summary="Crear contacto",
        description=(
            "Agrega un contacto de emergencia. "
            "**Límite: 3 contactos** para usuarios `free`, **10** para usuarios `premium`. "
            "Returns HTTP 400 si se supera el límite."
        )
    ),
    update=extend_schema(tags=['contacts'], summary="Actualizar contacto completo (PUT)"),
    partial_update=extend_schema(
        tags=['contacts'],
        summary="Actualizar contacto parcialmente (PATCH)",
        description="Útil para cambiar únicamente la prioridad u otro campo sin reenviar todos los datos."
    ),
    destroy=extend_schema(tags=['contacts'], summary="Eliminar contacto"),
)
class ContactViewSet(viewsets.ModelViewSet):
    serializer_class   = ContactSerializer
    permission_classes = [IsAuthenticated]
    queryset           = Contact.objects.all()   # needed by drf-spectacular for schema

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)
