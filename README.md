# Sistema de Gestión de Resultados (SGR)
## Ilustre Municipalidad de La Serena

**Asignatura:** Programación Back End (TI3041)  
**Evaluación:** Sumativa #3 (30%) — Aplicación Web con CRUD y Perfiles  
**Docente Guía:** Mariavictoria Freites Ayala / Alex Díaz Araos  
**Sede:** INACAP La Serena  
**Carrera:** Ingeniería en Informática  

---

## Integrantes del Equipo

| Nombre | Rol Principal |
| :--- | :--- |
| **Emanuel Román Serón** | Seguridad, Autenticación, SMTP, Despliegue AWS EC2 y QA |
| **Álvaro Obregón** | Modelado ORM, Migraciones y Base de Datos Relacional |
| **Benjamín Antipa** | Desarrollo de Vistas, Dashboards y Mantenedores CRUD |

---

## 1. Descripción del Proyecto

El **Sistema de Gestión de Resultados (SGR)** es una solución web empresarial desarrollada sobre **Django Framework**, diseñada para centralizar y modernizar los procesos de atención ciudadana, gestión territorial descentralizada, seguimiento de compromisos intersectoriales y monitoreo de metas en las diversas delegaciones de la Ilustre Municipalidad de La Serena.

Para esta **Tercera Evaluación Sumativa (30%)**, el sistema implementa un esquema completo de seguridad corporativa, segregación de funciones basada en roles y grupos nativos de Django, recuperación segura de contraseñas mediante correo electrónico real, paneles de control diferenciados y operación 100% basada en plantillas personalizadas (Django Templates).

### Características Principales de la Evaluación #3

1. **Autenticación y Control de Acceso por Perfiles:**
   - Tres niveles de acceso claramente diferenciados mediante grupos de Django (`Group` y `Permission`):
     - **Administrador:** Acceso total, auditoría, gestión de usuarios y 6 mantenedores CRUD.
     - **Supervisor:** Monitoreo territorial, tablero Kanban, semáforo SGR y catálogos autorizados.
     - **Administrativo:** Permisos operacionales mínimos (atención ciudadana y gestiones de terreno).
   - Protección de vistas mediante `@login_required` y verificación estricta de permisos con mensajes de advertencia ante accesos no autorizados.
2. **Recuperación de Contraseña por Correo Real y Código PIN:**
   - Integración con servidor **SMTP de Gmail** en producción (`emanuelromanseron@gmail.com`).
   - Envío de un **código de seguridad numérico de 6 dígitos** a la casilla del usuario, complementado con un **enlace con token criptográfico seguro** (`HMAC-SHA256`) de un solo uso.
   - Pantalla interactiva con 6 casilleros numéricos (`[ ][ ][ ][ ][ ][ ]`), auto-avance, limitación de 3 intentos fallidos y vigencia de 15 minutos.
3. **Dashboards Personalizados por Perfil y Cargo Institucional:**
   - El panel de inicio (`/`) detecta automáticamente el perfil del funcionario y renderiza las herramientas correspondientes.
   - Sub-diferenciación especializada para cargos operativos: **Gestor Social** (casos sociales y fichas), **Funcionario Territorial** (terreno y evidencias), **DISERCO** (servicios comunitarios) y **Funcionario Operador** (ventanilla presencial).
4. **Operación 100% en Django Templates (Sin Dependencia de Django Admin):**
   - La totalidad de las operaciones evaluadas (creación de usuarios, asignación de grupos, mantenedores, restablecimiento de claves y transacciones) se operan desde interfaces propias. Django Admin se mantiene intacto en `/admin/` exclusivamente como herramienta técnica interna de soporte.
5. **Seis Mantenedores CRUD Operativos:**
   - Delegaciones, Roles, Usuarios, Metas/Ítems, Tipos de Atención y Subatenciones con búsqueda insensible a mayúsculas, paginación, confirmaciones SweetAlert2 y exportación a **Excel (.xlsx)**.
6. **Transacción Operacional Compleja:**
   - Módulo de **Atención Ciudadana** con generación de folio correlativo único (`ATC-XXXXX`), selectores dependientes en cascada vía API interna (`TipoAtencion` → `Subatencion`) y asociación automática de vecinos por RUT.
7. **Suite de Pruebas Automatizadas:**
   - Script `test_suite.py` con cobertura completa de autenticación, grupos, restricciones, dashboards, mantenedores y transacciones, ejecutando con 100% de éxito (`exit code 0`).
8. **Despliegue Continuo en la Nube (AWS EC2):**
   - Instancia productiva en Amazon Web Services con base de datos MySQL, servicio systemd persistente y archivos estáticos servidos vía WhiteNoise.

---

## 2. Arquitectura del Repositorio

