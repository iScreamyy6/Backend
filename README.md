# Sistema de Gestión de Resultados (SGR)
## Ilustre Municipalidad de La Serena

**Asignatura:** Programación Back End (TI3041)
**Evaluación:** Sumativa #2 (25%)
**Docente:** Alex Díaz Araos
**Sede:** La Serena
**Carrera:** Ingeniería en Informática / Analista Programador

---

## Integrantes

| Nombre | Rol en el equipo |
|--------|-----------------|
| Álvaro Obregón | Desarrollo Back End / Modelos y Migraciones |
| Benjamín Antipa | Desarrollo Back End / Vistas y APIs |
| Emanuel Román | Desarrollo Back End / Despliegue AWS y Pruebas |

---

## 1. Descripción del Proyecto

El **Sistema de Gestión de Resultados (SGR)** es una aplicación web back-end modular desarrollada con **Django Framework**, orientada a modernizar los procesos de gestión territorial, monitoreo de compromisos y evaluación de desempeño por metas de las delegaciones municipales de La Serena.

Esta segunda entrega incorpora: sistema completo de acceso institucional, recuperación de contraseña con código de 6 dígitos, seis mantenedores CRUD con exportación a Excel y el módulo de ingreso de atención ciudadana con cascada de catálogos y contexto territorial automático.

### Características principales

