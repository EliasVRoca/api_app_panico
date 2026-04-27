"""
test_endpoints.py
=================
Suite completa de pruebas para la API.

Uso:
  python test_endpoints.py            → prueba local (http://127.0.0.1:8000)
  python test_endpoints.py prod       → prueba producción (https://api.ework.ia.bo)
  python test_endpoints.py http://... → URL personalizada

Escenarios cubiertos:
  0.  Preparacion de usuarios de prueba
  1.  Login Admin (username y email)
  2.  GET /api/users/me  (usuario autenticado)
  3.  CRUD Roles (admin)
  4.  CRUD Usuarios (admin)
  5.  Registro usuario Free
  6.  Login usuario Free
  7.  Contactos usuario Free (limite 3)
  8.  Modo Panico usuario Free
  9.  Login usuario Premium
  10. Contactos usuario Premium (limite 10)
  11. Modo Panico usuario Premium
"""

import os
import sys
import json
import urllib.request
from urllib.error import HTTPError
import time

# ──────────────────────────────────────────────────────────────────────────────
# Selección de entorno
# ──────────────────────────────────────────────────────────────────────────────
arg = sys.argv[1] if len(sys.argv) > 1 else 'local'

if arg == 'prod':
    BASE = 'https://api.ework.ia.bo'
    PROD_MODE = True
elif arg.startswith('http'):
    BASE = arg.rstrip('/')
    PROD_MODE = False
else:
    BASE = 'http://127.0.0.1:8000'
    PROD_MODE = False

API  = f'{BASE}/api'
AUTH = f'{BASE}/api/auth'

# En modo producción NO hacemos bootstrap de Django (no tenemos acceso a la BD),
# creamos los usuarios de prueba vía los endpoints de la API.
if not PROD_MODE:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    from django.contrib.auth import get_user_model
    User = get_user_model()

# ──────────────────────────────────────────────────────────────────────────────
# Colores ANSI para la terminal
# ──────────────────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PASS_COUNT = 0
FAIL_COUNT = 0

def ok(msg):
    global PASS_COUNT
    PASS_COUNT += 1
    print(f"  {GREEN}✅ PASS{RESET} {msg}")

def fail(msg):
    global FAIL_COUNT
    FAIL_COUNT += 1
    print(f"  {RED}❌ FAIL{RESET} {msg}")

def section(title):
    print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*60}{RESET}")

def assert_status(label, actual, expected):
    if actual == expected:
        ok(f"{label} → HTTP {actual}")
    else:
        fail(f"{label} → esperado HTTP {expected}, obtenido HTTP {actual}")

# ──────────────────────────────────────────────────────────────────────────────
# HTTP helper
# ──────────────────────────────────────────────────────────────────────────────
def fetch(url, data=None, token=None, method='GET'):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    body = json.dumps(data).encode('utf-8') if data is not None else None
    req  = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            content = r.read().decode('utf-8')
            return r.status, (json.loads(content) if content else None)
    except HTTPError as e:
        content = e.read().decode('utf-8')
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = content
        return e.code, parsed

def login(identifier, password):
    status, resp = fetch(f'{AUTH}/login/', data={'username': identifier, 'password': password}, method='POST')
    token = resp.get('access') if isinstance(resp, dict) else None
    return token

# ──────────────────────────────────────────────────────────────────────────────
# Banner de entorno
# ──────────────────────────────────────────────────────────────────────────────
env_label = f"{YELLOW}🌐 PRODUCCIÓN{RESET}" if PROD_MODE else f"{CYAN}🏠 LOCAL{RESET}"
print(f"\n{BOLD}{'='*60}{RESET}")
print(f"{BOLD}  Entorno : {env_label}")
print(f"{BOLD}  Base URL: {BASE}{RESET}")
print(f"{BOLD}{'='*60}{RESET}")

ts = int(time.time())

# ──────────────────────────────────────────────────────────────────────────────
# 0. Preparación de usuarios de prueba
# ──────────────────────────────────────────────────────────────────────────────
section("0. Preparando usuarios de prueba")

