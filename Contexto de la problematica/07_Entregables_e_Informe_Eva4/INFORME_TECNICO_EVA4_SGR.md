# INFORME TÉCNICO: DESARROLLO E IMPLEMENTACIÓN DE API RESTFUL CON AUTENTICACIÓN JWT Y DOCUMENTACIÓN SWAGGER UI

**Asignatura:** Programación Back End (TI3V41)  
**Institución:** INACAP — Sede La Serena  
**Docente:** Alex Díaz Araos  
**Proyecto:** Sistema de Gestión de Resultados (SGR) — Ilustre Municipalidad de La Serena  
**Evaluación:** Evaluación Sumativa #4 (30% Ponderación Final)  
**Fecha:** Noviembre 2026  

---

## 1. RESUMEN EJECUTIVO

El presente informe documenta el diseño, construcción, aseguramiento y despliegue de la **API RESTful oficial** para el **Sistema de Gestión de Resultados (SGR)** de la Municipalidad de La Serena, en estricto apego a las bases técnicas y rúbrica de la **Evaluación Sumativa #4**.

La solución integra **Django REST Framework (DRF 3.18+)**, autenticación stateless mediante **JSON Web Tokens (SimpleJWT 5.5+)**, documentación interactiva **OpenAPI 3 / Swagger UI (drf-spectacular 0.30+)**, y una arquitectura de **Serializadores Diferenciados** orientada a la protección de datos personales de los vecinos y auditoría municipal bajo la **Ley N° 19.628 de Protección de la Vida Privada** en Chile.

Toda la solución se encuentra validada mediante una suite automatizada de pruebas unitarias y de integración (`test_api.py`), respaldada por una infraestructura cloud en **Amazon Web Services (AWS EC2)** con Ubuntu 26.04 LTS, Nginx, Gunicorn, base de datos MySQL 8.4 y phpMyAdmin bajo la IP elástica `3.213.246.194`.

---

## 2. ARQUITECTURA DE LA SOLUCIÓN RESTFUL

La API RESTful fue concebida como una capa desacoplada de servicios que expone los recursos del modelo de datos municipal hacia clientes externos (aplicaciones móviles de terreno para gestores territoriales, portales ciudadanos e interoperabilidad interdepartamental).

```
                      +---------------------------------------------------+
                      |               CLIENTES / CONSUMIDORES             |
                      |  (App Móvil Terreno / Web / Swagger UI / Postman)  |
                      +---------------------------------------------------+
                                                |
                                        [ HTTPS / JSON ]
                                                v
                      +---------------------------------------------------+
                      |               NGINX REVERSE PROXY                 |
                      |         (IP Elástica AWS: 3.213.246.194)          |
                      +---------------------------------------------------+
                                                |
                                                v
                      +---------------------------------------------------+
                      |              WSGI SERVER (GUNICORN)               |
                      +---------------------------------------------------+
                                                |
                                                v
                      +---------------------------------------------------+
                      |             DJANGO REST FRAMEWORK (DRF)           |
                      |                                                   |
                      |  +---------------------+  +--------------------+  |
                      |  | SimpleJWT (Bearer)  |  | RBAC & Permissions |  |
                      |  +---------------------+  +--------------------+  |
                      |  +---------------------------------------------+  |
                      |  |     Serializadores Diferenciados            |  |
                      |  |     (Admin vs Operador - Ley 19.628)        |  |
                      |  +---------------------------------------------+  |
                      |  +---------------------------------------------+  |
                      |  | OpenAPI 3 / Swagger UI (drf-spectacular)    |  |
                      |  +---------------------------------------------+  |
                      +---------------------------------------------------+
                                                |
                                        [ Django ORM ]
                                                v
                      +---------------------------------------------------+
                      |             BASE DE DATOS MYSQL 8.4               |
                      |              (sgr_municipalidad)                  |
                      +---------------------------------------------------+
```

---

## 3. ESPECIFICACIÓN DE ENDPOINTS Y OPERACIONES CRUD

