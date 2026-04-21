import os
import django
import json
import urllib.request
from urllib.error import HTTPError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# ==========================================
# 1. SETUP & AUTHENTICATION
# ==========================================
print("Setting up users for security testing...")
admin_user, _ = User.objects.get_or_create(email='admin@admin.com')
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.set_password('12345678')
admin_user.save()

normal_user, _ = User.objects.get_or_create(email='normal@test.com')
normal_user.is_staff = False
normal_user.is_superuser = False
normal_user.set_password('userpass123')
normal_user.save()

api_url = 'http://127.0.0.1:8000/api'
auth_url = 'http://127.0.0.1:8000/api/auth'

def fetch(url, data=None, token=None, method='GET'):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req_data = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode()
            return response.status, json.loads(content) if content else None
    except HTTPError as e:
        content = e.read().decode()
        try:
            return e.code, json.loads(content)
        except json.JSONDecodeError:
            return e.code, content

print("\nFetching tokens...")
status, admin_login = fetch(f"{auth_url}/login/", data={'email': 'admin@admin.com', 'password': '12345678'}, method='POST')
admin_token = admin_login.get('access')

status, normal_login = fetch(f"{auth_url}/login/", data={'email': 'normal@test.com', 'password': 'userpass123'}, method='POST')
normal_token = normal_login.get('access')

# ==========================================
# 2. RUNNING SECURITY TESTS
# ==========================================
tests_passed = 0
tests_failed = 0

def assert_status(expected, actual, summary):
    global tests_passed, tests_failed
    if expected == actual:
        print(f"[PASSED] | Expected {expected} | {summary}")
        tests_passed += 1
    else:
        print(f"[FAILED] | Expected {expected}, got {actual} | {summary}")
        tests_failed += 1

print("\n--- TEST: UNAUTHENTICATED ACCESS (Expected 401 Unauthorized) ---")

status, resp = fetch(f"{api_url}/users/")
assert_status(401, status, "Access /users/ without any token")

status, resp = fetch(f"{api_url}/roles/")
assert_status(401, status, "Access /roles/ without any token")

status, resp = fetch(f"{api_url}/users/", method='POST', data={"email": "hacker@hacker.com"})
assert_status(401, status, "Try creating user without token")

print("\n--- TEST: INVALID/FORGED TOKENS (Expected 401 Unauthorized) ---")

status, resp = fetch(f"{api_url}/users/", token="Bearer fake.jwt.token123")
assert_status(401, status, "Access /users/ with forged Bearer token")

status, resp = fetch(f"{api_url}/roles/", token="random_string_not_token")
assert_status(401, status, "Access /roles/ with completely invalid token string")

print("\n--- TEST: UNAUTHORIZED ROLE - NORMAL USER (Expected 403 Forbidden) ---")

status, resp = fetch(f"{api_url}/users/", token=normal_token)
assert_status(403, status, "Normal user tries to GET users list")

status, resp = fetch(f"{api_url}/roles/", token=normal_token)
assert_status(403, status, "Normal user tries to GET roles list")

status, resp = fetch(f"{api_url}/roles/", data={"name": "HackerRole"}, token=normal_token, method='POST')
assert_status(403, status, "Normal user tries to POST (create) a role")

status, resp = fetch(f"{api_url}/users/{admin_user.id}/", token=normal_token, method='DELETE')
assert_status(403, status, "Normal user tries to DELETE the admin user")

print("\n--- TEST: AUTHORIZED ROLE - ADMIN (Expected 20X Success) ---")

status, resp = fetch(f"{api_url}/users/", token=admin_token)
assert_status(200, status, "Admin user tries to GET users list")

status, resp = fetch(f"{api_url}/roles/", token=admin_token)
assert_status(200, status, "Admin user tries to GET roles list")

print("\n==========================================")
print(f"SECURITY AUDIT COMPLETE: {tests_passed} Passed / {tests_failed} Failed")
print("==========================================")
