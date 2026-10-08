# Sistema de Gestión de Resultados (SGR)
## Ilustre Municipalidad de La Serena

**Asignatura:** Programación Back End (TI3041)  
**Evaluación:** Sumativa #2 (25%)  
**Docente:** Alex Díaz Araos  
**Sede:** La Serena  
**Carrera:** Ingeniería en Informática / Analista Programador  

### 👥 Integrantes
- Álvaro Obregón
- Benjamín Antipa
- Emanuel Román

---

## 📌 1. Descripción del Proyecto

El **Sistema de Gestión de Resultados (SGR)** es una aplicación web back-end modular desarrollada con Django Framework, orientada a modernizar los procesos de gestión territorial, monitoreo de compromisos y evaluación de desempeño por metas de las delegaciones municipales de La Serena.

Evolucionando desde el prototipo inicial basado en archivos JSON (Evaluación Sumativa #1), esta versión implementa:

1. **Persistencia relacional completa** en MySQL (InnoDB, UTF-8).
2. **Modelado ORM con Django** con claves foráneas consistentes y migraciones aplicadas.
3. **Panel de administración integral** mediante Django Admin con CRUD, búsquedas y filtros.
4. **Despliegue en infraestructura cloud AWS EC2** con systemd y servicio de estáticos con WhiteNoise.
5. **Control de versiones** mediante Git y repositorio en GitHub.

---

## 🏗️ 2. Arquitectura del Proyecto

El proyecto está estructurado en cuatro aplicaciones Django independientes:

```
SGR-Municipalidad/
├── Municipalidad/         # Configuración central (settings.py, urls.py, wsgi.py)
├── organizacion/          # Delegaciones territoriales y nómina de funcionarios
├── actividades/           # Registro de gestiones diarias y bandeja de evidencias
├── agenda/                # Tubo de trabajo, compromisos y tablero kanban
├── resultados/            # Semáforo de cumplimiento, metas ponderadas e indicadores
├── static/                # Archivos CSS, imágenes e íconos
├── staticfiles/           # Archivos recolectados para producción (WhiteNoise)
├── templates/             # Plantillas HTML con diseño responsivo
├── script_mysql_sgr.sql   # Script SQL DDL/DML con el modelo relacional físico
├── requirements.txt       # Dependencias del proyecto
├── .env.example           # Ejemplo de variables de entorno
└── manage.py              # Interfaz de comandos Django
```

---

## 🗄️ 3. Modelo Relacional — Base de Datos MySQL

Las entidades Django están mapeadas mediante `db_table` a las siguientes tablas:

| Tabla | Descripción |
|-------|-------------|
| `delegaciones` | Unidades territoriales descentralizadas (Las Compañías, La Antena, etc.) |
| `funcionarios` | Nómina de funcionarios adscritos con control de estado y cargo |
| `actividades` | Libro diario de gestiones y atención de vecinos en terreno |
| `evidencias` | Respaldo documental y fotográfico validado de las gestiones |
| `compromisos_tubo` | Tubo colectivo de compromisos con juntas de vecinos |
| `periodos_evaluacion` | Ciclos temporales de metas y monitoreo |
| `metas_funcionario` | Ponderación, avances y felicitaciones/reclamos individuales |
| `indicadores_delegacion` | Indicadores consolidados por área y estado semáforo |

**Relaciones implementadas:**
- `Funcionario` → `Delegacion` (ForeignKey)
- `Actividad` → `Funcionario` (ForeignKey)
- `Evidencia` → `Actividad` (ForeignKey)
- `Compromiso` → `Delegacion`, `Funcionario` (ForeignKey)
- `MetaFuncionario` → `Funcionario`, `PeriodoEvaluacion` (ForeignKey)
- `IndicadorDelegacion` → `Delegacion`, `PeriodoEvaluacion` (ForeignKey)

---

## ⚙️ 4. Variables de Entorno

La configuración sensible se gestiona mediante `python-dotenv` y un archivo `.env` (no incluido en el repositorio). Crear el archivo `.env` en la raíz del proyecto:

```ini
# Seguridad Django
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=*

# Motor de Base de Datos: 'sqlite' o 'mysql'
DB_ENGINE=mysql

# Configuración MySQL
DB_NAME=sgr_municipalidad
DB_USER=sgr_user
DB_PASSWORD=tu_password_aqui
DB_HOST=127.0.0.1
DB_PORT=3306
```

> Para desarrollo local con SQLite, usar `DB_ENGINE=sqlite`.

---

## 🚀 5. Instalación y Ejecución Local

### Prerrequisitos
- Python 3.10 o superior
- Git
- MySQL (opcional, solo si no se usa SQLite)

### Pasos

**1. Clonar el repositorio**
```bash
git clone https://github.com/iScreamyy6/Backend.git
cd Backend
```

**2. Crear el entorno virtual**
```bash
python -m venv venv
```

**3. Activar el entorno virtual**
```bash
# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Windows (CMD):
venv\Scripts\activate.bat

# Linux / macOS:
source venv/bin/activate
```

**4. Instalar las dependencias**
```bash
pip install -r requirements.txt
```

**5. Crear el archivo .env**
```bash
# Windows:
copy .env.example .env

# Linux/macOS:
cp .env.example .env
```
*(Completar los valores según el entorno)*

**6. Aplicar las migraciones**
```bash
python manage.py migrate
```

**7. Crear el superusuario**
```bash
python manage.py createsuperuser
```

**8. Recolectar archivos estáticos**
```bash
python manage.py collectstatic --noinput
```

**9. Ejecutar el servidor de desarrollo**
```bash
python manage.py runserver
```

Acceder a: http://127.0.0.1:8000/  
Panel Admin: http://127.0.0.1:8000/admin/

---

### ⚠️ Reactivar el entorno virtual (sesiones posteriores)

Cada vez que abras una nueva terminal, debes activar el entorno virtual antes de ejecutar cualquier comando Django:

```bash
# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

---

## ☁️ 6. Despliegue en AWS EC2

### Infraestructura
- **Instancia:** Amazon EC2 — Ubuntu Server 24.04 LTS
- **IP Pública:** 3.229.11.31
- **Acceso SSH:** `ssh -i "SGR-Municipalidad.pem" ubuntu@3.229.11.31`
- **Base de Datos:** MySQL 8.x en la misma instancia
- **Servidor Web:** Apache 2.4 como proxy inverso (puerto 80 → 8000)
- **Archivos Estáticos:** WhiteNoise con compresión
- **Gestión de Servicio:** systemd (`sgr-django.service`)

### Comandos de gestión en el servidor

```bash
# Ver estado del servicio
sudo systemctl status sgr-django

# Reiniciar el servicio
sudo systemctl restart sgr-django

# Ver logs en tiempo real
tail -f /home/ubuntu/django.log

# Actualizar desde GitHub y reiniciar
cd /home/ubuntu/SGR-Municipalidad
git pull origin main
sudo systemctl restart sgr-django
```

### URLs de Producción

| Servicio | URL |
|---------|-----|
| Aplicación Web | http://3.229.11.31/ |
| Django Admin | http://3.229.11.31/admin/ |
| phpMyAdmin | http://3.229.11.31/phpmyadmin/ |
| Repositorio GitHub | https://github.com/iScreamyy6/Backend |

---

## 🛠️ 7. Dependencias Principales

| Paquete | Uso |
|---------|-----|
| `Django` | Framework principal |
| `mysqlclient` | Conector MySQL |
| `python-dotenv` | Variables de entorno |
| `whitenoise` | Servicio de archivos estáticos en producción |

Ver listado completo en `requirements.txt`.

---

## 📁 8. Control de Versiones

```bash
# Clonar el proyecto (primera vez)
git clone https://github.com/iScreamyy6/Backend.git

# Ver historial de commits
git log --oneline

# Actualizar desde GitHub
git pull origin main
```

---

## 🤖 9. Evidencia de Uso de Inteligencia Artificial

Durante el desarrollo del proyecto se utilizó **IA generativa (Google Antigravity)** como herramienta de apoyo. A continuación se detallan los casos concretos donde la IA fue consultada y cómo se aplicaron sus respuestas:

### Caso 1 — Conflicto de migraciones en MySQL (`Table already exists`)
**Prompt utilizado:**
> *"Al ejecutar `python manage.py migrate` en el servidor, obtengo el error `(1050, 'Table delegaciones already exists')`. Las tablas del negocio ya existen porque fueron creadas con el script SQL. ¿Cómo aplico solo las migraciones del sistema Django sin recrear las tablas existentes?"*

**Respuesta de la IA:**
Utilizar `--fake` para marcar como aplicadas las migraciones de las apps cuyas tablas ya existen, y aplicar normalmente las migraciones del sistema (auth, sessions, admin, contenttypes):
```bash
python manage.py migrate --fake organizacion
python manage.py migrate --fake actividades
python manage.py migrate --fake agenda
python manage.py migrate --fake resultados
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate admin
python manage.py migrate sessions
```

**Aplicación:** Se ejecutaron estos comandos en el servidor EC2, lo que permitió crear las tablas del sistema Django (`auth_user`, `django_session`, `django_admin_log`) sin tocar las tablas del negocio ya existentes.

---

### Caso 2 — Error 500 en Django Admin al iniciar sesión
**Prompt utilizado:**
> *"Al entrar al Django Admin con usuario y contraseña, me sale `Server Error (500)`. El log muestra que el POST a `/admin/login/` devuelve 500. ¿Por qué?"*

**Respuesta de la IA:**
El error 500 al hacer POST en el login indica que la tabla `django_session` o `auth_user` no existe. Django necesita estas tablas para procesar la autenticación. La causa es que las migraciones del sistema nunca se aplicaron en el servidor MySQL.

**Aplicación:** Se identificó que las migraciones del sistema estaban pendientes (marcadas como `[ ]`). Se aplicaron correctamente con los comandos descritos en el Caso 1, y luego se creó el superusuario con `python manage.py createsuperuser`.

---

### Caso 3 — Compatibilidad de propiedad `id` en modelos con clave primaria personalizada
**Prompt utilizado:**
> *"Los modelos Django tienen `id_delegacion = models.AutoField(primary_key=True)` en lugar del `id` estándar. Los templates usan `{{ objeto.id }}` y los links se generan vacíos. ¿Cómo soluciono esto sin cambiar todos los templates?"*

**Respuesta de la IA:**
Agregar una `@property` llamada `id` en cada modelo que retorne `self.pk`, lo que hace compatible el acceso desde templates sin cambiar el esquema de la base de datos:
```python
@property
def id(self):
    return self.pk
```

**Aplicación:** Se agregó esta propiedad a todos los modelos del proyecto (`Delegacion`, `Funcionario`, `Actividad`, `Evidencia`, `Compromiso`, `PeriodoEvaluacion`, `MetaFuncionario`, `IndicadorDelegacion`), resolviendo los links rotos en las vistas.

---

### Caso 4 — Configuración de WhiteNoise para archivos estáticos en producción
**Prompt utilizado:**
> *"En el servidor EC2 los archivos CSS e imágenes no cargan. Django no sirve estáticos en producción con DEBUG=False. ¿Cómo lo soluciono sin Nginx?"*

**Respuesta de la IA:**
Instalar `whitenoise` y configurarlo en `settings.py` como middleware y storage backend, lo que permite que Django sirva sus propios archivos estáticos en producción:
```python
INSTALLED_APPS = ['whitenoise.runserver_nostatic', ...]
MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ...]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
```

**Aplicación:** Se instaló WhiteNoise, se configuró en `settings.py` y se ejecutó `python manage.py collectstatic`. Los archivos estáticos quedaron disponibles en producción sin necesidad de Nginx.

---

### Caso 5 — Idioma y zona horaria del panel de administración
**Prompt utilizado:**
> *"El panel Django Admin aparece en inglés. ¿Cómo lo cambio a español y configuro la hora de Chile?"*

**Respuesta de la IA:**
Modificar las variables `LANGUAGE_CODE` y `TIME_ZONE` en `settings.py`:
```python
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'
```

**Aplicación:** Se actualizó `settings.py`, se hizo `git push` y `git pull` en el servidor, y el admin quedó completamente en español con hora de Chile.

---

## 🤖 9. Evidencia de Uso de Inteligencia Artificial

Durante el desarrollo del proyecto se utilizó **IA generativa (Google Antigravity / Gemini)** como herramienta de apoyo. A continuación se detallan los casos concretos donde la IA fue consultada y cómo se aplicaron sus respuestas:

### Caso 1 — Conflicto de migraciones en MySQL (`Table already exists`)
**Prompt utilizado:**
> *"Al ejecutar `python manage.py migrate` en el servidor, obtengo el error `(1050, 'Table delegaciones already exists')`. Las tablas del negocio ya existen porque fueron creadas con el script SQL. ¿Cómo aplico solo las migraciones del sistema Django sin recrear las tablas existentes?"*

**Respuesta de la IA:**
Utilizar `--fake` para marcar como aplicadas las migraciones de las apps cuyas tablas ya existen, y aplicar normalmente las del sistema (auth, sessions, admin, contenttypes):
```bash
python manage.py migrate --fake organizacion
python manage.py migrate --fake actividades
python manage.py migrate --fake agenda
python manage.py migrate --fake resultados
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate admin
python manage.py migrate sessions
```

**Aplicación:** Se ejecutaron estos comandos en el servidor EC2, lo que permitió crear las tablas del sistema Django (`auth_user`, `django_session`, `django_admin_log`) sin eliminar las tablas de negocio ya existentes.

---

### Caso 2 — Error 500 en Django Admin al iniciar sesión
**Prompt utilizado:**
> *"Al entrar al Django Admin con usuario y contraseña, me sale Server Error (500). El log muestra que el POST a /admin/login/ devuelve 500. ¿Por qué ocurre esto?"*

**Respuesta de la IA:**
El error 500 en el POST del login indica que la tabla `django_session` o `auth_user` no existe en la base de datos. Django las necesita para procesar la autenticación. La causa raíz es que las migraciones del sistema (auth, sessions) nunca fueron aplicadas en MySQL.

**Aplicación:** Se identificó mediante `showmigrations` que todas las migraciones estaban pendientes. Se aplicaron con `--fake` para las apps del negocio y normalmente para las del sistema. Luego se creó el superusuario con `python manage.py createsuperuser`.

---

### Caso 3 — Compatibilidad de propiedad `id` en modelos con clave primaria personalizada
**Prompt utilizado:**
> *"Los modelos Django tienen `id_delegacion = models.AutoField(primary_key=True)` en lugar del `id` estándar. Los templates usan `{{ objeto.id }}` y los links se generan vacíos. ¿Cómo soluciono esto sin cambiar el esquema de la base de datos ni todos los templates?"*

**Respuesta de la IA:**
Agregar una `@property` llamada `id` en cada modelo que retorne `self.pk`, haciéndolo compatible con templates sin modificar el esquema relacional:
```python
@property
def id(self):
    return self.pk