FREE_EMAIL    = f'free_{ts}@test.com'
FREE_USERNAME = f'freeuser_{ts}'
FREE_PASS     = 'Free1234!'

PREM_EMAIL    = f'premium_{ts}@test.com'
PREM_USERNAME = f'premiumuser_{ts}'
PREM_PASS     = 'Premium1234!'

if not PROD_MODE:
    # Bootstrap directo por ORM
    admin, _ = User.objects.update_or_create(
        email='admin@admin.com',
        defaults=dict(username='admin', is_staff=True, is_superuser=True, is_active=True)
    )
    admin.set_password('admin')
    admin.save()
    print(f"  Admin listo: admin@admin.com / admin")

    premium_user, _ = User.objects.update_or_create(
        email=PREM_EMAIL,
        defaults=dict(username=PREM_USERNAME, tier='premium', is_active=True)
    )
    premium_user.set_password(PREM_PASS)
    premium_user.save()
    print(f"  Usuario Premium listo: {PREM_EMAIL} tier=premium")
else:
    print(f"  Modo producción: admin ya debe existir en el servidor (admin@admin.com / admin)")
    print(f"  Los usuarios de prueba free/premium se crearán vía /api/auth/register/")

# ──────────────────────────────────────────────────────────────────────────────
# 1. Login Admin
# ──────────────────────────────────────────────────────────────────────────────
section("1. Login de Administrador (por username y por email)")

admin_token = login('admin', 'admin')
if admin_token:
    ok("Login con username 'admin'")
else:
    fail("Login con username 'admin'  ← ¿El servidor está corriendo? ¿El usuario existe?")
    sys.exit(1)

admin_token_by_email = login('admin@admin.com', 'admin')
if admin_token_by_email:
    ok("Login con email 'admin@admin.com'")
else:
    fail("Login con email 'admin@admin.com'")

# ──────────────────────────────────────────────────────────────────────────────
# 2. GET /api/users/me  ← NUEVO
# ──────────────────────────────────────────────────────────────────────────────
section("2. GET /api/users/me (perfil del usuario autenticado)")

st, resp = fetch(f'{API}/users/me', token=admin_token)
assert_status("GET /api/users/me (admin autenticado)", st, 200)

if isinstance(resp, dict):
    # Verificar campos esperados
    for campo in ['id', 'username', 'email', 'tier', 'is_active', 'is_staff', 'roles']:
        if campo in resp:
            ok(f"  Campo presente: '{campo}' = {resp[campo]}")
        else:
            fail(f"  Campo ausente: '{campo}'")

    # Verificar que la contraseña NO está en la respuesta
    if 'password' not in resp:
        ok("  Contraseña NO expuesta en la respuesta ✓")
    else:
        fail("  ⚠️  Contraseña expuesta en la respuesta!")

# Sin token debe devolver 401
st, _ = fetch(f'{API}/users/me')
assert_status("GET /api/users/me sin token → debe ser 401", st, 401)

# ──────────────────────────────────────────────────────────────────────────────
# 3. CRUD Roles (como admin)
# ──────────────────────────────────────────────────────────────────────────────
section("3. CRUD de Roles (como Admin)")

role_name = f"Role_{ts}"

st, resp = fetch(f'{API}/roles/', data={"name": role_name, "description": "Rol de prueba"}, token=admin_token, method='POST')
assert_status("CREATE role", st, 201)
role_id = resp.get('id') if isinstance(resp, dict) else None

st, resp = fetch(f'{API}/roles/', token=admin_token)
assert_status("READ ALL roles", st, 200)

if role_id:
    st, resp = fetch(f'{API}/roles/{role_id}/', token=admin_token)
    assert_status("READ ONE role", st, 200)

if role_id:
    st, resp = fetch(f'{API}/roles/{role_id}/', data={"name": role_name + "_Update", "description": "Actualizado"}, token=admin_token, method='PUT')
    assert_status("UPDATE (PUT) role", st, 200)