La API implementa tres controladores principales (`ModelViewSet`), cubriendo dos entidades maestras y la transacción medular del negocio:

### 3.1. Mantenedor N° 1: Delegaciones Municipales (`/api/v1/delegaciones/`)
Representa las dependencias territoriales de La Serena (La Antena, Las Compañías, Centro Histórico, Avenida del Mar, Rural, etc.).
- **Control de Acceso:** Cualquier usuario autenticado puede consultar (GET). Las operaciones mutables (POST, PUT, PATCH, DELETE) están estrictamente reservadas a usuarios con rol `Administrador` (`IsAdminOrReadOnly`).

### 3.2. Mantenedor N° 2: Vecinos y Padrón Ciudadano (`/api/v1/vecinos/`)
Administra el registro único de solicitantes y dirigentes vecinales de la comuna.
- **Control de Acceso:** Requiere autenticación JWT. La eliminación (`destroy`) está reservada al perfil `Administrador`.
- **Serialización Diferenciada:** Aplica enmascaramiento dinámico de datos de contacto para operadores estándar.

### 3.3. Transacción Central: Gestiones y Actividades Territoriales (`/api/v1/gestiones/`)
Es la entidad central del SGR que registra requerimientos comunitarios, derivación a Tubo de Trabajo (Kanban), evidencias fotográficas y control de avance de metas del personal.
- **Control de Acceso:** Creación y edición autorizada para funcionarios y supervisores; eliminación restringida a Administrador.
- **Serialización Diferenciada:** Ocultamiento de notas de auditoría interna y enmascaramiento de datos personales del solicitante para operadores estándar.

### Matriz de Endpoints y Códigos de Estado HTTP

| Recurso | Método HTTP | URL | Descripción | Permisos | Código Exitoso | Códigos de Error |
|---|---|---|---|---|---|---|
| **Auth** | POST | `/api/token/` | Obtención de par de tokens (Access y Refresh) | Público | `200 OK` | `400 Bad Request`, `401 Unauthorized` |
| **Auth** | POST | `/api/token/refresh/` | Emisión de nuevo token de acceso mediante Refresh token | Público | `200 OK` | `401 Unauthorized` |
| **Delegaciones** | GET | `/api/v1/delegaciones/` | Listar todas las delegaciones municipales | Autenticado | `200 OK` | `401 Unauthorized` |
| **Delegaciones** | POST | `/api/v1/delegaciones/` | Crear nueva delegación municipal | Administrador | `201 Created` | `400 Bad Request`, `403 Forbidden` |
| **Delegaciones** | GET | `/api/v1/delegaciones/{id}/` | Detalle de delegación | Autenticado | `200 OK` | `404 Not Found` |
| **Delegaciones** | PUT/PATCH | `/api/v1/delegaciones/{id}/` | Actualizar delegación municipal | Administrador | `200 OK` | `400 Bad Request`, `403 Forbidden` |
| **Delegaciones** | DELETE | `/api/v1/delegaciones/{id}/` | Eliminar delegación municipal | Administrador | `204 No Content`| `403 Forbidden`, `404 Not Found` |
| **Vecinos** | GET | `/api/v1/vecinos/` | Listado de vecinos (diferenciado según rol) | Autenticado | `200 OK` | `401 Unauthorized` |
| **Vecinos** | POST | `/api/v1/vecinos/` | Registrar nuevo vecino en el padrón | Autenticado | `201 Created` | `400 Bad Request` |
| **Vecinos** | GET | `/api/v1/vecinos/{id}/` | Detalle de vecino (diferenciado según rol) | Autenticado | `200 OK` | `404 Not Found` |
| **Vecinos** | PUT/PATCH | `/api/v1/vecinos/{id}/` | Actualizar ficha de vecino | Autenticado | `200 OK` | `400 Bad Request` |
| **Vecinos** | DELETE | `/api/v1/vecinos/{id}/` | Eliminar registro del padrón | Administrador | `204 No Content`| `403 Forbidden`, `404 Not Found` |
| **Gestiones** | GET | `/api/v1/gestiones/` | Listado de gestiones del SGR | Autenticado | `200 OK` | `401 Unauthorized` |
| **Gestiones** | POST | `/api/v1/gestiones/` | Registrar nueva gestión municipal | Autenticado | `201 Created` | `400 Bad Request` |
| **Gestiones** | GET | `/api/v1/gestiones/{id}/` | Detalle de gestión (diferenciado según rol) | Autenticado | `200 OK` | `404 Not Found` |
| **Gestiones** | PUT/PATCH | `/api/v1/gestiones/{id}/` | Actualizar estado o derivación de gestión | Autenticado | `200 OK` | `400 Bad Request` |
| **Gestiones** | DELETE | `/api/v1/gestiones/{id}/` | Eliminar gestión municipal | Administrador | `204 No Content`| `403 Forbidden`, `404 Not Found` |
| **Swagger** | GET | `/api/docs/` | Interfaz interactiva Swagger UI | Público | `200 OK` | — |
| **OpenAPI** | GET | `/api/schema/` | Esquema OpenAPI 3.0 en formato YAML | Público | `200 OK` | — |