```

**Aplicación:** Se agregó esta propiedad a todos los modelos del proyecto (`Delegacion`, `Funcionario`, `Actividad`, `Evidencia`, `Compromiso`, `MetaFuncionario`, `IndicadorDelegacion`), resolviendo los links rotos en todas las vistas públicas.

---

### Caso 4 — Configuración de WhiteNoise para archivos estáticos en producción
**Prompt utilizado:**
> *"En el servidor EC2 los archivos CSS e imágenes no cargan. Django no sirve archivos estáticos en producción con DEBUG=False. ¿Cómo lo soluciono sin instalar Nginx?"*

**Respuesta de la IA:**
Instalar `whitenoise` y configurarlo en `settings.py` como middleware y como storage backend, permitiendo que Django sirva sus propios archivos estáticos en producción:
```python
INSTALLED_APPS = ['whitenoise.runserver_nostatic', ...]
MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ...]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
```

**Aplicación:** Se instaló WhiteNoise, se configuró en `settings.py`, y se ejecutó `python manage.py collectstatic`. Los estilos y recursos quedaron disponibles en producción.

---

### Caso 5 — Idioma y zona horaria del panel de administración
**Prompt utilizado:**
> *"El panel Django Admin aparece completamente en inglés. ¿Cómo lo cambio a español chileno y configuro la zona horaria correcta para Chile?"*

**Respuesta de la IA:**
Modificar `LANGUAGE_CODE` y `TIME_ZONE` en `settings.py`:
```python
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'
```

**Aplicación:** Se actualizó `settings.py`, se hizo commit, push y git pull en el servidor. El panel Django Admin quedó completamente en español con hora de Chile.