if role_id:
    st, resp = fetch(f'{API}/roles/{role_id}/', data={"description": "Desc parcial"}, token=admin_token, method='PATCH')
    assert_status("PARTIAL UPDATE (PATCH) role", st, 200)

if role_id:
    st, resp = fetch(f'{API}/roles/{role_id}/', token=admin_token, method='DELETE')
    assert_status("DELETE role", st, 204)

# ──────────────────────────────────────────────────────────────────────────────
# 4. CRUD Usuarios (como admin)
# ──────────────────────────────────────────────────────────────────────────────
section("4. CRUD de Usuarios (como Admin)")

if not PROD_MODE:
    temp_email    = f'temp_{ts}@test.com'
    temp_username = f'tempuser_{ts}'
    temp_user = User.objects.create(email=temp_email, username=temp_username, is_active=True)
    temp_user.set_password('Temp1234!')
    temp_user.save()
    temp_id = temp_user.id
else:
    # En prod, creamos el usuario temporal vía register
    st, resp = fetch(f'{AUTH}/register/', data={
        "email": f'temp_{ts}@test.com',
        "username": f'tempuser_{ts}',
        "phone_number": "+591 77700000",
        "password": 'Temp1234!'
    }, method='POST')
    temp_id = resp.get('user', {}).get('id') if isinstance(resp, dict) else None

st, resp = fetch(f'{API}/users/', token=admin_token)
assert_status("READ ALL users", st, 200)
if isinstance(resp, list):
    ok(f"  Total usuarios en BD: {len(resp)}")

if temp_id:
    st, resp = fetch(f'{API}/users/{temp_id}/', token=admin_token)
    assert_status("READ ONE user", st, 200)
    if isinstance(resp, dict):
        tier_val = resp.get('tier', 'N/A')
        if tier_val == 'free':
            ok("  tier=free por defecto ✓")
        else:
            fail(f"  tier esperado 'free', obtenido '{tier_val}'")

    st, resp = fetch(f'{API}/users/{temp_id}/', data={"phone_number": "+591 71234567"}, token=admin_token, method='PATCH')
    assert_status("PARTIAL UPDATE (PATCH) user phone_number", st, 200)

    st, resp = fetch(f'{API}/users/{temp_id}/', token=admin_token, method='DELETE')
    assert_status("DELETE user", st, 204)

# ──────────────────────────────────────────────────────────────────────────────
# 5. Registro usuario Free
# ──────────────────────────────────────────────────────────────────────────────
section("5. Registro de Usuario Free via /api/auth/register/")

st, resp = fetch(f'{AUTH}/register/', data={
    "email": FREE_EMAIL,
    "username": FREE_USERNAME,
    "phone_number": "+591 71111111",
    "password": FREE_PASS
}, method='POST')
assert_status("POST /api/auth/register/", st, 201)

if isinstance(resp, dict) and resp.get('user'):
    ok(f"  Usuario creado: id={resp['user'].get('id')} email={resp['user'].get('email')}")
    ok("  Tokens JWT recibidos") if resp.get('access') else fail("  No se recibieron tokens")

# ──────────────────────────────────────────────────────────────────────────────
# 6. Login usuario Free
# ──────────────────────────────────────────────────────────────────────────────
section("6. Login de Usuario Free (dual auth)")

free_token = login(FREE_USERNAME, FREE_PASS)
if free_token:
    ok(f"Login con username '{FREE_USERNAME}'")
else:
    fail(f"Login con username '{FREE_USERNAME}'")
    sys.exit(1)

free_token_email = login(FREE_EMAIL, FREE_PASS)
if free_token_email:
    ok(f"Login con email '{FREE_EMAIL}'")
else:
    fail(f"Login con email '{FREE_EMAIL}'")

# Verificar /me para usuario free también
st, resp = fetch(f'{API}/users/me', token=free_token)
assert_status("GET /api/users/me (usuario free)", st, 200)
if isinstance(resp, dict):
    ok(f"  Email retornado: {resp.get('email')} tier={resp.get('tier')}")