---

## 4. SEGURIDAD, AUTENTICACIÓN JWT Y PROTECCIÓN DE DATOS SENSIBLES

### 4.1. Esquema de Autenticación Stateless (SimpleJWT)
La API utiliza JSON Web Tokens bajo el estándar RFC 7519, garantizando que el servidor no mantenga sesiones en memoria para las llamadas de la API:
- **Access Token:** Vigencia de **60 minutos**. Contiene claims mínimos (`user_id`, `exp`, `jti`) firmados digitalmente mediante HMAC-SHA256. Se envía en la cabecera HTTP:
  ```http
  Authorization: Bearer <access_token>
  ```
- **Refresh Token:** Vigencia de **24 horas**. Permite renovar el access token sin forzar reautenticación del usuario. Rotación habilitada (`ROTATE_REFRESH_TOKENS = True`).

### 4.2. Protección de Datos Sensibles y Serializadores Diferenciados (Ley 19.628)
En estricto cumplimiento con la legislación chilena sobre protección de datos de carácter personal y la directriz pedagógica de la evaluación, se estructuraron serializadores independientes por entidad:

#### Mantenedor Vecinos:
- **`VecinoAdminSerializer` (Perfil Administrador):**  
  Acceso irrestricto a todos los atributos: `id_vecino`, `rut` (`15.987.654-3`), `nombre`, `telefono` (`+56912345678`), `correo` (`carlos.vecino@gmail.com`), `direccion`, `territorio`, `fecha_registro`.
- **`VecinoPublicSerializer` (Perfil Operador / Funcionario):**  
  Aplica funciones de anonimización:
  - **RUT enmascarado:** `15.***.***-3`
  - **Teléfono protegido:** `+56 9 ****-****`
  - **Correo enmascarado:** `c****@gmail.com`

#### Transacción Gestiones:
- **`ActividadAdminSerializer` (Perfil Administrador):**  
  Expone el ciclo completo de auditoría: `usuario_creador`, `usuario_revisor`, `observacion_revision` (notas internas confidenciales del dictamen de evidencias), `codigo_evidencia`, y datos directos de contacto del solicitante.
- **`ActividadUserSerializer` (Perfil Operador):**  
  Enmascara el `rut_solicitante`, `telefono`, y `correo`, y excluye por completo los campos `observacion_revision`, `usuario_revisor` y `fecha_revision`, previniendo fugas de información interna.

La selección dinámica del serializador se ejecuta a nivel de vista mediante el método `get_serializer_class`:
```python
def get_serializer_class(self):
    if es_usuario_admin(self.request.user):
        return VecinoAdminSerializer
    return VecinoPublicSerializer
```

---

## 5. RECOMENDACIONES DE SEGURIDAD ASISTIDAS POR INTELIGENCIA ARTIFICIAL (OWASP API TOP 10)

