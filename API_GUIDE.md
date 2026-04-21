# Guía Rápida de la API - Para Frontend

¡Hola! Esta guía documenta todos los endpoints de nuestra API, sus usos, qué datos enviar (payloads), qué datos nos devuelve la respuesta, y las reglas o restricciones (como los permisos requeridos).

La API está construida con Django REST Framework y utiliza **JSON Web Tokens (JWT)** para la autenticación en casi todos los endpoints (excepto los de Login y Registro).

---

## 🔑 1. Autenticación (`/api/auth/`)

**¡Importante!** Los endpoints de esta sección son accesibles públicamente (no requieren token) ya que su propósito es precisamente generarlos o crear cuentas.

### 🔹 1.1 Iniciar Sesión (Login)
- **Ruta:** `POST /api/auth/login/`
- **Uso:** Autenticar a un usuario existente. Permite usar tanto el nombre de usuario (`username`) como el correo (`email`) en el campo `username`.
- **Payload esperado:**
  ```json
  {
    "username": "tucorreo@o_tu_usuario",
    "password": "tu_password123"
  }
  ```
- **Respuesta (200 OK):**
  Devuelve el usuario logueado junto a sus tokens de acceso. **Debes guardar guardarlas** (por ejemplo en LocalStorage o en cookies seguras) para usar el `access` en los demás endpoints de la API.
  ```json
  {
    "user": { "id": 1, "email": "usuario@email.com", "username": "miusuario" },
    "access": "eyJhbGciOi...",
    "refresh": "eyJhbGciOi..."
  }
  ```
- **Errores comunes:** `401 Unauthorized` (credenciales inválidas), `403 Forbidden` (cuenta inactiva).

### 🔹 1.2 Registro de Usuario
- **Ruta:** `POST /api/auth/register/`
- **Uso:** Crea una nueva cuenta de usuario. ¡Ojo! Todo usuario nuevo se crea por defecto con el nivel o tier `"free"`.
- **Payload esperado:**
  ```json
  {
    "email": "nuevo@email.com",
    "username": "nuevousuario",
    "password": "passwordSeguro123",
    "phone_number": "+580000000" // Opcional
  }
  ```
- **Respuesta (201 Created):** Al registrar se hace "auto-login" y ya te devuelve los tokens de acceso listos para usar además del usuario creado.
- **Errores:** `400 Bad Request` si el correo o usuario ya existen.

### 🔹 1.3 Login con Google
- **Ruta:** `POST /api/auth/google-login/`
- **Uso:** Inicia sesión (o crea la cuenta si es nuevo) utilizando el botón de Google.
- **Payload esperado:** Necesitas enviar el token de ID de Google que te devuelve la librería de Google en el frontend (Ej. `@react-oauth/google`).
  ```json
  {
    "id_token": "token_proveniente_de_google"
  }
  ```
- **Respuesta:** Devuelve `user`, `access`, `refresh` y una bandera `is_new` (booleano) para que desde el front sepas si es la primera vez que inicia sesión o no.

### 🔹 1.4 Refrescar Token
- **Ruta:** `POST /api/auth/token/refresh/`
- **Uso:** El token `access` expira cada cierto tiempo por seguridad. Envía el token `refresh` a este endpoint para obtener uno nuevo.

---

## 🚨 2. Botón de Pánico (`/api/panic/`)

Todos los endpoints aquí requieren que envíes en tus Cabeceras/Headers HTTP tu token JWT:
`Authorization: Bearer <tu_access_token>`

### 🔹 2.1 Activar Alerta (Panic Button)
- **Ruta:** `POST /api/panic/activate/`
- **Uso:** Se llama cuando el usuario oprime el botón central de pánico en la App/Web. Registrará una alerta y simulará el envío de mensajes a sus contactos de emergencia por orden de prioridad.
- **Payload esperado:** *(Opcional)* Si puedes acceder al GPS del dispositivo, envíalo. Si no tienes permisos de ubicación, puedes mandar un JSON vacío `{}`.
  ```json
  {
    "latitude": 10.480600,
    "longitude": -66.903600
  }
  ```
- **Respuesta (201 Created):** Se devuelve la confirmación, detalles pánico registrado y simulaciones de los SMS.

### 🔹 2.2 Historial de Pánico
- **Ruta:** `GET /api/panic/history/`
- **Uso:** Devuelve la lista, ordenada de lo más reciente a más viejo, de las veces que este usuario específico activó el modo pánico. Totalmente confidencial (`IsAuthenticated` y fitrado por el propio usuario).

---

## 🫂 3. Contactos de Emergencia (`/api/contacts/`)

Este es un endpoint **CRUD** estándar. **Restricción importante:** 
Los usuarios `"free"` **solo pueden tener hasta 3 asociados**, mientras que los `"premium"` tienen límite de **10**. 
*(Requiere header con token: `Authorization: Bearer <token>`)*

- **Traer mi lista de contactos (`GET /api/contacts/`)**
  Devuelve un Array/Lista de la libreta del propio usuario, vienen ordenados según su prioridad (el número de prioriidad más bajo va de primero).
  
- **Agregar contacto (`POST /api/contacts/`)**
  Añades a alguien a tu red de seguridad. Si el usuario topa su límite (ej. es *free* y ya tiene 3), la API te regresará un estado **`400 Bad Request`**.
  
- **Modificar un contacto (`PATCH /api/contacts/{id}/`)**
  Ideal para poder cambiar un número o cambiar su orden de `prioridad` en la libreta.
  
- **Eliminar Contacto (`DELETE /api/contacts/{id}/`)**

---

## 🛡️ 4. Sección de Administradores (Dashboard Interno)

Estos endoints sirven de CRUD nativo y operan usando el permiso estricto `IsAdminUser`. ¡Si el usuario en el navegador **no es** administrador, devolverá error 403 o 401! Úsalas si vas a programar el Panel de Administración.

- **Manejo de Usuarios:** `/api/users/` (GET, POST, PATCH, DELETE). Para ver toda la lista del sistema.
- **Manejo de Roles:** `/api/roles/` (GET, POST, PATCH, DELETE).

---

> [!TIP]
> 📖 **Cómo Explorar a Fondo la API (Swagger)**
> La interfaz visual completa en vivo de todos estos endpoints la tienes en la ruta **`/api/docs/swagger/`**. ¡Pruébala en el entorno local arrancando el servidor y yendo en el navegador a `http://localhost:8000/api/docs/swagger/`! 
> Allí podrás probar enviar los requests desde una interfaz amigable.