# ──────────────────────────────────────────────────────────────────────────────
# 7. Contactos usuario Free (límite 3)
# ──────────────────────────────────────────────────────────────────────────────
section("7. Lista de Contactos - Usuario Free (max 3)")

free_contact_ids = []

for i in range(1, 4):
    st, resp = fetch(f'{API}/contacts/', data={
        "name": f"Contacto Free {i}",
        "phone_number": f"+591 7100000{i:02d}",
        "priority": i
    }, token=free_token, method='POST')
    assert_status(f"CREATE contacto {i}/3 (free)", st, 201)
    if isinstance(resp, dict) and resp.get('id'):
        free_contact_ids.append(resp['id'])

st, resp = fetch(f'{API}/contacts/', data={
    "name": "Contacto Extra",
    "phone_number": "+591 79999999",
    "priority": 4
}, token=free_token, method='POST')
if st == 400:
    ok(f"4to contacto RECHAZADO correctamente (HTTP 400) - limite free alcanzado")
    if isinstance(resp, dict):
        print(f"    Mensaje de error: {resp}")
else:
    fail(f"4to contacto debio ser rechazado (HTTP 400), obtenido HTTP {st}")

st, resp = fetch(f'{API}/contacts/', token=free_token)
assert_status("READ ALL contacts (free)", st, 200)
if isinstance(resp, list):
    ok(f"Total contactos = {len(resp)} (esperado 3)") if len(resp) == 3 else fail(f"Total contactos = {len(resp)} (esperado 3)")

if free_contact_ids:
    st, resp = fetch(f'{API}/contacts/{free_contact_ids[0]}/', token=free_token)
    assert_status("READ ONE contact (free)", st, 200)

if free_contact_ids:
    st, resp = fetch(f'{API}/contacts/{free_contact_ids[0]}/', data={"priority": 10}, token=free_token, method='PATCH')
    assert_status("PATCH contact prioridad (free)", st, 200)

if free_contact_ids:
    st, resp = fetch(f'{API}/contacts/{free_contact_ids[-1]}/', token=free_token, method='DELETE')
    assert_status("DELETE contact (free)", st, 204)
    free_contact_ids.pop()

# ──────────────────────────────────────────────────────────────────────────────
# 8. Modo Pánico - Usuario Free
# ──────────────────────────────────────────────────────────────────────────────
section("8. Modo Panico - Usuario Free")

st, resp = fetch(f'{API}/panic/activate/', data={
    "latitude": "10.480600",
    "longitude": "-66.903600"
}, token=free_token, method='POST')
assert_status("POST /api/panic/activate/ (free)", st, 201)

if isinstance(resp, dict):
    event_data = resp.get('event', {})
    logs = resp.get('simulated_logs', [])
    ok(f"Evento creado: id={event_data.get('id')} status={event_data.get('status')}")
    ok(f"Alertas simuladas a {len(logs)} contacto(s) en orden de prioridad")
    for log in logs:
        print(f"    LOG: {log}")

st, resp = fetch(f'{API}/panic/history/', token=free_token)
assert_status("GET /api/panic/history/ (free)", st, 200)
if isinstance(resp, list):
    ok(f"Historial de panico: {len(resp)} evento(s)")

# ──────────────────────────────────────────────────────────────────────────────
# 9. Login usuario Premium
# ──────────────────────────────────────────────────────────────────────────────
section("9. Login de Usuario Premium")

if PROD_MODE:
    # En producción creamos el usuario premium vía register y luego lo upgradea admin
    st, resp = fetch(f'{AUTH}/register/', data={
        "email": PREM_EMAIL,
        "username": PREM_USERNAME,
        "phone_number": "+591 72222222",
        "password": PREM_PASS
    }, method='POST')
    prem_id = resp.get('user', {}).get('id') if isinstance(resp, dict) else None
    if prem_id:
        # El admin lo sube a premium
        fetch(f'{API}/users/{prem_id}/', data={"tier": "premium"}, token=admin_token, method='PATCH')
        ok(f"Usuario premium creado y actualizado a tier=premium vía admin")