```
SGR-Municipalidad/
├── Municipalidad/                    # Configuración central del proyecto Django
│   ├── settings.py                   # Ajustes globales, BD, WhiteNoise y SMTP
│   ├── views.py                      # Vista de inicio y lógica de dashboards
│   ├── views_auth.py                 # Login, logout y flujo de recuperación por PIN/token
│   ├── views_mantenedores.py         # 6 CRUDs + Atención Ciudadana + API cascada + Excel
│   ├── context_processors.py         # Variables globales de delegación activa, rol y tier
│   └── urls.py                       # Enrutamiento general y paths del sistema
├── organizacion/                     # App: Delegaciones, Roles, Funcionarios y PerfilUsuario
├── actividades/                      # App: Atenciones Ciudadanas, Gestiones, Vecinos y Evidencias
├── agenda/                           # App: Compromisos del Tubo de Trabajo y Tablero Kanban
├── resultados/                       # App: Ítems, Metas ponderadas e Informe Ejecutivo SGR
├── static/                           # Hojas de estilo CSS corporativas (#AD0000) y scripts JS
├── templates/                        # Plantillas HTML estructuradas
│   ├── base.html                     # Layout maestro con cabecera y navegación según perfil
│   ├── inicio.html                   # Dashboards diferenciados (Admin, Super, Administrativo)
│   ├── auth/                         # Login, recuperar solicitud, validar PIN y nueva clave
│   ├── mantenedores/                 # Vistas de lista y formulario para los 6 mantenedores
│   └── atenciones/                   # Formulario en cascada y libro de atenciones
├── Contexto de la problematica/      # Documentación académica, requerimientos y pautas
│   └── 06_Entregables_e_Informe_Eva3/
│       ├── GUIA_DEMOSTRACION_DOCENTE_EVA3.md # Guion para defender la evaluación
│       └── INFORME_TECNICO_EVA3_SGR.md        # Informe formal INACAP
├── test_suite.py                     # Suite automatizada de pruebas de integración
├── requirements.txt                  # Dependencias Python del entorno
├── .env.example                      # Plantilla de variables de entorno seguras
└── manage.py                         # CLI de administración de Django
```

---

## 3. Matriz de Roles y Perfiles de Acceso (Eva #3)

| Perfil Django (`Group`) | Permisos | Cargo Institucional Ejemplo | Funcionalidades Habilitadas | Restricciones Aplicadas |
| :--- | :---: | :--- | :--- | :--- |
| **Administrador** | 80 | Administrador General (`admin`) | Acceso total al sistema, 6 mantenedores CRUD, gestión de usuarios, asignación de grupos Django, auditoría y configuración comunal. | Sin restricciones operativas. |
| **Supervisor** | 41 | Coordinador Municipal (`coordinador`) | Supervisión de metas SGR, semáforo institucional, monitoreo del Tubo Kanban y consulta de catálogos autorizados. | Bloqueado de la gestión de usuarios, roles y configuraciones críticas. |
| **Administrativo** | 14 | Operador (`operador_d01`), Territorial (`operador_d02`), DISERCO (`diserco`) | Recepción en ventanilla, levantamiento de atenciones ciudadanas, registro de gestiones en terreno y evidencias fotográficas. | Bloqueado de mantenedores, reportes ejecutivos y administración de cuentas. |

---

## 4. Cuentas de Acceso para la Demostración

| Usuario | Contraseña | Perfil / Grupo Django | Cargo Institucional | Enfoque de Demostración |
| :--- | :--- | :--- | :--- | :--- |
| `admin` | `admin` | **Administrador** | Administrador General | Demostrar acceso global, CRUD de usuarios y asignación de grupos de Django. |
| `coordinador` | `admin` | **Supervisor** | Coordinador Municipal | Demostrar panel de supervisión, semáforo SGR y restricción en mantenedor de usuarios. |
| `operador_d01` | `admin` | **Administrativo** | Funcionario Operador | Demostrar ventanilla presencial e ingreso de Atención Ciudadana con folio correlativo. |
| `operador_d02` | `admin` | **Administrativo** | Funcionario Territorial | Demostrar panel especializado en labores e inspecciones en terreno. |
| `diserco` | `admin` | **Administrativo** | Funcionario DISERCO | Demostrar panel especializado en coordinación de servicios comunitarios. |

---

## 5. Puntos de Acceso en Vivo (AWS Cloud y Producción)

