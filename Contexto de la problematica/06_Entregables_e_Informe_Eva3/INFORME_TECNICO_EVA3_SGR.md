# INFORME TÉCNICO Y DE DESPLIEGUE — EVALUACIÓN SUMATIVA N°3 (30%)
## SISTEMA DE GESTIÓN DE RESULTADOS (SGR) — ILUSTRE MUNICIPALIDAD DE LA SERENA

---

### IDENTIFICACIÓN DEL PROYECTO Y EQUIPO

* **Institución:** INACAP — Sede La Serena
* **Área Académica:** Informática, Ciberseguridad y Telecomunicaciones
* **Carrera:** Ingeniería en Informática
* **Asignatura:** Programación Back End (TI3041)
* **Docente Guía:** Mariavictoria Freites Ayala
* **Integrantes del Equipo:**
  * **Emanuel Román Serón**
  * **Benjamín Antipa**
  * **Álvaro Obregón**
* **Fecha de Entrega:** Noviembre de 2026

---

## 1. INTRODUCCIÓN Y CONTEXTO DEL SISTEMA

### 1.1 Problemática Municipal Abordada
La Ilustre Municipalidad de La Serena cuenta con diversas delegaciones territoriales (La Serena Centro, Las Compañías, La Pampa, Avenida del Mar, entre otras) cuyo propósito es acercar los servicios municipales a los vecinos. Históricamente, la atención de requerimientos, la gestión de casos sociales y la coordinación intersectorial se registraban en planillas locales y cuadernos físicos, provocando:
* Descoordinación entre las unidades territoriales y las jefaturas comunales.
* Pérdida de trazabilidad en los compromisos asumidos con los ciudadanos.
* Imposibilidad de medir en tiempo real el cumplimiento de metas institucionales.
* Vulnerabilidades de seguridad por falta de control de perfiles y accesos.

El **Sistema de Gestión de Resultados (SGR)** resuelve esta problemática centralizando en una plataforma web relacional y moderna la recepción de atenciones ciudadanas, el seguimiento de compromisos mediante un tablero Kanban y la reportabilidad ejecutiva.

### 1.2 Objetivos de la Evaluación Sumativa #3
Esta tercera etapa del proyecto consolida la arquitectura back end del sistema con los siguientes hitos técnicos:
1. **Seguridad y Control de Acceso Multi-Perfil:** Implementación de tres niveles de acceso claramente diferenciados (`Administrador`, `Supervisor`, `Administrativo`) basados en los modelos nativos de grupos y permisos de Django (`django.contrib.auth.models.Group`).
2. **Recuperación Segura de Contraseñas por Correo Electrónico:** Integración de un servicio SMTP real para el envío de códigos de seguridad de 6 dígitos y enlaces con tokens criptográficos de un solo uso.
3. **Dashboards Personalizados por Perfil y Cargo:** Interfaces de inicio dinámicas construidas en Django Templates que adaptan sus herramientas según el nivel de autorización y el cargo institucional del funcionario.
4. **Administración Exclusiva mediante Django Templates:** Eliminación de la dependencia de Django Admin durante la operación del sistema; el 100% de los mantenedores CRUD y transacciones se operan mediante vistas y plantillas propias.
5. **Transacción Operacional Integrada:** Módulo de Atención Ciudadana con generación correlativa de folios, selectores dependientes en cascada y asociación automática de vecinos.
6. **Despliegue Continuo en AWS EC2:** Aplicación ejecutándose en una instancia Ubuntu Linux en la nube de Amazon Web Services, conectada a una base de datos MySQL relacional y respaldada en GitHub.

---

## 2. ARQUITECTURA DE SEGURIDAD, PERFILES Y CONTROL DE ACCESO

### 2.1 Modelo de Autorización: Grupos de Django (`Group` y `Permission`)
Para cumplir estrictamente con los estándares de seguridad de Django, se implementó una estructura de autorización basada en roles (RBAC) vinculada directamente con el sistema de autenticación nativo:

| Perfil / Grupo Django | Nivel de Acceso | Total Permisos | Alcance Funcional |
| :--- | :--- | :---: | :--- |
| **Administrador** | Acceso Total | 80 permisos | Acceso irrestricto a los 6 mantenedores CRUD, creación y edición de usuarios, asignación de grupos de Django, auditoría de transacciones y configuración comunal. |
| **Supervisor** | Permisos Intermedios | 41 permisos | Visualización de metas y semáforo SGR, monitoreo del tablero Kanban de compromisos, aprobación de atenciones y consulta de catálogos autorizados. Bloqueado de la gestión de usuarios y roles. |
| **Administrativo** | Permisos Mínimos | 14 permisos | Ingreso de atenciones ciudadanas en ventanilla, registro de gestiones en terreno y carga de evidencias fotográficas. Bloqueado de reportes gerenciales y mantenedores críticos. |

### 2.2 Diferenciación Adicional por Cargo Institucional
Dentro del nivel **Administrativo**, el sistema lee el cargo institucional (`PerfilUsuario.rol`) para adaptar de forma personalizada la interfaz de trabajo:
* **Funcionario Operador:** Enfocado en la recepción presencial en ventanilla y registro de requerimientos.
* **Funcionario Territorial:** Orientado a inspecciones en terreno, levantamiento vecinal y evidencias fotográficas.
* **Gestor Social:** Especializado en fichas sociales, visitas domiciliarias y derivaciones a redes de apoyo.
* **Funcionario DISERCO:** Coordinación de servicios comunitarios y resolución de contingencias urbanas.

### 2.3 Matriz de Restricciones Funcionales en Vistas

| Módulo / URL | Administrador | Supervisor | Administrativo | Comportamiento ante Acceso no Autorizado |
| :--- | :---: | :---: | :---: | :--- |
| `/mantenedores/usuarios/` | Permitido | Denegado | Denegado | Redirección con alerta de seguridad: *"Acceso restringido: Se requieren permisos de nivel Administrador"*. |
| `/mantenedores/roles/` | Permitido | Denegado | Denegado | Redirección con alerta de seguridad. |
| `/mantenedores/delegaciones/` | Total (CRUD) | Solo Lectura | Denegado | Bloqueo de acciones de creación, edición y eliminación. |
| `/resultados/` (Semáforo/Metas) | Permitido | Permitido | Denegado | Oculto en interfaz y protegido en vista. |
| `/atenciones/nueva/` | Permitido | Permitido | Permitido | Acceso autorizado para todos los perfiles activos. |

---

## 3. FLUJO DE RECUPERACIÓN DE CONTRASEÑA POR CORREO ELECTRÓNICO

### 3.1 Arquitectura del Flujo Seguro
El proceso de restablecimiento combina dos mecanismos de protección complementarios:
1. **Código numérico de 6 dígitos (PIN):** Enviado al buzón de correo del usuario, con vencimiento a los 15 minutos y límite estricto de 3 intentos fallidos para prevenir ataques de fuerza bruta.
2. **Token Criptográfico de un solo uso:** Generado mediante `default_token_generator` de Django (`HMAC-SHA256`) combinando la clave secreta, la contraseña actual y la fecha de expiración; se invalida de forma inmediata y automática al momento de cambiar la contraseña.

### 3.2 Diagrama de Secuencia del Proceso

```
Usuario                  Navegador Web                 Servidor Django                  Servidor SMTP (Gmail)
   |                           |                              |                                   |
   |--- 1. Clic "¿Olvidó?" --->|                              |                                   |
   |                           |--- 2. GET /recuperar/ ------>|                                   |
   |                           |<-- 3. Formulario Email ------|                                   |
   |--- 4. Ingresa Email ----->|                              |                                   |
   |                           |--- 5. POST /recuperar/ ----->|                                   |
   |                           |                              |-- 6. Genera Token + PIN 6 dígitos |
   |                           |                              |--- 7. Envía Correo Institucional->|
   |                           |                              |                                   |---> Correo a buzón
   |                           |<-- 8. Redirect /validar/ ----|                                   |
   |                           |<-- 9. Pantalla 6 casilleros -|                                   |
   |--- 10. Revisa Correo ---->|                              |                                   |
   |    (Obtiene el PIN)       |                              |                                   |
   |--- 11. Ingresa los 6 d. ->|                              |                                   |
   |                           |--- 12. POST /validar/ ------>|                                   |
   |                           |                              |-- 13. Valida vigencia e intentos  |
   |                           |<-- 14. Redirect /nueva-clave/|                                   |
   |--- 15. Escribe Clave ---->|                              |                                   |
   |                           |--- 16. POST /nueva-clave/ -->|                                   |
   |                           |                              |-- 17. set_password() + Invalida   |
   |                           |<-- 18. Redirect /login/ OK --|                                   |
```

