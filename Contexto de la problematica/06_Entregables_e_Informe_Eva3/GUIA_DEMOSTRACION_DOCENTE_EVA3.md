# GUÍA RÁPIDA DE DEMOSTRACIÓN DOCENTE — EVALUACIÓN SUMATIVA #3 (30%)
## Programación Back End (TI3041) · SGR Ilustre Municipalidad de La Serena

Esta guía está diseñada para que el estudiante realice una **demostración presencial fluida, profesional y estructurada** ante el docente, cumpliendo el 100% de la pauta y la condición obligatoria de **no utilizar Django Admin** durante la presentación.

---

## 🔑 Credenciales Rápidas para la Demostración

| Perfil / Nivel de Acceso | Usuario | Contraseña | Cargo Institucional | Función a Demostrar |
| :--- | :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin` | Administrador General | Acceso total, 6 Mantenedores CRUD, crear usuario y asignar Grupo de Django. |
| **Supervisor** | `coordinador` | `admin` | Coordinador Municipal | Supervisión de metas, semáforo SGR, Tubo de compromisos, restricción a usuarios. |
| **Administrativo** | `operador_d01` | `admin` | Funcionario Operador | Ventanilla: Ingreso de Atención Ciudadana con folio único, derivaciones. |
| **Administrativo (Territorial)** | `operador_d02` | `admin` | Funcionario Territorial | Dashboard especializado en terreno y evidencias. |
| **Administrativo (DISERCO)** | `diserco` | `admin` | Funcionario DISERCO | Dashboard especializado en servicios comunitarios. |

* **URL en Producción (AWS EC2):** `http://3.229.11.31:8000/`  
* **URL en Local:** `http://localhost:8000/`

---

## 📋 Guion de Demostración Paso a Paso (10 a 15 Minutos)

### Paso 1: Recuperación de Contraseña por Correo Real y Código PIN (15 pts)
> **Punto clave para el docente:** Demostrar que el correo sale en vivo a través de un servidor SMTP real de Gmail y que la pantalla obliga al usuario a abrir su buzón para obtener el código PIN de 6 dígitos.

1. Ir a la pantalla de Login (`/login/`).
2. Clic en **"¿Olvidó su contraseña?"** (`/recuperar/`).
3. Ingresar el correo del administrador: `emanuelseron2003@gmail.com`.
4. Clic en **"Enviar Código de Verificación"**.
5. **Mostrar al docente:**
   - La pantalla redirige inmediatamente a `/recuperar/validar/` mostrando los 6 casilleros numéricos interactivos.
   - *No hay ningún código visible en la pantalla* (se eliminó cualquier modo demo).
6. Abrir la bandeja de entrada de Gmail (`emanuelseron2003@gmail.com`) en otra pestaña:
   - Mostrar el correo recibido de `SGR Municipalidad de La Serena <emanuelromanseron@gmail.com>`.
   - Mostrar el diseño institucional formal y el **Código de seguridad de 6 dígitos**.
   - (Mencionar que el correo también incluye un botón con token criptográfico seguro de un solo uso).
7. Escribir los 6 dígitos en los casilleros de la pantalla web.
8. Ingresar la nueva contraseña y confirmar. Se muestra el mensaje de confirmación exitosa y redirige al Login.

---

### Paso 2: Autenticación y Tres Dashboards Diferenciados (25 pts)
> **Punto clave para el docente:** Cada grupo de Django y cargo institucional ve un panel adaptado a su responsabilidad legal y funcional.

1. **Iniciar sesión como `admin` (Administrador General):**
   - Mostrar el encabezado: **DASHBOARD ADMINISTRADOR**.
   - Mostrar acceso a los **6 Mantenedores CRUD**, gestión de usuarios y enlaces estructurales comunales.
2. **Cerrar sesión e iniciar como `coordinador` (Supervisor):**
   - Mostrar el encabezado: **DASHBOARD SUPERVISOR**.
   - Mostrar que tiene acceso a:
     * Semáforo General e Informe Ejecutivo de Metas SGR.
     * Tablero Kanban del Tubo de Compromisos.
     * Catálogos autorizados de consulta (Delegaciones, Metas, Tipos de Atención).
   - Mostrar que **NO** tiene acceso a crear usuarios ni mantenedor de roles.
