# Sistema de Gestión de Resultados (SGR) — Ilustre Municipalidad de La Serena
## Programación Back End (TI3041) — Evaluación Sumativa #2

### 👥 Integrantes del Equipo
* **Álvaro Obregón** (Módulos: *Organización* y *Resultados*)
* **Benjamín Antipa** (Módulos: *Agenda* y *Actividades*)
* **Docente**: Alex Díaz Araos  
* **Sede**: La Serena  
* **Carrera**: Ingeniería en Informática / Analista Programador

---

## 📌 1. Descripción del Proyecto
El **Sistema de Gestión de Resultados (SGR)** es una solución web back-end modular orientada a la modernización de los procesos de gestión territorial, monitoreo de compromisos y evaluación de desempeño por metas de las delegaciones municipales de La Serena.

Evolucionando desde el prototipo inicial basado en archivos JSON (Evaluación Sumativa #1), esta versión implementa:
1. **Persistencia relacional completa** en MySQL (InnoDB, UTF-8).
2. **Modelado ORM con Django** y claves foráneas consistentes.
3. **Panel de control administrativo integral** mediante Django Admin con permisos, búsquedas y filtros.
4. **Despliegue cloud** en infraestructura **AWS EC2** con servicio gestionado por systemd y servicio de estáticos optimizado con WhiteNoise.

---

## 🏗️ 2. Arquitectura de Aplicaciones

El proyecto está estructurado de manera desacoplada en cuatro aplicaciones Django independientes:

```text
Backend/
├── Municipalidad/       # Configuración central del proyecto (settings, urls, wsgi)
├── organizacion/        # EP-08: Delegaciones territoriales y nómina de funcionarios
├── actividades/         # EP-01/03: Registro de gestiones diarias y bandeja de evidencias
├── agenda/              # EP-04: Tubo de trabajo, compromisos intersectoriales y tablero kanban
├── resultados/          # EP-02/05: Semáforo de cumplimiento, metas ponderadas e indicadores
├── static/              # Hojas de estilo CSS, imágenes municipales (MuniV2.png), scripts
├── staticfiles/         # Archivos recolectados para producción mediante WhiteNoise
├── templates/           # Plantillas HTML con diseño responsivo y botones de control CRUD
└── script_mysql_sgr.sql # Script SQL DDL/DML con el modelo relacional físico
```

---

## 🗄️ 3. Modelo Relacional y Base de Datos (MySQL)

Las entidades están mapeadas mediante `db_table` a las 8 tablas diseñadas en el script relacional:
* `delegaciones`: Unidades territoriales descentralizadas (Las Compañías, La Antena, etc.).
* `funcionarios`: Nómina de funcionarios adscritos con control de estado y cargo.
* `actividades`: Libro diario de gestiones y atención de vecinos en terreno.
* `evidencias`: Respaldo documental y fotográfico validado de las gestiones.
* `compromisos_tubo`: Tubo colectivo de compromisos con juntas de vecinos.
* `periodos_evaluacion`: Ciclos temporales de metas y monitoreo.
* `metas_funcionario`: Ponderación, avances y felicitaciones/reclamos individuales.
* `indicadores_delegacion`: Indicadores consolidados por área y estado semáforo.

---

## ⚙️ 4. Variables de Entorno (.env)

La configuración sensible se desacopla mediante `python-dotenv`:
```ini
SECRET_KEY=django-insecure-produccion-sgr-2026
DEBUG=False
ALLOWED_HOSTS=*
DB_ENGINE=mysql
DB_NAME=sgr_municipalidad
DB_USER=sgr_user
DB_PASSWORD=Municipalidad2026!
DB_HOST=127.0.0.1
DB_PORT=3306
```

---

## 🚀 5. Instalación y Ejecución

### Entorno Local:
```bash
# 1. Clonar el repositorio
git clone https://github.com/iScreamyy6/Backend.git
cd Backend

# 2. Crear y activar entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno en .env y aplicar migraciones
python manage.py migrate

# 5. Ejecutar servidor
python manage.py runserver
```

### Despliegue en AWS EC2:
* **Host**: Instancia Ubuntu Server 24.04 LTS en Amazon EC2.
* **Servicio**: Gestionado como servicio de fondo con `systemd` (`sgr-django.service`).
* **Archivos Estáticos**: Distribuidos directamente vía `WhiteNoise` con compresión y caché.