prem_token = login(PREM_USERNAME, PREM_PASS)
if prem_token:
    ok(f"Login premium con username '{PREM_USERNAME}'")
else:
    fail(f"Login premium con username '{PREM_USERNAME}'")
    sys.exit(1)

prem_token_email = login(PREM_EMAIL, PREM_PASS)
if prem_token_email:
    ok(f"Login premium con email '{PREM_EMAIL}'")
else:
    fail(f"Login premium con email '{PREM_EMAIL}'")

# ──────────────────────────────────────────────────────────────────────────────
# 10. Contactos usuario Premium (límite 10)
# ──────────────────────────────────────────────────────────────────────────────
section("10. Lista de Contactos - Usuario Premium (max 10)")

prem_contact_ids = []

for i in range(1, 11):
    st, resp = fetch(f'{API}/contacts/', data={
        "name": f"Contacto Premium {i}",
        "phone_number": f"+591 7200000{i:02d}",
        "priority": i
    }, token=prem_token, method='POST')
    assert_status(f"CREATE contacto {i}/10 (premium)", st, 201)
    if isinstance(resp, dict) and resp.get('id'):
        prem_contact_ids.append(resp['id'])

st, resp = fetch(f'{API}/contacts/', data={
    "name": "Contacto Extra Premium",
    "phone_number": "+591 79999998",
    "priority": 11
}, token=prem_token, method='POST')
if st == 400:
    ok(f"Contacto 11 RECHAZADO correctamente (HTTP 400) - limite premium alcanzado")
    if isinstance(resp, dict):
        print(f"    Mensaje de error: {resp}")
else:
    fail(f"Contacto 11 debia ser rechazado (HTTP 400), obtenido HTTP {st}")

st, resp = fetch(f'{API}/contacts/', token=prem_token)
assert_status("READ ALL contacts (premium)", st, 200)
if isinstance(resp, list):
    ok(f"Total contactos del premium = {len(resp)} (esperado 10)") if len(resp) == 10 else fail(f"Total contactos = {len(resp)} (esperado 10)")

# ──────────────────────────────────────────────────────────────────────────────
# 11. Modo Pánico - Usuario Premium
# ──────────────────────────────────────────────────────────────────────────────
section("11. Modo Panico - Usuario Premium")

st, resp = fetch(f'{API}/panic/activate/', data={
    "latitude": "10.491016",
    "longitude": "-66.872467"
}, token=prem_token, method='POST')
assert_status("POST /api/panic/activate/ (premium)", st, 201)

if isinstance(resp, dict):
    event_data = resp.get('event', {})
    logs = resp.get('simulated_logs', [])
    ok(f"Evento creado: id={event_data.get('id')} status={event_data.get('status')}")
    ok(f"Alertas simuladas a {len(logs)} contacto(s) en orden de prioridad")
    for log in logs:
        print(f"    LOG: {log}")

st, resp = fetch(f'{API}/panic/history/', token=prem_token)
assert_status("GET /api/panic/history/ (premium)", st, 200)
if isinstance(resp, list):
    ok(f"Historial de panico premium: {len(resp)} evento(s)")

# ──────────────────────────────────────────────────────────────────────────────
# Resumen Final
# ──────────────────────────────────────────────────────────────────────────────
total = PASS_COUNT + FAIL_COUNT
print(f"\n{BOLD}{'='*60}{RESET}")
print(f"{BOLD}  RESULTADO FINAL  [{('PRODUCCIÓN' if PROD_MODE else 'LOCAL')}]{RESET}")
print(f"{'='*60}")
print(f"  {GREEN}✅ Pasadas : {PASS_COUNT}/{total}{RESET}")
if FAIL_COUNT > 0:
    print(f"  {RED}❌ Fallidas: {FAIL_COUNT}/{total}{RESET}")
else:
    print(f"  {GREEN}   Sin fallos 🎉{RESET}")
print(f"{'='*60}\n")