3. **Cerrar sesión e iniciar como `operador_d01` (Administrativo):**
   - Mostrar el encabezado: **DASHBOARD ADMINISTRATIVO — FUNCIONARIO OPERADOR**.
   - Mostrar el panel enfocado en recepción de vecinos: botón directo `+ Nueva Atención` y `Libro de Atenciones`.
   - (Opcional) Iniciar sesión como `diserco` para mostrar cómo el panel se adapta automáticamente a Servicios Comunitarios.

---

### Paso 3: Restricción Funcional y Seguridad en Vistas (15 pts)
> **Punto clave para el docente:** Demostrar que la seguridad no es solo visual, sino que está blindada a nivel de vista en Django.

1. Estando con la sesión de `operador_d01` (Administrativo), intentar ingresar directamente por URL a:
   `http://localhost:8000/mantenedores/usuarios/` (o en EC2).
2. **Resultado esperado:**
   - El sistema intercepta la petición.
   - Bloquea el acceso y redirige al usuario.
   - Muestra el mensaje de alerta: **"Acceso restringido: Se requieren permisos de nivel Administrador"**.

---

### Paso 4: Mantenedor CRUD de Usuarios y Asignación de Grupos Django (20 pts)
> **Punto clave para el docente:** Demostrar la gestión de usuarios y asignación de Grupos nativos de Django (`django.contrib.auth.models.Group`) 100% mediante Django Templates.

1. Iniciar sesión como `admin`.
2. Ir a **Gestión de Usuarios** (`/mantenedores/usuarios/`).
3. Mostrar la tabla con búsqueda insensible, paginación y la columna destacada **"Perfil / Grupo (Eva #3)"** con badges de color.
4. Clic en **"+ Nuevo Usuario"**:
   - Completar: `username`, `nombre`, `apellido`, `email`, `contraseña`.
   - Mostrar el selector **"Perfil de Acceso / Grupo Django *"**:
     * Seleccionar `Supervisor` o `Administrativo`.
   - Guardar el usuario.
5. Verificar que el usuario aparece en la lista con su grupo asignado correctamente.
6. Demostrar la **exportación a Excel (.xlsx)** del listado con un solo clic.

---

### Paso 5: Transacción Operacional — Atención Ciudadana (10 pts)
> **Punto clave para el docente:** Demostrar el funcionamiento de una transacción compleja entre múltiples modelos (`AtencionCiudadana`, `Vecino`, `Subatencion`, `Delegacion`).

1. Ir a **Atención Ciudadana** -> **+ Nueva Atención** (`/atenciones/nueva/`).
2. Ingresar RUT del vecino (cuenta con búsqueda automática de vecino registrado).
3. Mostrar los **selectores dependientes en cascada**:
   - Seleccionar "Tipo de Atención" (ej. *Atención Social y Beneficios*).
   - Mostrar cómo el combo "Subatención" se filtra automáticamente vía API interna mostrando solo las opciones pertinentes.
4. Completar la descripción y guardar.
5. Mostrar cómo el sistema genera automáticamente el **Folio Correlativo Institucional único** (`ATC-XXXXX`), asigna la delegación activa y guarda la transacción de forma atómica.

---

### Paso 6: Infraestructura Cloud AWS EC2 y GitHub (8 pts)
1. Mostrar la URL en AWS EC2 corriendo en vivo: `http://3.229.11.31:8000/`.
2. Mostrar la terminal de AWS con el servicio activo: `sudo systemctl status sgr-django.service`.
3. Mostrar el repositorio GitHub `https://github.com/iScreamyy6/Backend` con los commits organizados por funcionalidad.
4. Ejecutar el script automatizado de pruebas:
   ```bash
   python test_suite.py
   ```
   Mostrar la salida final: **`[EXITO COMPLETO EVALUACIÓN #3] AUTENTICACIÓN, GRUPOS, RECUPERACIÓN POR TOKEN, DASHBOARDS Y RESTRICCIONES AL 100%`**.
