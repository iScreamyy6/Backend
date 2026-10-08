# Sistema de GestiÃ³n de Resultados (SGR)
## Ilustre Municipalidad de La Serena

**Asignatura:** ProgramaciÃ³n Back End (TI3041)  
**EvaluaciÃ³n:** Sumativa #2 (25%)  
**Docente:** Alex DÃ­az Araos  
**Sede:** La Serena  
**Carrera:** IngenierÃ­a en InformÃ¡tica / Analista Programador  

### ðŸ‘¥ Integrantes
- Ãlvaro ObregÃ³n
- BenjamÃ­n Antipa
- Emanuel RomÃ¡n

---

## ðŸ“Œ 1. DescripciÃ³n del Proyecto

El **Sistema de GestiÃ³n de Resultados (SGR)** es una aplicaciÃ³n web back-end modular desarrollada con Django Framework, orientada a modernizar los procesos de gestiÃ³n territorial, monitoreo de compromisos y evaluaciÃ³n de desempeÃ±o por metas de las delegaciones municipales de La Serena.

Evolucionando desde el prototipo inicial basado en archivos JSON (EvaluaciÃ³n Sumativa #1), esta versiÃ³n implementa:

1. **Persistencia relacional completa** en MySQL (InnoDB, UTF-8).
2. **Modelado ORM con Django** con claves forÃ¡neas consistentes y migraciones aplicadas.
3. **Panel de administraciÃ³n integral** mediante Django Admin con CRUD, bÃºsquedas y filtros.
4. **Despliegue en infraestructura cloud AWS EC2** con systemd y servicio de estÃ¡ticos con WhiteNoise.
5. **Control de versiones** mediante Git y repositorio en GitHub.

---

## ðŸ—ï¸ 2. Arquitectura del Proyecto

El proyecto estÃ¡ estructurado en cuatro aplicaciones Django independientes:

```
SGR-Municipalidad/
â”œâ”€â”€ Municipalidad/         # ConfiguraciÃ³n central (settings.py, urls.py, wsgi.py)
â”œâ”€â”€ organizacion/          # Delegaciones territoriales y nÃ³mina de funcionarios
â”œâ”€â”€ actividades/           # Registro de gestiones diarias y bandeja de evidencias
â”œâ”€â”€ agenda/                # Tubo de trabajo, compromisos y tablero kanban
â”œâ”€â”€ resultados/            # SemÃ¡foro de cumplimiento, metas ponderadas e indicadores
â”œâ”€â”€ static/                # Archivos CSS, imÃ¡genes e Ã­conos
â”œâ”€â”€ staticfiles/           # Archivos recolectados para producciÃ³n (WhiteNoise)
â”œâ”€â”€ templates/             # Plantillas HTML con diseÃ±o responsivo
â”œâ”€â”€ script_mysql_sgr.sql   # Script SQL DDL/DML con el modelo relacional fÃ­sico
â”œâ”€â”€ requirements.txt       # Dependencias del proyecto
â”œâ”€â”€ .env.example           # Ejemplo de variables de entorno
â””â”€â”€ manage.py              # Interfaz de comandos Django
```

---

## ðŸ—„ï¸ 3. Modelo Relacional â€” Base de Datos MySQL

Las entidades Django estÃ¡n mapeadas mediante `db_table` a las siguientes tablas:

| Tabla | DescripciÃ³n |
|-------|-------------|
| `delegaciones` | Unidades territoriales descentralizadas (Las CompaÃ±Ã­as, La Antena, etc.) |
| `funcionarios` | NÃ³mina de funcionarios adscritos con control de estado y cargo |
| `actividades` | Libro diario de gestiones y atenciÃ³n de vecinos en terreno |
| `evidencias` | Respaldo documental y fotogrÃ¡fico validado de las gestiones |
| `compromisos_tubo` | Tubo colectivo de compromisos con juntas de vecinos |
| `periodos_evaluacion` | Ciclos temporales de metas y monitoreo |
| `metas_funcionario` | PonderaciÃ³n, avances y felicitaciones/reclamos individuales |
| `indicadores_delegacion` | Indicadores consolidados por Ã¡rea y estado semÃ¡foro |

**Relaciones implementadas:**
- `Funcionario` â†’ `Delegacion` (ForeignKey)
- `Actividad` â†’ `Funcionario` (ForeignKey)
- `Evidencia` â†’ `Actividad` (ForeignKey)
- `Compromiso` â†’ `Delegacion`, `Funcionario` (ForeignKey)
- `MetaFuncionario` â†’ `Funcionario`, `PeriodoEvaluacion` (ForeignKey)
- `IndicadorDelegacion` â†’ `Delegacion`, `PeriodoEvaluacion` (ForeignKey)

---

## âš™ï¸ 4. Variables de Entorno

La configuraciÃ³n sensible se gestiona mediante `python-dotenv` y un archivo `.env` (no incluido en el repositorio). Crear el archivo `.env` en la raÃ­z del proyecto:

```ini
# Seguridad Django
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=*

# Motor de Base de Datos: 'sqlite' o 'mysql'
DB_ENGINE=mysql

# ConfiguraciÃ³n MySQL
DB_NAME=sgr_municipalidad
DB_USER=sgr_user
DB_PASSWORD=tu_password_aqui
DB_HOST=127.0.0.1
DB_PORT=3306
```

> Para desarrollo local con SQLite, usar `DB_ENGINE=sqlite`.

---

## ðŸš€ 5. InstalaciÃ³n y EjecuciÃ³n Local

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
*(Completar los valores segÃºn el entorno)*

**6. Aplicar las migraciones**
```bash
python manage.py migrate
```

**7. Crear el superusuario**
```bash
python manage.py createsuperuser
```

**8. Recolectar archivos estÃ¡ticos**
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

### âš ï¸ Reactivar el entorno virtual (sesiones posteriores)

Cada vez que abras una nueva terminal, debes activar el entorno virtual antes de ejecutar cualquier comando Django:

```bash
# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

---

## â˜ï¸ 6. Despliegue en AWS EC2

### Infraestructura
- **Instancia:** Amazon EC2 â€” Ubuntu Server 24.04 LTS
- **IP PÃºblica:** 3.229.11.31
- **Acceso SSH:** `ssh -i "SGR-Municipalidad.pem" ubuntu@3.229.11.31`
- **Base de Datos:** MySQL 8.x en la misma instancia
- **Servidor Web:** Apache 2.4 como proxy inverso (puerto 80 â†’ 8000)
- **Archivos EstÃ¡ticos:** WhiteNoise con compresiÃ³n
- **GestiÃ³n de Servicio:** systemd (`sgr-django.service`)

### Comandos de gestiÃ³n en el servidor

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

### URLs de ProducciÃ³n

| Servicio | URL |
|---------|-----|
| AplicaciÃ³n Web | http://3.229.11.31/ |
| Django Admin | http://3.229.11.31/admin/ |
| phpMyAdmin | http://3.229.11.31/phpmyadmin/ |
| Repositorio GitHub | https://github.com/iScreamyy6/Backend |

---

## ðŸ› ï¸ 7. Dependencias Principales

| Paquete | Uso |
|---------|-----|
| `Django` | Framework principal |
| `mysqlclient` | Conector MySQL |
| `python-dotenv` | Variables de entorno |
| `whitenoise` | Servicio de archivos estÃ¡ticos en producciÃ³n |

Ver listado completo en `requirements.txt`.

---

## ðŸ“ 8. Control de Versiones

```bash
# Clonar el proyecto (primera vez)
git clone https://github.com/iScreamyy6/Backend.git

# Ver historial de commits
git log --oneline

# Actualizar desde GitHub
git pull origin main
```

---

## ðŸ¤– 9. Evidencia de Uso de Inteligencia Artificial

Durante el desarrollo del proyecto se utilizÃ³ **IA generativa (Google Antigravity)** como herramienta de apoyo. A continuaciÃ³n se detallan los casos concretos donde la IA fue consultada y cÃ³mo se aplicaron sus respuestas:

### Caso 1 â€” Conflicto de migraciones en MySQL (`Table already exists`)
**Prompt utilizado:**
> *"Al ejecutar `python manage.py migrate` en el servidor, obtengo el error `(1050, 'Table delegaciones already exists')`. Las tablas del negocio ya existen porque fueron creadas con el script SQL. Â¿CÃ³mo aplico solo las migraciones del sistema Django sin recrear las tablas existentes?"*

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

**AplicaciÃ³n:** Se ejecutaron estos comandos en el servidor EC2, lo que permitiÃ³ crear las tablas del sistema Django (`auth_user`, `django_session`, `django_admin_log`) sin tocar las tablas del negocio ya existentes.

---

### Caso 2 â€” Error 500 en Django Admin al iniciar sesiÃ³n
**Prompt utilizado:**
> *"Al entrar al Django Admin con usuario y contraseÃ±a, me sale `Server Error (500)`. El log muestra que el POST a `/admin/login/` devuelve 500. Â¿Por quÃ©?"*

**Respuesta de la IA:**
El error 500 al hacer POST en el login indica que la tabla `django_session` o `auth_user` no existe. Django necesita estas tablas para procesar la autenticaciÃ³n. La causa es que las migraciones del sistema nunca se aplicaron en el servidor MySQL.

**AplicaciÃ³n:** Se identificÃ³ que las migraciones del sistema estaban pendientes (marcadas como `[ ]`). Se aplicaron correctamente con los comandos descritos en el Caso 1, y luego se creÃ³ el superusuario con `python manage.py createsuperuser`.

---

### Caso 3 â€” Compatibilidad de propiedad `id` en modelos con clave primaria personalizada
**Prompt utilizado:**
> *"Los modelos Django tienen `id_delegacion = models.AutoField(primary_key=True)` en lugar del `id` estÃ¡ndar. Los templates usan `{{ objeto.id }}` y los links se generan vacÃ­os. Â¿CÃ³mo soluciono esto sin cambiar todos los templates?"*

**Respuesta de la IA:**
Agregar una `@property` llamada `id` en cada modelo que retorne `self.pk`, lo que hace compatible el acceso desde templates sin cambiar el esquema de la base de datos:
```python
@property
def id(self):
    return self.pk
```

**AplicaciÃ³n:** Se agregÃ³ esta propiedad a todos los modelos del proyecto (`Delegacion`, `Funcionario`, `Actividad`, `Evidencia`, `Compromiso`, `PeriodoEvaluacion`, `MetaFuncionario`, `IndicadorDelegacion`), resolviendo los links rotos en las vistas.

---

### Caso 4 â€” ConfiguraciÃ³n de WhiteNoise para archivos estÃ¡ticos en producciÃ³n
**Prompt utilizado:**
> *"En el servidor EC2 los archivos CSS e imÃ¡genes no cargan. Django no sirve estÃ¡ticos en producciÃ³n con DEBUG=False. Â¿CÃ³mo lo soluciono sin Nginx?"*

**Respuesta de la IA:**
Instalar `whitenoise` y configurarlo en `settings.py` como middleware y storage backend, lo que permite que Django sirva sus propios archivos estÃ¡ticos en producciÃ³n:
```python
INSTALLED_APPS = ['whitenoise.runserver_nostatic', ...]
MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ...]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
```

**AplicaciÃ³n:** Se instalÃ³ WhiteNoise, se configurÃ³ en `settings.py` y se ejecutÃ³ `python manage.py collectstatic`. Los archivos estÃ¡ticos quedaron disponibles en producciÃ³n sin necesidad de Nginx.

---

### Caso 5 â€” Idioma y zona horaria del panel de administraciÃ³n
**Prompt utilizado:**
> *"El panel Django Admin aparece en inglÃ©s. Â¿CÃ³mo lo cambio a espaÃ±ol y configuro la hora de Chile?"*

**Respuesta de la IA:**
Modificar las variables `LANGUAGE_CODE` y `TIME_ZONE` en `settings.py`:
```python
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'
```

**AplicaciÃ³n:** Se actualizÃ³ `settings.py`, se hizo `git push` y `git pull` en el servidor, y el admin quedÃ³ completamente en espaÃ±ol con hora de Chile.

---

## ðŸ¤– 9. Evidencia de Uso de Inteligencia Artificial

Durante el desarrollo del proyecto se utilizÃ³ **IA generativa (Google Antigravity / Gemini)** como herramienta de apoyo. A continuaciÃ³n se detallan los casos concretos donde la IA fue consultada y cÃ³mo se aplicaron sus respuestas:

### Caso 1 â€” Conflicto de migraciones en MySQL (`Table already exists`)
**Prompt utilizado:**
> *"Al ejecutar `python manage.py migrate` en el servidor, obtengo el error `(1050, 'Table delegaciones already exists')`. Las tablas del negocio ya existen porque fueron creadas con el script SQL. Â¿CÃ³mo aplico solo las migraciones del sistema Django sin recrear las tablas existentes?"*

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

**AplicaciÃ³n:** Se ejecutaron estos comandos en el servidor EC2, lo que permitiÃ³ crear las tablas del sistema Django (`auth_user`, `django_session`, `django_admin_log`) sin eliminar las tablas de negocio ya existentes.

---

### Caso 2 â€” Error 500 en Django Admin al iniciar sesiÃ³n
**Prompt utilizado:**
> *"Al entrar al Django Admin con usuario y contraseÃ±a, me sale Server Error (500). El log muestra que el POST a /admin/login/ devuelve 500. Â¿Por quÃ© ocurre esto?"*

**Respuesta de la IA:**
El error 500 en el POST del login indica que la tabla `django_session` o `auth_user` no existe en la base de datos. Django las necesita para procesar la autenticaciÃ³n. La causa raÃ­z es que las migraciones del sistema (auth, sessions) nunca fueron aplicadas en MySQL.

**AplicaciÃ³n:** Se identificÃ³ mediante `showmigrations` que todas las migraciones estaban pendientes. Se aplicaron con `--fake` para las apps del negocio y normalmente para las del sistema. Luego se creÃ³ el superusuario con `python manage.py createsuperuser`.

---

### Caso 3 â€” Compatibilidad de propiedad `id` en modelos con clave primaria personalizada
**Prompt utilizado:**
> *"Los modelos Django tienen `id_delegacion = models.AutoField(primary_key=True)` en lugar del `id` estÃ¡ndar. Los templates usan `{{ objeto.id }}` y los links se generan vacÃ­os. Â¿CÃ³mo soluciono esto sin cambiar el esquema de la base de datos ni todos los templates?"*

**Respuesta de la IA:**
Agregar una `@property` llamada `id` en cada modelo que retorne `self.pk`, haciÃ©ndolo compatible con templates sin modificar el esquema relacional:
```python
@property
def id(self):
    return self.pk