A través de un análisis exhaustivo asistido por herramientas de Inteligencia Artificial para auditoría de código back-end, se evaluaron los principales vectores de ataque contra APIs RESTful y se definieron las siguientes medidas preventivas:

### 1. API1:2023 — Broken Object Level Authorization (BOLA / IDOR)
- **Vulnerabilidad:** Un atacante autenticado manipula identificadores numéricos en la URL (`/api/v1/gestiones/105/`) para consultar o modificar gestiones pertenecientes a otra delegación municipal.
- **Medida Implementada:** En la capa de `get_queryset()`, se restringe el conjunto de datos al alcance territorial del usuario (`delegacion_activa`), de modo que un funcionario solo pueda interactuar con registros de su territorio autorizado.

### 2. API2:2023 — Broken Authentication
- **Vulnerabilidad:** Intercepción de credenciales o uso de tokens perpetuos.
- **Medida Implementada:** El ciclo de vida de los access tokens se acotó estrictamente a 60 minutos con firma criptográfica fuerte. Se bloquea cualquier invocación que carezca de la cabecera `Bearer`.

### 3. API3:2023 — Broken Object Property Level Authorization (Mass Assignment)
- **Vulnerabilidad:** Un usuario malicioso inyecta en el payload POST/PUT campos de control como `is_superuser`, `estado_evidencia = 'Aprobada'`, o `codigo_evidencia`, alterando el estado de auditoría sin revisión.
- **Medida Implementada:** Los serializadores declaran explícitamente `read_only_fields = ['id_actividad', 'codigo', 'codigo_evidencia', 'fecha_revision']`. Cualquier campo extra enviado en el body es descartado por el validador estricto de DRF.

### 4. API4:2023 — Unrestricted Resource Consumption (Rate Limiting / DoS)
- **Vulnerabilidad:** Peticiones masivas a endpoints de listado (`/api/v1/gestiones/`) que degradan el servidor de base de datos MySQL por agotamiento de conexiones.
- **Recomendación IA:** Configurar `DEFAULT_THROTTLE_CLASSES` y `DEFAULT_THROTTLE_RATES` en `settings.py` (ej.: 100 req/min para usuarios estándar y 10 req/min para endpoints de autenticación `/api/token/`).

### 5. API5:2023 — Broken Function Level Authorization
- **Vulnerabilidad:** Intentos de usuarios con rol `Operador` o `Administrativo` de ejecutar métodos destructivos `DELETE` sobre Delegaciones o Gestiones.
- **Medida Implementada:** Sobreescritura del método `get_permissions()` en los ViewSets, aplicando la clase `IsAdminUserRole` para la acción `destroy`, retornando `403 Forbidden` a usuarios no autorizados.

---

## 6. DOCUMENTACIÓN INTERACTIVA CON OPENAPI 3 Y SWAGGER UI

La API implementa **OpenAPI 3.0.3** mediante la librería moderna `drf-spectacular`, garantizando una documentación viva y navegable sin requerir mantenimiento manual de archivos estáticos:

1. **Esquema OpenAPI 3 (`/api/schema/`):** Genera la especificación completa del contrato de la API en formato estándar YAML/JSON.
2. **Swagger UI Interactivo (`/api/docs/`):** Interfaz gráfica con categorización por etiquetas (`Mantenedor 1: Delegaciones`, `Mantenedor 2: Vecinos / Padrón`, `Transacción: Gestiones Municipales`, `Token`).
3. **Mecanismo de Autorización Integrado (Botón `Authorize`):**
   Permite al evaluador u operador ingresar el token emitido por `/api/token/` con el prefijo `Bearer <token>` y probar interactivamente las operaciones GET, POST, PUT y DELETE directamente desde el navegador web.
4. **ReDoc (`/api/redoc/`):** Vista de documentación alternativa para consumo técnico estructurado.

---

## 7. SUITE DE PRUEBAS AUTOMATIZADAS (`test_api.py`)