- Autenticación institucional con recuperación de clave por código temporal de 6 dígitos
- Seis mantenedores CRUD completos con paginación, búsqueda y exportación a Excel
- Atención ciudadana con selectores en cascada (AJAX), folio correlativo y contexto de delegación
- Identificación visual permanente de delegación activa y rol del usuario en cabecera
- Diseño bajo normas gráficas oficiales de la Municipalidad de La Serena (#AD0000, Arial)
- Alertas y confirmaciones SweetAlert2 en todas las operaciones
- Persistencia relacional en MySQL con ORM Django y migraciones controladas
- Despliegue en AWS EC2 con systemd y WhiteNoise

---

## 2. Arquitectura del Proyecto

```
SGR-Municipalidad/
├── Municipalidad/                    # Configuracion central (settings.py, urls.py, wsgi.py)
│   ├── views_auth.py                 # Login, logout, recuperacion de contraseña (3 pasos)
│   ├── views_mantenedores.py         # 6 CRUDs + atencion ciudadana + AJAX + Excel
│   ├── context_processors.py         # Delegacion activa y rol para todos los templates
│   └── urls.py                       # Enrutamiento completo del proyecto
├── organizacion/                     # Delegaciones, Roles y Perfiles de Usuario
├── actividades/                      # TipoAtencion, SubAtencion y AtencionCiudadana
├── agenda/                           # Compromisos y tablero Kanban
├── resultados/                       # ItemMeta, semaforo y metas ponderadas
├── datos/                            # Script SQL de base de datos inicial
├── static/                           # CSS institucional, imagenes y assets
├── templates/                        # Plantillas HTML con diseno institucional
│   ├── base.html                     # Template base con header, sub-nav y footer
│   ├── inicio.html                   # Dashboard con accesos directos
│   ├── auth/                         # Login, recuperar (3 pantallas)
│   ├── mantenedores/                 # Lista + formulario para los 6 CRUDs
│   └── atenciones/                   # Formulario, lista y detalle de atencion
├── requirements.txt                  # Dependencias del proyecto
├── test_suite.py                     # Suite de pruebas automatizadas
├── .env.example                      # Ejemplo de variables de entorno (sin secretos)
└── manage.py                         # Interfaz de comandos Django
```

---

## 3. Modelo Relacional — Base de Datos MySQL

| Tabla | App Django | Descripcion |
|-------|------------|-------------|
| delegaciones | organizacion | Unidades territoriales: codigo, nombre, direccion, comuna, estado |
| roles | organizacion | Catalogo de perfiles con alcance comunal o por delegacion |
| perfiles_usuarios | organizacion | OneToOne con auth_user: rol, delegacion activa y autorizadas |
| items_metas | resultados | Items de evaluacion cuantitativos y cualitativos |
| tipos_atencion | actividades | Clasificadores de requerimientos ciudadanos |
| sub_atenciones | actividades | Subcategorias dependientes en cascada de tipos de atencion |
| atenciones_ciudadanas | actividades | Registro oficial con folio ATC-XXXXX correlativo unico |
| funcionarios | organizacion | Nomina de funcionarios con control de estado y cargo |
| actividades | actividades | Libro diario de gestiones y atencion en terreno |
| evidencias | actividades | Respaldo documental y fotografico validado |
| compromisos_tubo | agenda | Tubo colectivo de compromisos con juntas de vecinos |
| periodos_evaluacion | resultados | Ciclos temporales de metas y monitoreo |
| metas_funcionario | resultados | Ponderacion, avances e indicadores individuales |
| indicadores_delegacion | resultados | Indicadores consolidados por area y semaforo |

**Relaciones clave:**
- PerfilUsuario → User (OneToOne), Rol (FK), Delegacion (FK + M2M autorizadas)
- SubAtencion → TipoAtencion (FK, cascada de catalogos)
- AtencionCiudadana → TipoAtencion, SubAtencion, Delegacion, User (FK)
- ItemMeta → PeriodoEvaluacion (FK, evaluacion por ciclo)

---

## 4. Variables de Entorno

La configuracion sensible se gestiona mediante python-dotenv y un archivo .env NO incluido en el repositorio.

```ini
# Seguridad Django
SECRET_KEY=tu_clave_secreta_aqui_minimo_50_caracteres
DEBUG=False
ALLOWED_HOSTS=*

# Motor de Base de Datos: sqlite para desarrollo, mysql para produccion
DB_ENGINE=sqlite

# Configuracion MySQL (solo si DB_ENGINE=mysql)
DB_NAME=sgr_municipalidad
DB_USER=sgr_user
DB_PASSWORD=tu_password_aqui
DB_HOST=127.0.0.1
DB_PORT=3306
```

## 5. Instalacion y Ejecucion Local

### Prerrequisitos
- Python 3.10 o superior
- Git
- MySQL 8.x (opcional — solo si se usa DB_ENGINE=mysql)

### Pasos completos

**1. Clonar el repositorio**
```bash
git clone https://github.com/iScreamyy6/Backend.git
cd Backend
```

**2. Crear y activar el entorno virtual**
```bash
python -m venv venv

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Linux/macOS:
source venv/bin/activate
```

**3. Instalar las dependencias**
```bash
pip install -r requirements.txt
```

**4. Configurar las variables de entorno**
```bash
copy .env.example .env    # Windows
cp .env.example .env      # Linux/macOS
```

**5. Aplicar las migraciones**
```bash
python manage.py migrate
```

**6. Cargar datos de prueba**
```bash
python manage.py poblar_datos
```

Este comando crea delegaciones, roles, usuarios de prueba, tipos de atencion y subatenciones de ejemplo.

**7. Recolectar archivos estaticos**
```bash
python manage.py collectstatic --noinput
```

**8. Ejecutar el servidor de desarrollo**
```bash
python manage.py runserver
```

Acceder a: http://127.0.0.1:8000/login/
Panel Admin: http://127.0.0.1:8000/admin/

---

## 6. Despliegue en AWS EC2

### Infraestructura

| Componente | Detalle |
|-----------|---------|
| Instancia | Amazon EC2 — Ubuntu Server 24.04 LTS |
| IP Publica | 3.229.11.31 |
| Acceso SSH | ssh -i "SGR-Municipalidad.pem" ubuntu@3.229.11.31 |
| Base de Datos | MySQL 8.x en la misma instancia |
| Archivos Estaticos | WhiteNoise con compresion (collectstatic) |
| Gestion de Servicio | systemd (sgr-django.service) |
| Directorio del proyecto | /home/ubuntu/SGR-Municipalidad |

### Pasos de actualizacion en el servidor

```bash
ssh -i "SGR-Municipalidad.pem" ubuntu@3.229.11.31
cd ~/SGR-Municipalidad
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart sgr-django
sudo systemctl status sgr-django
```

### URLs de Produccion

| Servicio | URL |
|---------|-----|
| Login / Aplicacion | http://3.229.11.31/login/ |
| Dashboard | http://3.229.11.31/ |
| Django Admin | http://3.229.11.31/admin/ |
| phpMyAdmin | http://3.229.11.31/phpmyadmin/ |
| Repositorio GitHub | https://github.com/iScreamyy6/Backend |

### Gestion del servicio systemd

```bash
sudo systemctl status sgr-django    # Ver estado
sudo systemctl restart sgr-django   # Reiniciar
sudo systemctl stop sgr-django      # Detener
tail -f /home/ubuntu/django.log     # Ver logs en tiempo real
```

---

## 7. Dependencias Principales

| Paquete | Version | Uso |
|---------|---------|-----|
| Django | 5.x | Framework principal |
| mysqlclient | 2.x | Conector MySQL para produccion |
| python-dotenv | 1.x | Variables de entorno desde archivo .env |
| whitenoise | 6.x | Servicio de archivos estaticos en produccion |
| openpyxl | 3.1.x | Exportacion de listados a Excel .xlsx |

Ver listado completo en requirements.txt.

---

## 8. Control de Versiones y Entrega

```bash
git clone https://github.com/iScreamyy6/Backend.git
git log --oneline
```

**Repositorio:** https://github.com/iScreamyy6/Backend
**Rama de entrega:** main
**Commit de entrega:** 3a163e4 — fix: remove all emojis from templates to fix text alignment

---

## 9. Estado de los Modulos — Segunda Evaluacion

| Modulo | Funcion | Estado | Observacion |
|--------|---------|--------|-------------|
| Acceso | Login por usuario o correo | Operativo | Autenticacion real con Django auth |
| Acceso | Logout y cierre de sesion | Operativo | Invalida sesion en servidor |
| Acceso | Rutas protegidas (login_required) | Operativo | Redirige a /login/ si no autenticado |
| Recuperacion | Solicitar codigo de 6 digitos | Operativo | Codigo generado y almacenado en sesion |
| Recuperacion | Validar codigo (vigencia 10 min, 3 intentos, reenvio 45s) | Operativo | Logica completa en views_auth.py |
| Recuperacion | Crear nueva contraseña | Operativo | Invalida codigo y actualiza hash |
| CRUD Delegaciones | Crear, editar, desactivar | Operativo | Persiste en base de datos |
| CRUD Delegaciones | Listar, paginar, buscar | Operativo | Busqueda insensible a mayusculas |
| CRUD Delegaciones | Exportar a Excel | Operativo | Exporta resultado del filtro activo |
| CRUD Roles | Crear, editar, desactivar | Operativo | Persiste en base de datos |
| CRUD Roles | Listar, paginar, buscar | Operativo | Busqueda insensible a mayusculas |
| CRUD Roles | Exportar a Excel | Operativo | Exporta resultado del filtro activo |
| CRUD Usuarios | Crear, editar, desactivar | Operativo | Crea auth_user + PerfilUsuario |
| CRUD Usuarios | Listar, paginar, buscar | Operativo | Busqueda insensible a mayusculas |
| CRUD Usuarios | Exportar a Excel (sin contraseñas) | Operativo | Excluye campos sensibles |
| CRUD Items y Metas | Crear, editar, desactivar | Operativo | Persiste en base de datos |
| CRUD Items y Metas | Listar, paginar, buscar | Operativo | Busqueda insensible a mayusculas |
| CRUD Items y Metas | Exportar a Excel | Operativo | Exporta resultado del filtro activo |
| CRUD Tipo de Atencion | Crear, editar, desactivar | Operativo | Persiste en base de datos |
| CRUD Tipo de Atencion | Listar, paginar, buscar | Operativo | Busqueda insensible a mayusculas |
| CRUD Tipo de Atencion | Exportar a Excel | Operativo | Exporta resultado del filtro activo |
| CRUD Sub Atencion | Crear, editar, desactivar | Operativo | Asociacion FK a TipoAtencion |
| CRUD Sub Atencion | Listar, paginar, buscar | Operativo | Busqueda insensible a mayusculas |
| CRUD Sub Atencion | Exportar a Excel | Operativo | Exporta resultado del filtro activo |
| Atencion Ciudadana | Formulario con cascada AJAX | Operativo | SubAtencion filtra por TipoAtencion via API |
| Atencion Ciudadana | Contexto de delegacion automatico | Operativo | Se toma del perfil del usuario en sesion |
| Atencion Ciudadana | Folio correlativo ATC-XXXXX | Operativo | Generado automaticamente al guardar |
| Atencion Ciudadana | Confirmacion SweetAlert2 post-guardado | Operativo | Muestra folio en alerta de exito |
| Atencion Ciudadana | Libro de atenciones + Excel | Operativo | Listado paginado con exportacion |
| Atencion Ciudadana | Prevencion doble envio | Operativo | Boton se deshabilita tras primer clic |
| Interfaz | Badge delegacion activa en cabecera | Operativo | Codigo + nombre en header siempre visible |
| Interfaz | Badge nombre de usuario y rol | Operativo | Siempre visible cuando hay sesion activa |
| Interfaz | Selector de delegacion (multi-delegacion) | Operativo | Muestra solo delegaciones autorizadas del perfil |
| Interfaz | Normas graficas (#AD0000, Arial) | Operativo | Template base unificado |
| Interfaz | SweetAlert2 en todas las operaciones | Operativo | Exito, error, confirmacion de eliminacion |
| Actividades / Gestiones | Libro de gestiones | Operativo (heredado Eval 1) | No es requisito de esta evaluacion |
| Agenda / Compromisos | Tubo Kanban | Operativo (heredado Eval 1) | No es requisito de esta evaluacion |
| Resultados / Semaforo | Tablero y metas | Operativo (heredado Eval 1) | No es requisito de esta evaluacion |

**Leyenda:**
- **Operativo:** Funcion implementada, probada y con persistencia real en base de datos.
- **Simulado:** Funcion con interfaz visible pero sin persistencia de back-end. (Ninguna en esta entrega)
- **Pendiente:** Funcion no implementada en esta evaluacion. (Ninguna de las exigidas)

---

## 10. Cuentas de Prueba

| Usuario | Contraseña | Rol | Alcance |
|---------|-----------|-----|---------|
| admin | admin | Administrador General | Comunal (todas las delegaciones) |
| coordinador | admin | Coordinador Municipal | Comunal (supervision) |
| delegado_d01 | admin | Delegado Municipal | Las Compañias — D01 |
| operador_d01 | admin | Funcionario Operador | Las Compañias — D01 |
| operador_d02 | admin | Funcionario Operador | La Antena — D02 |

> NOTA: Estas contraseñas son exclusivamente para evaluacion academica.

---

## 11. Instrucciones de Prueba

### Pruebas funcionales rapidas (flujo de evaluacion)

**1. Acceso y recuperacion:**
1. Ir a http://3.229.11.31/login/
2. Iniciar sesion con usuario: admin / contraseña: admin
3. Verificar badge de delegacion y rol en la cabecera
4. Cerrar sesion y probar recuperacion de contraseña en /recuperar/

**2. Los 6 Mantenedores CRUD:**
1. Ir a Mantenedores CRUD en la barra de navegacion
2. En Delegaciones: crear una nueva con codigo D99, editar y desactivar
3. Usar el buscador; verificar filtros persistentes al paginar
4. Descargar Excel y verificar que coincide con la tabla en pantalla
5. Repetir para Roles, Usuarios, Items, Tipo Atencion y Sub Atencion

**3. Ingreso de Atencion Ciudadana:**
1. Ir a Atencion Ciudadana > Nueva Atencion
2. Seleccionar un Tipo de Atencion y verificar que Sub Atencion se actualiza
3. Cambiar el tipo y verificar que Sub Atencion se limpia
4. Completar el formulario y guardar
5. Verificar folio ATC-XXXXX en la confirmacion SweetAlert2
6. Verificar el registro en el Libro de Atenciones con exportacion Excel

**4. Contexto de delegacion:**
1. Iniciar sesion con operador_d01 (acceso solo a D01)
2. Verificar que la nueva atencion queda asociada a D01 automaticamente
3. Verificar que el selector de delegacion no aparece (perfil de una sola delegacion)
4. Iniciar sesion con admin y verificar que puede cambiar delegacion activa

### Prueba de suite automatizada (local)
```bash
python test_suite.py
```

---

## 12. Pruebas de Estres — AWS EC2

Las pruebas de estres se ejecutan en el servidor EC2 usando ApacheBench (ab).

### Ejecutar la prueba
```bash
ssh -i "SGR-Municipalidad.pem" ubuntu@3.229.11.31

# Prueba 1: Login (500 peticiones, 20 concurrentes)
ab -n 500 -c 20 http://127.0.0.1:8000/login/

# Prueba 2: Dashboard (500 peticiones, 20 concurrentes)
ab -n 500 -c 20 http://127.0.0.1:8000/

# Prueba 3: Lista de delegaciones (500 peticiones, 50 concurrentes)
ab -n 500 -c 50 http://127.0.0.1:8000/mantenedores/delegaciones/
```

### Umbrales de aceptacion definidos

| Metrica | Umbral aceptable |
|---------|-----------------| 
| Tasa de error | < 1% |
| Latencia promedio | < 2000 ms |
| Percentil 95 (p95) | < 5000 ms |
| Solicitudes por segundo | > 5 req/s |

### Resultados de ejecucion

| Prueba | Concurrencia | Req/s | Latencia promedio | p95 | Errores |
|--------|-------------|-------|-------------------|-----|---------|
| Login (/login/) | 20 | — | — | — | — |
| Dashboard (/) | 20 | — | — | — | — |
| Lista delegaciones | 50 | — | — | — | — |

---

## 13. Evidencia de Uso de Inteligencia Artificial

Durante el desarrollo se utilizo IA generativa (Google Antigravity / Gemini) como herramienta de apoyo al aprendizaje.

### Caso 1 — Conflicto de migraciones en MySQL (Table already exists)
**Prompt:** "Al ejecutar python manage.py migrate obtengo error Table already exists. Las tablas ya existen por el script SQL. Como aplico solo las migraciones del sistema Django?"
**Respuesta aplicada:** Usar --fake para apps del negocio y aplicar normalmente las del sistema (auth, sessions, contenttypes).

### Caso 2 — Error 500 en Django Admin al iniciar sesion
**Prompt:** "Al entrar al Django Admin me sale Server Error 500 en el POST de /admin/login/. Por que?"
**Respuesta aplicada:** Las tablas django_session y auth_user no existian. Se aplicaron las migraciones del sistema y se creo el superusuario.

### Caso 3 — Propiedad id en modelos con clave primaria personalizada
**Prompt:** "Los modelos tienen id_delegacion = models.AutoField(primary_key=True). Los templates usan objeto.id y los links salen vacios. Como soluciono sin cambiar el esquema?"
**Respuesta aplicada:** Agregar @property def id(self): return self.pk a todos los modelos.

### Caso 4 — Archivos estaticos no cargan en produccion
**Prompt:** "En el servidor EC2 los CSS no cargan con DEBUG=False. Como sirvo estaticos sin Nginx?"
**Respuesta aplicada:** Instalar y configurar WhiteNoise como middleware en settings.py.

### Caso 5 — Idioma y zona horaria del panel de administracion
**Prompt:** "El panel Admin aparece en ingles. Como lo cambio a espanol y configuro la hora de Chile?"
**Respuesta aplicada:** LANGUAGE_CODE = 'es', TIME_ZONE = 'America/Santiago' en settings.py.

### Caso 6 — Selectores en cascada via AJAX (Tipo → Sub Atencion)
**Prompt:** "Necesito que al seleccionar el Tipo de Atencion, el campo Sub Atencion se actualice automaticamente. Como implemento esto sin recargar la pagina?"
**Respuesta aplicada:** Endpoint JSON /api/subatenciones/<tipo_id>/ y fetch en JavaScript del template.

### Caso 7 — Exportacion a Excel con openpyxl
**Prompt:** "Como exporto el resultado de una consulta Django a un archivo Excel descargable desde el navegador?"
**Respuesta aplicada:** openpyxl construye el libro en memoria y se devuelve con HttpResponse con content-type xlsx.

---

## 14. Scripts de Base de Datos

El directorio datos/ contiene:
- script_mysql_sgr.sql — Script completo de creacion de tablas para MySQL

Para poblar datos de prueba:
```bash
python manage.py poblar_datos
```

---

*SGR — Sistema de Gestion de Resultados | Municipalidad de La Serena | Segunda Evaluacion 2026*