```

**AplicaciÃ³n:** Se agregÃ³ esta propiedad a todos los modelos del proyecto (`Delegacion`, `Funcionario`, `Actividad`, `Evidencia`, `Compromiso`, `MetaFuncionario`, `IndicadorDelegacion`), resolviendo los links rotos en todas las vistas pÃºblicas.

---

### Caso 4 â€” ConfiguraciÃ³n de WhiteNoise para archivos estÃ¡ticos en producciÃ³n
**Prompt utilizado:**
> *"En el servidor EC2 los archivos CSS e imÃ¡genes no cargan. Django no sirve archivos estÃ¡ticos en producciÃ³n con DEBUG=False. Â¿CÃ³mo lo soluciono sin instalar Nginx?"*

**Respuesta de la IA:**
Instalar `whitenoise` y configurarlo en `settings.py` como middleware y como storage backend, permitiendo que Django sirva sus propios archivos estÃ¡ticos en producciÃ³n:
```python
INSTALLED_APPS = ['whitenoise.runserver_nostatic', ...]
MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ...]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
```

**AplicaciÃ³n:** Se instalÃ³ WhiteNoise, se configurÃ³ en `settings.py`, y se ejecutÃ³ `python manage.py collectstatic`. Los estilos y recursos quedaron disponibles en producciÃ³n.

---

### Caso 5 â€” Idioma y zona horaria del panel de administraciÃ³n
**Prompt utilizado:**
> *"El panel Django Admin aparece completamente en inglÃ©s. Â¿CÃ³mo lo cambio a espaÃ±ol chileno y configuro la zona horaria correcta para Chile?"*

**Respuesta de la IA:**
Modificar `LANGUAGE_CODE` y `TIME_ZONE` en `settings.py`:
```python
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'
```

**AplicaciÃ³n:** Se actualizÃ³ `settings.py`, se hizo commit, push y git pull en el servidor. El panel Django Admin quedÃ³ completamente en espaÃ±ol con hora de Chile.
