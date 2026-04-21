# Panic Button API - Django REST Framework

Este proyecto es una API robusta para un sistema de **Botón de Pánico**. Permite a los usuarios registrarse, gestionar contactos de emergencia y activar alertas que simulan el envío de notificaciones automáticas.

## 🚀 Características Principales

- **Autenticación Segura**: Uso de JWT (SimpleJWT) y soporte para Google OAuth2.
- **RBAC (Control de Acceso basado en Roles)**: Gestión de usuarios y roles para administradores.
- **Sistema de Contactos**: Límites dinámicos según el nivel de suscripción del usuario (`free` vs `premium`).
- **Modo Pánico**: Registro de eventos con coordenadas GPS y simulación de alertas en cascada.
- **Documentación Interactiva**: Integración completa con `drf-spectacular` (Swagger/Redoc).

## 🛠️ Requisitos Previos

- Python 3.10 o superior.
- Pip (gestor de paquetes de Python).
- Un entorno virtual (recomendado).

## ⚙️ Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto localmente:

1. **Clonar el repositorio** (si aún no lo has hecho):
   ```bash
   git clone https://github.com/tu-usuario/drf_google_api.git
   cd drf_google_api
   ```

2. **Crear y activar un entorno virtual**:
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar migraciones**:
   ```bash
   python manage.py migrate
   ```

5. **Crear un superusuario** (para acceder al admin):
   ```bash
   python manage.py createsuperuser
   ```

6. **Iniciar el servidor**:
   ```bash
   python manage.py runserver
   ```

El servidor estará disponible en `http://127.0.0.1:8000/`.

## 📖 Documentación

- **Guía para Frontend**: Hemos preparado una guía detallada con todos los endpoints, payloads y ejemplos. Consúltala aquí: [API_GUIDE.md](./API_GUIDE.md).
- **Swagger UI**: Accede a la documentación interactiva en vivo en `/api/docs/swagger/`.
- **Redoc**: Alternativa de visualización en `/api/docs/redoc/`.

## 🧪 Pruebas

Para ejecutar la suite de pruebas y verificar que todo funciona correctamente:
```bash
python manage.py test
```
O ejecutar los scripts de prueba específicos:
```bash
python test_endpoints.py
```

---
Desarrollado con ❤️ usando Django REST Framework.
