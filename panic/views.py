from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer

from django.conf import settings
import requests

from .models import PanicEvent
from .serializers import PanicEventSerializer


# Response schema for the activate endpoint
class PanicActivateResponseSerializer(serializers.Serializer):
    message      = serializers.CharField()
    event        = PanicEventSerializer()
    alert_logs   = serializers.ListField(child=serializers.CharField())


class PanicEventActivateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['panic'],
        summary="Activar Modo Pánico",
        description=(
            "Registra un evento de pánico con la ubicación del usuario y **envía** un "
            "mensaje de WhatsApp a todos sus contactos usando la API oficial de Meta."
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

        alert_logs = []
        
        # Configuración de Meta API
        token = settings.META_WHATSAPP_TOKEN
        phone_id = settings.META_WHATSAPP_PHONE_ID
        template_name = settings.META_WHATSAPP_TEMPLATE_NAME
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"https://graph.facebook.com/v25.0/{phone_id}/messages"
        
        # Preparar parámetros del mensaje
        user_name = f"{user.first_name} {user.last_name}".strip()
        if not user_name:
            user_name = user.email

        if panic_event.latitude and panic_event.longitude:
            coords_str = f"{panic_event.latitude},{panic_event.longitude},21z"
        else:
            coords_str = "0,0,21z" # Fallback si no hay ubicación

        for contact in contacts:
            # Formatear el número (quitar '+' y espacios)
            phone_str = str(contact.phone_number).replace('+', '').replace(' ', '')
            contact_name = contact.name if contact.name else "Contacto"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_str,
                "type": "template",
                "template": {
                    "name": template_name, # Debería ser 'aviso_preventivo'
                    "language": {
                        "code": "es"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": str(contact_name)
                                },
                                {
                                    "type": "text",
                                    "text": str(user_name)
                                }
                            ]
                        },
                        {
                            "type": "button",
                            "sub_type": "url",
                            "index": "0",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": coords_str
                                }
                            ]
                        }
                    ]
                }
            }
            
            try:
                # Si las credenciales están configuradas, hacer la petición real
                if token and phone_id and template_name:
                    response = requests.post(url, headers=headers, json=payload, timeout=5)
                    response.raise_for_status()
                    alert_logs.append(f"WhatsApp enviado a {contact.name} ({phone_str}) exitosamente.")
                else:
                    # Fallback a simulación si no hay credenciales (útil para desarrollo)
                    msg = (
                        f"Simulando WhatsApp a {contact.name} ({phone_str}): "
                        f"Hola {contact_name}. {user_name} se encuentra en una situación... "
                        f"Mapa: https://www.google.com/maps/@{coords_str}"
                    )
                    alert_logs.append(msg)
                    print(msg)
            except requests.exceptions.RequestException as e:
                # Capturamos el error pero no rompemos el flujo para intentar con los demás contactos
                error_detail = str(e)
                if e.response is not None:
                    error_detail = e.response.text
                alert_logs.append(f"Error al enviar a {contact.name} ({phone_str}): {error_detail}")

        return Response({
            "message": "Evento de pánico generado procesado correctamente.",
            "event": serializer.data,
            "alert_logs": alert_logs,
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
