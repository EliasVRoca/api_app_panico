from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer

from .models import PanicEvent
from .serializers import PanicEventSerializer


# Response schema for the activate endpoint
class PanicActivateResponseSerializer(serializers.Serializer):
    message      = serializers.CharField()
    event        = PanicEventSerializer()
    simulated_logs = serializers.ListField(child=serializers.CharField())


class PanicEventActivateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['panic'],
        summary="Activar Modo Pánico",
        description=(
            "Registra un evento de pánico con la ubicación del usuario y **simula** el "
            "envío de alertas (SMS/WhatsApp) a todos sus contactos en orden de prioridad."
        ),
        request=inline_serializer(
            name='PanicActivateInput',
            fields={
                'latitude':  serializers.DecimalField(
                    max_digits=9, decimal_places=6, required=False,
                    help_text="Latitud GPS del usuario (ej: 10.480600)"
                ),
                'longitude': serializers.DecimalField(
                    max_digits=9, decimal_places=6, required=False,
                    help_text="Longitud GPS del usuario (ej: -66.903600)"
                ),
            }
        ),
        responses={
            201: PanicActivateResponseSerializer,
            401: OpenApiResponse(description="No autenticado"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = PanicEventSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        panic_event = serializer.save()

        user     = request.user
        contacts = user.contacts.all()

        simulated_logs = []
        for contact in contacts:
            msg = (
                f"Simulando SMS a {contact.name} ({contact.phone_number}): "
                f"¡ALERTA DE PÁNICO! {user.email} requiere ayuda."
            )
            if panic_event.latitude and panic_event.longitude:
                msg += f" Coordenadas: {panic_event.latitude}, {panic_event.longitude}"
            print(msg)
            simulated_logs.append(msg)

        return Response({
            "message": "Panic event generated successfully and alerts simulated.",
            "event": serializer.data,
            "simulated_logs": simulated_logs,
        }, status=status.HTTP_201_CREATED)


class PanicEventHistoryAPIView(generics.ListAPIView):
    serializer_class   = PanicEventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['panic'],
        summary="Historial de Eventos de Pánico",
        description="Devuelve todos los eventos de pánico del usuario autenticado, ordenados del más reciente al más antiguo.",
        responses={
            200: PanicEventSerializer(many=True),
            401: OpenApiResponse(description="No autenticado"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return PanicEvent.objects.filter(user=self.request.user)