* **🌐 Aplicación Web en Producción (AWS EC2):** [http://3.229.11.31:8000/](http://3.229.11.31:8000/)
* **🔐 Pantalla de Inicio de Sesión:** [http://3.229.11.31:8000/login/](http://3.229.11.31:8000/login/)
* **✉️ Restablecimiento de Contraseñas:** [http://3.229.11.31:8000/recuperar/](http://3.229.11.31:8000/recuperar/)
* **📦 Repositorio Oficial en GitHub:** [https://github.com/iScreamyy6/Backend](https://github.com/iScreamyy6/Backend)

---

## 6. Instalación y Ejecución en Entorno Local

### Prerrequisitos
* Python 3.10 o superior
* Git
* MySQL 8.x (opcional, por defecto opera sobre SQLite en desarrollo)

### Pasos de Despliegue Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/iScreamyy6/Backend.git
   cd Backend
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux / macOS:
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar el archivo `.env`:**
   Crear el archivo `.env` en la raíz del proyecto basándose en `.env.example`:
   ```ini
   SECRET_KEY=clave_secreta_segura_de_desarrollo
   DEBUG=True
   ALLOWED_HOSTS=*
   DB_ENGINE=sqlite

   # Configuración de Correo Electrónico (Gmail SMTP)
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=tu_correo@gmail.com
   EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion_16_caracteres
   DEFAULT_FROM_EMAIL=SGR Municipalidad de La Serena <tu_correo@gmail.com>
   ```

5. **Aplicar migraciones:**
   ```bash
   python manage.py migrate
   ```

6. **Ejecutar el servidor local:**
   ```bash
   python manage.py runserver
   ```
   Abrir en el navegador: `http://localhost:8000/`

---

## 7. Ejecución de Pruebas Automatizadas

El proyecto incluye un script de integración continua que evalúa automáticamente todos los requerimientos de la rúbrica docente (autenticación, asignación de grupos, restricción funcional de URLs, flujo de recuperación por token y validación de dashboards):

```bash
python test_suite.py
```

**Resultado esperado:**
```text
[OK] Home (redirect / 200) OK
[OK] Login authenticated OK
[OK] /mantenedores/delegaciones/ & Excel Export OK
[OK] /mantenedores/roles/ & Excel Export OK
[OK] /mantenedores/usuarios/ & Excel Export OK
[OK] /mantenedores/items/ & Excel Export OK
[OK] /mantenedores/tipos-atencion/ & Excel Export OK
[OK] /mantenedores/subatenciones/ & Excel Export OK
[OK] API Subatenciones cascade OK: 4 found for Atención Social y Beneficios
[OK] Atención Ciudadana creada exitosamente: Folio ATC-00033
[OK] Atenciones Ciudadanas Excel Export OK
[OK] Recuperación paso 1: código generado 597397
[OK] Validación rechaza código erróneo
[OK] Validación aprueba código de 6 dígitos
[OK] Token criptográfico generado y enlace emitido: http://localhost/recuperar/reset/...
[OK] Validación de token seguro exitosa
[OK] Restablecimiento de contraseña por token exitoso
[OK] Token de un solo uso invalidado tras su consumo
[OK] Dashboard Administrador verificado al 100%
[OK] Dashboard Supervisor verificado al 100%
[OK] Dashboard Administrativo verificado al 100%
[OK] Restricción funcional: Perfil Administrativo bloqueado de mantenedor de usuarios
[OK] Asignación de grupos verificada: nuevo_supervisor_test -> Grupo Supervisor

[EXITO COMPLETO EVALUACIÓN #3] AUTENTICACIÓN, GRUPOS, RECUPERACIÓN POR TOKEN, DASHBOARDS Y RESTRICCIONES AL 100%
```

---

## 8. Administración del Servicio en AWS EC2

La aplicación en la nube es administrada mediante `systemd`:

```bash
# Ver estado del servicio
sudo systemctl status sgr-django.service

# Reiniciar el servicio tras actualizar código
sudo systemctl restart sgr-django.service

# Ver registros de actividad en tiempo real
sudo journalctl -u sgr-django.service -f
```

---

## 9. Evidencias de Apoyo con Inteligencia Artificial

Durante el desarrollo de la Evaluación Sumativa #3 se empleó Inteligencia Artificial como asistente metodológico en:
1. **Desacoplamiento arquitectónico:** Separación limpia entre grupos de autorización técnica (`django.contrib.auth.models.Group`) y cargos municipales operativos (`PerfilUsuario.rol`).
2. **Seguridad en restablecimiento de contraseñas:** Diseño del flujo con mitigación de ataques de fuerza bruta (máximo 3 intentos de PIN y tokens `HMAC-SHA256` de consumo único).
3. **Automatización de pruebas:** Desarrollo del arnés de pruebas automatizadas con el cliente de testing de Django.

El detalle completo de los prompts y análisis se encuentra documentado en el archivo:  
[`Contexto de la problematica/06_Entregables_e_Informe_Eva3/INFORME_TECNICO_EVA3_SGR.md`](Contexto%20de%20la%20problematica/06_Entregables_e_Informe_Eva3/INFORME_TECNICO_EVA3_SGR.md).

---

*SGR — Sistema de Gestión de Resultados | Ilustre Municipalidad de La Serena | Evaluación Sumativa N°3 · 2026*