### 3.3 Configuración de Infraestructura SMTP
* **Servidor de Correo:** Gmail SMTP (`smtp.gmail.com`).
* **Puerto y Protocolo:** Puerto `587` con cifrado TLS activo (`EMAIL_USE_TLS = True`).
* **Cuenta Emisora Institucional:** `emanuelromanseron@gmail.com` (mostrada como *"SGR Municipalidad de La Serena"*).
* **Seguridad de Credenciales:** La contraseña de aplicación de 16 caracteres se almacena exclusivamente en variables de entorno dentro del archivo `.env`, manteniéndose fuera del control de versiones mediante `.gitignore`.

---

## 4. BASE DE DATOS Y MODELADO RELACIONAL ORM

El sistema opera sobre una base de datos relacional normalizada en tercera forma normal (3NF), administrada integralmente mediante el ORM de Django:

### 4.1 Entidades Principales
1. **`User` (Django Core):** Autenticación, nombres, correo institucional y pertenencia a grupos (`Group`).
2. **`PerfilUsuario` (`organizacion`):** Extensión del usuario que almacena el `Rol` institucional, la delegación activa, teléfono y estado.
3. **`Rol` (`organizacion`):** Catálogo de cargos municipales con alcance territorial autorizado.
4. **`Delegacion` (`organizacion`):** Jurisdicciones territoriales municipales activas.
5. **`AtencionCiudadana` (`actividades`):** Registro de atenciones presenciales con folio correlativo único (`ATC-XXXXX`), fecha, solicitante, RUT y estado.
6. **`TipoAtencion` y `Subatencion` (`actividades`):** Clasificación jerárquica de atenciones con relación 1:N que alimenta los selectores en cascada.
7. **`Vecino` (`actividades`):** Registro histórico de ciudadanos identificados por RUT.
8. **`Compromiso` (`agenda`):** Tareas intersectoriales asociadas al tablero Kanban del Tubo de Trabajo.
9. **`Evidencia` (`actividades`):** Archivos adjuntos y registros fotográficos de respaldo.
10. **`ItemMeta` (`resultados`):** Indicadores y metas operacionales para el cálculo del semáforo institucional.

---

## 5. MANTENEDORES CRUD Y TRANSACCIÓN OPERACIONAL

### 5.1 Los 6 Mantenedores CRUD Implementados (100% Django Templates)
1. **Mantenedor de Delegaciones (`/mantenedores/delegaciones/`):** Alta, baja, edición y listado de delegaciones territoriales con exportación a Excel.
2. **Mantenedor de Roles (`/mantenedores/roles/`):** Administración de cargos municipales y alcances autorizados.
3. **Mantenedor de Usuarios (`/mantenedores/usuarios/`):** Creación de cuentas, asignación obligatoria de Grupos de Django (`Administrador`, `Supervisor`, `Administrativo`), activación/bloqueo de usuarios y exportación tabular.
4. **Mantenedor de Ítems y Metas (`/mantenedores/items/`):** Catálogo de indicadores institucionales ponderados.
5. **Mantenedor de Tipos de Atención (`/mantenedores/tipos-atencion/`):** Categorías macro de requerimientos vecinales.
6. **Mantenedor de Subatenciones (`/mantenedores/subatenciones/`):** Subcategorías específicas vinculadas a un Tipo de Atención.

### 5.2 Transacción Operacional: Atención Ciudadana
* **Folio Único Autoincremental:** El sistema calcula y asigna automáticamente folios correlativos protegidos contra colisiones (`ATC-00001`, `ATC-00002`, etc.).
* **Integración de Vecinos en Tiempo Real:** Al ingresar el RUT del vecino, el sistema busca en la base de datos y auto-completa los datos conocidos, o crea automáticamente el registro si es un nuevo solicitante.
* **Cascada Asíncrona (Tipo -> Subatención):** Al seleccionar un tipo de atención, el formulario consulta una API interna en `/api/subatenciones/?tipo_id=X` y actualiza dinámicamente las opciones sin recargar la página.