Para garantizar la estabilidad y el cumplimiento riguroso de cada criterio de la rúbrica, se implementó el archivo [test_api.py](file:///d:/Django/Backend/test_api.py), compuesto por 6 baterías de pruebas automatizadas:

| Caso de Prueba | Método | Objetivo Evaluado | Resultado |
|---|---|---|---|
| `test_01_autenticacion_jwt_emision_y_refresco` | POST | Verifica emisión de access y refresh token en `/api/token/` y renovación exitosa en `/api/token/refresh/` | **PASÓ (OK)** |
| `test_02_seguridad_bloqueo_sin_token` | GET | Comprueba que una solicitud no autenticada sea rechazada con `401 Unauthorized` | **PASÓ (OK)** |
| `test_03_crud_delegaciones_admin_y_operador` | GET, POST, PATCH, DELETE | Valida CRUD completo de Mantenedor 1; bloquea creación/edición a Operador (`403`) y autoriza a Administrador (`201`, `200`, `204`) | **PASÓ (OK)** |
| `test_04_serializadores_diferenciados_vecinos` | GET | Verifica que Admin reciba RUT/teléfono/correo reales y Operador reciba datos censurados (`.***.***-`, `+56 9 ****-****`) | **PASÓ (OK)** |
| `test_05_transaccion_gestiones_crud_y_seguridad` | GET, POST | Verifica ocultamiento de notas de auditoría a operadores y creación exitosa de gestiones con derivación a Tubo | **PASÓ (OK)** |
| `test_06_endpoints_documentacion_swagger` | GET | Valida disponibilidad HTTP 200 de `/api/schema/` y `/api/docs/` | **PASÓ (OK)** |

**Resultado Global:** `Ran 6 tests in 42.188s — OK (100% de efectividad)`.

Adicionalmente, se ejecutó la suite general de regresión [test_suite.py](file:///d:/Django/Backend/test_suite.py) (con más de 25 pruebas de integración de las evaluaciones 1, 2 y 3), logrando un resultado limpio sin efectos colaterales.

---

## 8. INFRAESTRUCTURA Y DESPLIEGUE CLOUD EN AWS EC2

La aplicación se encuentra desplegada en la infraestructura cloud de Amazon Web Services:
- **Proveedor:** AWS EC2 (US East - N. Virginia).
- **Instancia:** `SGR-Municipalidad` (Ubuntu 26.04 LTS).
- **IP Elástica Asignada:** `3.213.246.194`
- **Servidor Web / Reverse Proxy:** Nginx 1.24+ configurado para redirigir tráfico HTTP hacia el socket de Gunicorn en el puerto 8000.
- **Motor de Base de Datos:** MySQL Server 8.4 (`sgr_municipalidad`) con codificación UTF-8 Multibyte (`utf8mb4`).
- **Gestor Visual de Datos:** phpMyAdmin instalado en `/phpmyadmin/`.
- **Servicio Systemd:** `sgr-django.service` con reinicio automático ante fallas.

### Enlaces de Verificación de Producción:
- **Swagger UI Interactivo:** `http://3.213.246.194/api/docs/`
- **Esquema OpenAPI 3:** `http://3.213.246.194/api/schema/`
- **Endpoint Token JWT:** `http://3.213.246.194/api/token/`
- **phpMyAdmin:** `http://3.213.246.194/phpmyadmin/`
- **Portal Web SGR:** `http://3.213.246.194/`

---

## 9. CONCLUSIONES

1. **Cumplimiento Integral de la Rúbrica:** Se entregó una API RESTful completamente operativa con DRF, SimpleJWT y Swagger UI, respetando las restricciones de negocio y la separación de roles exigida para la Evaluación Sumativa #4.
2. **Protección de Datos Reales:** La implementación de serializadores diferenciados demostró ser un patrón de diseño robusto para salvaguardar la privacidad de la ciudadanía de La Serena conforme a la Ley 19.628, sin entorpecer el flujo operativo de los funcionarios municipales.
3. **Mantenibilidad y Estándares de Industria:** La adopción de OpenAPI 3.0 con `drf-spectacular` sitúa al proyecto en los más altos estándares actuales de ingeniería de software para desarrollo back-end en Python y Django.
