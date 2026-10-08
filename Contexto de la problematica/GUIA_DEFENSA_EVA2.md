# 🎯 Guía de Defensa y Revisión Presencial — Evaluación Sumativa #2
**Asignatura:** Programación Back End (TI3041)  
**Docente:** Alex Díaz Araos  
**Proyecto:** Sistema de Gestión de Resultados (SGR) — Ilustre Municipalidad de La Serena  
**Integrantes:** Álvaro Obregón / Benjamín Antipa  

---

## 🔑 1. Credenciales y Enlaces Rápidos

Ten estos accesos a mano antes de comenzar la revisión presencial:

| Servicio | URL / Comando | Credenciales |
|---|---|---|
| **🌐 Aplicación Web SGR** | [http://3.229.11.31/](http://3.229.11.31/) | Acceso público directo *(puerto 80)* |
| **⚙️ Django Admin** | [http://3.229.11.31/admin/](http://3.229.11.31/admin/) | **Usuario:** `admin`<br>**Contraseña:** `admin123` |
| **🗄️ phpMyAdmin** | [http://3.229.11.31/phpmyadmin/](http://3.229.11.31/phpmyadmin/) | **Usuario:** `sgr_user`<br>**Contraseña:** `Municipalidad2026!` |
| **🐙 Repositorio GitHub** | [https://github.com/iScreamyy6/Backend](https://github.com/iScreamyy6/Backend) | Repositorio público |
| **💻 Conexión SSH a EC2** | `ssh -i "SGR-Municipalidad.pem" ubuntu@3.229.11.31` | Llave privada `.pem` |

---

## 📋 2. Guía de Presentación Paso a Paso

### 🔹 Paso 1: Demostrar Infraestructura en AWS EC2
> **Qué te pedirá el evaluador:** *"Conéctate a tu máquina en AWS y muéstrame el entorno operativo"*.

1. **Abrir terminal** (PowerShell o Git Bash) en la carpeta donde tienes la llave `.pem` y conectarte:
   ```bash
   ssh -i "SGR-Municipalidad.pem" ubuntu@3.229.11.31
   ```
2. **Entrar a la carpeta del proyecto y activar el entorno virtual:**
   ```bash
   cd SGR-Municipalidad
   source venv/bin/activate
   ```
3. **Mostrar el estado del servicio web:**
   ```bash
   sudo systemctl status sgr-django
   ```
4. **Verificar memoria y estabilidad (Swap de 2 GB implementado):**
   ```bash
   free -m
   ```
   * **Qué explicar:** *"Profesor, la aplicación se ejecuta en una instancia Linux de AWS EC2 gestionada en segundo plano con `systemd` (`sgr-django.service`). Además, configuramos Apache como proxy inverso para servir el sitio en el puerto estándar 80 junto con phpMyAdmin, y habilitamos 2 GB de memoria SWAP para garantizar alta disponibilidad y evitar saturación de memoria"*.

---

### 🔹 Paso 2: Control de Versiones con Git y GitHub
> **Qué te pedirá el evaluador:** *"Muéstrame el repositorio y el historial de commits"*.

1. **En la terminal de la EC2, demostrar origen y commits:**
   ```bash
   git remote -v
   git log --oneline -n 6
   ```
2. **En el navegador abrir el repositorio GitHub:**
   * Abrir: [https://github.com/iScreamyy6/Backend](https://github.com/iScreamyy6/Backend)
   * Mostrar el archivo `README.md` (con la arquitectura, integrantes y pasos de despliegue).
   * Mostrar el archivo `.gitignore`.
   * **Qué explicar:** *"Profesor, el repositorio mantiene el historial evolutivo del proyecto. Mediante el `.gitignore` protegemos la seguridad del entorno excluyendo las llaves `.pem`, archivos de base de datos local y el archivo `.env` con las contraseñas"*.

---

### 🔹 Paso 3: Variables de Entorno y Migraciones (Back-End)
> **Qué te pedirá el evaluador:** *"¿Dónde guardas las credenciales sensibles y cómo manejas las migraciones?"*.

1. **Mostrar el archivo `.env` en el servidor:**
   ```bash
   cat .env
   ```
2. **Mostrar cómo se carga en `settings.py`:**
   * En `Municipalidad/settings.py` se utiliza `python-dotenv`:
     ```python
     load_dotenv(BASE_DIR / '.env')
     ```
3. **Demostrar las migraciones ejecutadas con Django ORM:**
   ```bash
   python manage.py showmigrations
   ```
   * Verá todas las migraciones del sistema y de las apps con su marca `[X]`.
   * **Qué explicar:** *"Profesor, la persistencia se desacopló completamente de archivos JSON. Usamos Django ORM con `db_table` para mapear directamente las tablas de nuestro modelo relacional, aplicando migraciones consistentes"*.

---

### 🔹 Paso 4: Evidencia Física en phpMyAdmin
> **Qué te pedirá el evaluador:** *"Abre phpMyAdmin y muéstrame las tablas y sus relaciones físicas"*.

1. Abrir en el navegador: **[http://3.229.11.31/phpmyadmin/](http://3.229.11.31/phpmyadmin/)**
2. Iniciar sesión:
   * **Usuario:** `sgr_user`
   * **Contraseña:** `Municipalidad2026!`
3. En el menú izquierdo seleccionar la base de datos **`sgr_municipalidad`**.
4. **Mostrar las 8 tablas físicas:**
   * `delegaciones`
   * `funcionarios`
   * `actividades`
   * `evidencias`
   * `compromisos_tubo`
   * `periodos_evaluacion`
   * `metas_funcionario`
   * `indicadores_delegacion`
5. **Mostrar el Diseñador Relacional (MER):**
   * Hacer clic en la pestaña superior **Más** → **Diseñador** (*Designer*).
   * Mostrar el diagrama visual de entidades enlazadas mediante sus claves foráneas (`FOREIGN KEY`).
6. Hacer clic en cualquier tabla (ej: `delegaciones` o `actividades`) para mostrar los datos almacenados físicamente.

---

### 🔹 Paso 5: Demostración de CRUD en Django Admin
> **Qué te pedirá el evaluador:** *"Realiza una operación de Crear, Buscar, Modificar y Eliminar en Django Admin"*.

1. Abrir en el navegador: **[http://3.229.11.31/admin/](http://3.229.11.31/admin/)**
2. Iniciar sesión:
   * **Usuario:** `admin`
   * **Contraseña:** `admin123`
3. **Demostrar las 5 capacidades evaluadas:**
   * **Visualizar y Filtrar:** Entrar a *Delegaciones* o *Actividades*. Mostrar las columnas personalizadas (`list_display`) y los filtros laterales por estado/ámbito (`list_filter`).
   * **Buscar:** Escribir en la barra de búsqueda superior (ej: "Compañías" o "Terreno") y presionar Enter (`search_fields`).
   * **Navegar relaciones (Inlines):** Al abrir una Delegación, mostrar que abajo aparecen sus funcionarios asociados listos para administrar mediante `TabularInline`.
   * **Crear (Create):** Hacer clic en **Añadir delegación** (`+`), completar el formulario y guardar.
   * **Modificar (Update):** Cambiar el nombre o responsable de un registro y guardar cambios.
   * **Eliminar (Delete):** Seleccionar un registro de prueba y confirmar su eliminación.

---

### 🔹 Paso 6: Front-End y Botones de Acción (Vistas Públicas)
> **Qué te pedirá el evaluador:** *"Muéstrame el sitio web y los controles CRUD en los listados"*.

1. Abrir en el navegador: **[http://3.229.11.31/](http://3.229.11.31/)**
2. Navegar por los 4 módulos:
   * **Organización (`/organizacion/`):** Delegaciones territoriales y nómina de personal (`/organizacion/personas/`).
   * **Actividades (`/actividades/`):** Libro de gestiones y bandeja de evidencias (`/actividades/evidencias/`).
   * **Agenda (`/agenda/`):** Compromisos intersectoriales y tablero (`/agenda/resumen/`).
   * **Resultados (`/resultados/`):** Semáforo de cumplimiento y tableros por delegación (`/resultados/tablero/1/`).
3. **Demostrar los 4 Botones de Acción exigidos por la pauta en cada listado:**
   * En la barra superior de cada vista:
     * Botón **🔍 Buscar** (caja de texto y botón con filtro funcional).
     * Botón **➕ Agregar** (enlaza al formulario de creación del modelo).
   * En cada fila o tarjeta de la lista:
     * Botón **✏️ Modificar** (enlaza directamente al formulario de edición en el admin).
     * Botón **🗑️ Eliminar** (enlaza a la confirmación de eliminación).
   * **Qué explicar:** *"Profesor, cumpliendo las directrices de la Evaluación 2, cada vista incorpora visualmente los 4 controles CRUD para preparar la integración completa de cara a la Evaluación 3"*.

---

## 🧠 3. Evidencias de Inteligencia Artificial (Para el Informe Técnico)

Si te consultan sobre el uso de herramientas de IA durante el desarrollo:
* **Prompt 1 (Modelado Relacional y MER):** *"Genera un script SQL DDL/DML para MySQL con motor InnoDB, claves foráneas y comentarios para un sistema de gestión territorial de 8 entidades con las siguientes reglas de negocio..."*
* **Prompt 2 (Evolución de modelos en Django ORM):** *"Mapea los modelos de Django en 4 aplicaciones desacopladas utilizando `db_table` para que apunten a las tablas del script SQL sin alterar la integridad referencial..."*
* **Prompt 3 (Despliegue y optimización en EC2):** *"Configura WhiteNoise y un proxy inverso en Apache para servir archivos estáticos con compresión en producción (`DEBUG=False`) en conjunto con phpMyAdmin..."*

---

> [!TIP]
> **Checklist final antes de pasar a la mesa:**
> 1. Asegúrate de que la instancia esté en estado **"Running"** en la consola de AWS.
> 2. Verifica que puedas abrir `http://3.229.11.31/` y `http://3.229.11.31/phpmyadmin/` desde el navegador de tu notebook o celular.