---

## 6. INFRAESTRUCTURA CLOUD Y CONTROL DE VERSIONES

### 6.1 Despliegue en AWS EC2
* **Instancia:** Amazon EC2 `t2.micro` corriendo Ubuntu 24.04 LTS.
* **Dirección IP Pública:** `3.229.11.31`
* **Servicio:** `sgr-django.service` configurado bajo `systemd` para reinicio automático ante fallas o reinicios del servidor.
* **Base de Datos Productiva:** MySQL Server local en el puerto `3306`, asegurada con usuario dedicado y contraseñas cifradas.

### 6.2 Control de Versiones en GitHub
* **Repositorio:** `https://github.com/iScreamyy6/Backend.git`
* **Rama Principal:** `main`
* **Metodología de Trabajo:** Commits incrementales estructurados con mensajes descriptivos según la convención *Conventional Commits* (`feat:`, `fix:`, `test:`).

---

## 7. EVIDENCIAS DE USO DE INTELIGENCIA ARTIFICIAL

En cumplimiento con el criterio de evaluación correspondiente al uso de herramientas de Inteligencia Artificial para el desarrollo de software, se documenta a continuación el registro de apoyo metodológico:

### 7.1 Prompts Clave y Decisiones Asistidas

#### Caso 1: Diseño de la Arquitectura de Seguridad (Grupos vs. Roles)
* **Prompt Utilizado:**
  > *"Necesito cumplir con los requerimientos de la Evaluación 3 de Django donde se exigen tres perfiles nativos (Administrador, Supervisor, Administrativo) con grupos de Django, pero en el proyecto ya existía un modelo Rol institucional. ¿Cómo desacoplar la autorización técnica de la función municipal sin romper el código previo?"*
* **Solución Implementada:**
  La IA propuso una arquitectura de dos capas: los **Grupos de Django** gobiernan los permisos de vistas y acceso a mantenedores (`request.user.groups`), mientras que el modelo **`Rol`** gobierna el cargo municipal específico (`PerfilUsuario.rol`), permitiendo una especialización granular en los dashboards sin duplicar la lógica de seguridad.

#### Caso 2: Flujo Seguro de Correo y Código de 6 Dígitos
* **Prompt Utilizado:**
  > *"Configura el envío de correos vía SMTP real con Gmail en Django para el restablecimiento de contraseñas. El flujo debe pedir obligatoriamente en pantalla un código PIN de 6 dígitos que llegue al correo, evitando mostrar datos sensibles en la vista y previniendo ataques de fuerza bruta."*
* **Solución Implementada:**
  Se diseñó un flujo que combina `default_token_generator` con un código PIN almacenado con expiración de 15 minutos (`codigo_expiracion`) y contador de intentos fallidos (`intentos_fallidos >= 3`), redirigiendo inmediatamente a una interfaz interactiva de 6 dígitos que avanza automáticamente.

#### Caso 3: Automatización Integral del Test Suite
* **Prompt Utilizado:**
  > *"Crea un script automatizado en Python para probar de punta a punta toda la evaluación sumativa 3: autenticación, restricción de perfiles, asignación de grupos en CRUD de usuarios, generación de token y validación de dashboards."*
* **Solución Implementada:**
  Se desarrolló la sección 12 en `test_suite.py` utilizando el `Client` de pruebas de Django, asegurando el 100% de cobertura y validación previa antes de desplegar en producción.

---

## 8. CONCLUSIONES
El Sistema de Gestión de Resultados (SGR) cumple rigurosamente con la totalidad de los requisitos pedagógicos y funcionales establecidos en la pauta de la Evaluación Sumativa N°3:
* La seguridad del sistema fue robustecida mediante la integración formal de los grupos y permisos de Django.
* La experiencia de usuario en la recuperación de contraseñas es real, moderna y protegida contra abusos.
* La separación de dashboards y restricciones en vistas garantiza la confidencialidad y segregación de funciones exigidas en una institución pública.
* La aplicación se encuentra desplegada y operativa en la nube de AWS, con sus pruebas automatizadas pasando al 100% tanto en local como en producción.
