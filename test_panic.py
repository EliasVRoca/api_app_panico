import os
import django
import requests
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from contacts.models import Contact

User = get_user_model()

# 1. Crear usuario
print("Creando o recuperando usuario...")
user, created = User.objects.get_or_create(email="juan.perez@test.com", defaults={"first_name": "Juan", "last_name": "Perez"})
user.set_password("Admin123!")
user.save()

# 2. Añadir contacto
print("Añadiendo contacto Elias Vasquez Roca (59169220076)...")
contact, _ = Contact.objects.get_or_create(user=user, phone_number="59169220076", defaults={"name": "Elias Vasquez Roca"})

# Esperamos un segundo por si el servidor apenas se está levantando
time.sleep(2)

# 3. Obtener token
print("Obteniendo token de acceso...")
login_data = {
    "username": "juan.perez@test.com",
    "password": "Admin123!"
}
try:
    login_response = requests.post("http://127.0.0.1:8000/api/auth/login/", json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json().get("access")
        
        # 4. Probar el endpoint
        print("Probando el endpoint /api/panic/activate/...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "latitude": -17.778818,
            "longitude": -63.188941
        }
        response = requests.post('http://127.0.0.1:8000/api/panic/activate/', json=payload, headers=headers)

        print("Status Code:", response.status_code)
        import json
        print("Response JSON:\n", json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print("Error al iniciar sesión:", login_response.status_code, login_response.text)
except requests.exceptions.ConnectionError:
    print("El servidor aún no está levantado en http://127.0.0.1:8000. Por favor, espera a que termine de iniciar.")
