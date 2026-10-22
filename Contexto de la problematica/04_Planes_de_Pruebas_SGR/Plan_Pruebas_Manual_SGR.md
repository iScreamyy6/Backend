# Plan de Pruebas Manual — SGR Segunda Evaluación
**URL base:** http://3.229.11.31  
**Fecha:** 18-10-2026

---

## Antes de empezar

Abre el navegador en modo **ventana normal** (no incógnito) y ten a mano estas credenciales:

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin` | Administrador (todas las delegaciones) |
| `operador_d01` | `admin` | Operador (solo D01) |
| `operador_d02` | `admin` | Operador (solo D02) |

---

## BLOQUE 1 — Acceso al Sistema
**Tiempo estimado: 5 minutos**

### 1.1 Login correcto
1. Ve a → **http://3.229.11.31/login/**
2. Ingresa usuario `admin` y contraseña `admin`
3. Haz clic en **Ingresar**
4. ✅ **Esperado:** Redirige al dashboard (`/`). En la barra superior aparece **"Ilustre Municipalidad de La Serena"**, el nombre **admin** y su rol. El badge de delegación activa es visible.

### 1.2 Login con credenciales incorrectas
1. Cierra sesión (clic en **[Cerrar Sesión]**)
2. Ve a `/login/` e ingresa usuario `admin` con contraseña `mala123`
3. ✅ **Esperado:** Permanece en `/login/`. Aparece mensaje de error. **No hay redirección al dashboard.**

### 1.3 Campos vacíos
1. En `/login/`, haz clic en **Ingresar** sin completar nada
2. ✅ **Esperado:** El navegador señala los campos obligatorios. No se hace petición al servidor.

### 1.4 Ruta protegida sin sesión
1. Sin iniciar sesión, ve directamente a → **http://3.229.11.31/mantenedores/delegaciones/**
2. ✅ **Esperado:** Redirige automáticamente a `/login/`. No se muestra contenido protegido.

### 1.5 Logout y protección post-cierre
1. Inicia sesión con `admin`
2. Cierra sesión
3. Presiona el botón **Atrás** del navegador
4. ✅ **Esperado:** No recupera la sesión. Redirige o muestra la página de login.

---

## BLOQUE 2 — Recuperación de Contraseña
**Tiempo estimado: 8 minutos**

### 2.1 Solicitar código
1. Ve a → **http://3.229.11.31/recuperar/**
2. Ingresa el correo **de la cuenta admin** (el que aparece en `/admin/`)
3. ✅ **Esperado:** Mensaje genérico tipo *"Si el correo existe, recibirás un código"*. No revela si el correo está registrado.

### 2.2 Correo no registrado
1. En `/recuperar/`, ingresa un correo ficticio `noexiste@test.com`
2. ✅ **Esperado:** **Mismo mensaje** que el paso 2.1. No debe decir "correo no encontrado".

### 2.3 Validar código correcto
1. Solicita el código con el correo de admin
2. Ve a → **http://3.229.11.31/recuperar/validar/**
3. Busca el código generado en la sesión (o consúltalo en el admin Django: `/admin/`)
4. Ingresa el código de 6 dígitos en las casillas
5. ✅ **Esperado:** Avanza a la pantalla de nueva contraseña (`/recuperar/nueva-clave/`)

### 2.4 Código incorrecto (3 intentos)
1. Solicita un código nuevo
2. En `/recuperar/validar/`, ingresa `000000` tres veces seguidas
3. ✅ **Esperado:** Tras el tercer intento, el código queda bloqueado o se muestra error de límite.

### 2.5 Nueva contraseña
1. Con el código validado correctamente, en `/recuperar/nueva-clave/`:
   - Ingresa nueva clave `NuevaClave123`
   - Confirma la misma clave
2. ✅ **Esperado:** SweetAlert2 de éxito. Redirige a login.
3. Intenta iniciar sesión con la **clave anterior** `admin` → ❌ debe fallar
4. Inicia sesión con la **clave nueva** `NuevaClave123` → ✅ debe funcionar
5. **Importante:** Cambia la clave de vuelta a `admin` desde el admin Django para no bloquear las demás pruebas

---

## BLOQUE 3 — Los 6 Mantenedores CRUD
**Tiempo estimado: 20 minutos (3-4 min por mantenedor)**

> **Repite este flujo para cada uno de los 6 mantenedores.**

### Flujo estándar por mantenedor

#### Paso A — Crear registro
| Mantenedor | URL | Datos de prueba |
|-----------|-----|----------------|
| Delegaciones | `/mantenedores/delegaciones/crear/` | Código: `D99`, Nombre: `Prueba Norte`, Dirección: `Av. Test 123`, Comuna: `La Serena` |
| Roles | `/mantenedores/roles/crear/` | Código: `ROL-TEST`, Nombre: `Rol de Prueba`, Alcance: `DELEGACION` |
| Usuarios | `/mantenedores/usuarios/crear/` | Usuario: `usuario_prueba`, Email: `test@test.com`, Rol: cualquiera |
| Ítems y Metas | `/mantenedores/items/crear/` | Código: `I-TEST`, Nombre: `Ítem de Prueba` |
| Tipo Atención | `/mantenedores/tipos-atencion/crear/` | Código: `TA-TEST`, Nombre: `Tipo Prueba` |
| Sub Atención | `/mantenedores/subatenciones/crear/` | Código: `SA-TEST`, Nombre: `Sub Prueba`, Tipo: seleccionar uno existente |

1. Completa el formulario con los datos de prueba
2. Clic en **Guardar**
3. ✅ **Esperado:** SweetAlert2 verde de éxito. Aparece el registro en la lista.

#### Paso B — Buscar el registro creado
1. En el buscador del listado escribe el nombre del registro recién creado
2. ✅ **Esperado:** Solo aparece el registro que coincide. El total se actualiza.
3. Prueba buscar en **MAYÚSCULAS** → debe encontrarlo igual.
4. Prueba buscar un texto parcial → debe encontrarlo igual.

#### Paso C — Editar el registro
1. Haz clic en **Editar** en la fila del registro D99 (o el que creaste)
2. Cambia el nombre a `Prueba Norte Editada`
3. Guarda
4. ✅ **Esperado:** SweetAlert2 de éxito. El nuevo nombre aparece en la lista.

#### Paso D — Verificar paginación con filtros
> *(Aplica si hay más de 10 registros en el mantenedor)*
1. Sin filtro, navega a la página 2
2. ✅ **Esperado:** Llega a la página 2 sin perder el contexto.
3. Aplica un filtro de búsqueda desde la página 2
4. ✅ **Esperado:** Vuelve a la página 1 del subconjunto filtrado.

#### Paso E — Exportar a Excel
1. Con o sin filtro activo, haz clic en **Exportar a Excel**
2. ✅ **Esperado:** Se descarga un archivo `.xlsx`
3. Ábrelo y verifica:
   - El número de filas coincide con el contador de registros en pantalla
   - Las columnas tienen cabeceras legibles
   - **No hay columnas de contraseñas ni campos internos**

#### Paso F — Desactivar el registro de prueba
1. Haz clic en **Desactivar** en la fila del registro de prueba
2. Aparece una confirmación SweetAlert2 → confirma
3. ✅ **Esperado:** El estado cambia a `Inactivo` (o desaparece del listado activo).

---

## BLOQUE 4 — Módulo Unificado de Gestiones y Gestor Social
**Tiempo estimado: 12 minutos**

### 4.1 Formulario Unificado con cascada AJAX
1. Inicia sesión con `operador_d01`
2. Ve a → **http://3.229.11.31/actividades/nueva/** (también accesible desde el menú **Gestiones -> Nueva Gestión**)
3. Verifica que el campo **Delegación** aparece completado automáticamente con **D01**
4. Selecciona un **Tipo de Atención** del selector
5. ✅ **Esperado:** El campo **Sub Atención** se actualiza AUTOMÁTICAMENTE con las subatenciones del tipo seleccionado (sin recargar la página)
6. Cambia el tipo de atención a otro distinto
7. ✅ **Esperado:** El campo Sub Atención se limpia y carga las opciones correspondientes al nuevo tipo seleccionado

### 4.2 Registrar gestión estándar con código automático
1. Completa los datos generales:
   - **Solicitante:** `Carlos Gómez Miranda`
   - **RUT:** `12.345.678-9`
   - **Teléfono:** `+56 9 8877 6655`
   - **Correo:** `carlos.gomez@test.cl`
   - **Dirección:** `Av. Las Compañías #450`
   - **Tipo y Sub Atención:** selecciona los cargados en cascada
   - **Descripción / Acción:** `Orientación social y consulta ciudadana presencial`
   - Mantén `Es Gestión Social` en **NO** y `Derivar al Tubo` en **NO**
2. Haz clic en **Guardar Gestión**
3. ✅ **Esperado:** SweetAlert2 de éxito con el código autoincremental asignado (ej. `GES-00001`). Redirige al libro general.

### 4.3 Ficha especializada de Gestor Social (Flujo Multi-etapa)
1. En `/actividades/nueva/`, activa el switch o selector **¿Es Gestión Social?** en **SÍ**
2. ✅ **Esperado:** Se despliega el panel especializado del Gestor Social con los campos de etapas y visitas
3. Completa los datos:
   - **Solicitante:** `Ana Fuentes Castro`
   - **¿Requiere Visita?:** Selecciona **SÍ** e ingresa una fecha programada
   - **Primera Gestión:** Selecciona o escribe `ATENCIÓN SOCIAL A USUARIO PRESENCIAL`
   - **Segunda Gestión:** Selecciona `VISITA TERRENO E INFORME FIBE` con fecha de informe
   - **Tercera Gestión:** Selecciona `ENTREGA BENEFICIO Y MATERIALES`
4. Guarda la gestión
5. ✅ **Esperado:** Se genera un código con prefijo `SOC-XXXXX` (ej. `SOC-00001`). Se guardan las 3 etapas y la programación de visita.

### 4.4 Libro General de Gestiones y Navegación por Pestañas
1. Ve a → **http://3.229.11.31/actividades/**
2. Observa las 5 pestañas en la parte superior:
   - **Todas** (con badge de total global)
   - **Atención** (gestiones regulares)
   - **Territorial** (gestiones de terreno)
   - **Social** (fichas especializadas del Gestor Social)
   - **Tubo** (gestiones derivadas a compromisos)
3. Haz clic en la pestaña **Social**
4. ✅ **Esperado:** La tabla muestra únicamente las gestiones sociales con su código `SOC-XXXXX` y sus indicadores de visita
5. Haz clic en **Exportar a Excel** desde la lista
6. ✅ **Esperado:** Se descarga el archivo `.xlsx` con todas las gestiones filtradas

---

## BLOQUE 5 — Tubo de Trabajo y Tablero Kanban
**Tiempo estimado: 8 minutos**

### 5.1 Derivación al Tubo de Trabajo desde Gestión Unificada
1. Ve a `/actividades/nueva/`
2. Ingresa solicitante `Roberto Valenzuela`
3. En la sección inferior, activa **¿Derivar al Tubo de Trabajo?** en **SÍ**
4. Completa los campos del compromiso:
   - **Fecha Compromiso:** fecha futura (ej. próxima semana)
   - **Área de Apoyo:** `DIDECO / Obras Municipales`
   - **Territorio:** `Sector Centro / Casco Histórico`
5. Haz clic en **Guardar Gestión**
6. ✅ **Esperado:** Se genera la gestión y automáticamente se crea un compromiso en el Tubo con código autoincremental `TUB-XXXXX`. Ambos registros quedan enlazados bidireccionalmente.

### 5.2 Visualización en Tablero Kanban
1. Ve al menú superior y selecciona **Tubo de Trabajo** (o ingresa a **http://3.229.11.31/agenda/resumen/**)
2. ✅ **Esperado:** Se muestra el Tablero Kanban dividido en tres columnas operativas:
   - 🔴 **Pendientes**
   - 🟡 **En Proceso**
   - 🟢 **Realizados**
3. Verifica que en la columna **Pendientes** aparece la tarjeta recién creada con su código `TUB-XXXXX`, el solicitante `Roberto Valenzuela`, territorio y la insignia con el código de la gestión de origen.

### 5.3 Transición de estados en el Tablero Kanban
1. En la tarjeta de `Roberto Valenzuela` en la columna Pendientes, haz clic en el botón **A Proceso**
2. ✅ **Esperado:** La página se actualiza y la tarjeta pasa automáticamente a la columna **En Proceso**
3. Luego, haz clic en el botón verde **✓ Realizar**
4. ✅ **Esperado:** La tarjeta se mueve a la columna **Realizados**. El estado queda persistido en la base de datos sin alterar los datos de la gestión origen.

---

## BLOQUE 6 — Contexto de Delegación e Interfaz
**Tiempo estimado: 5 minutos**

### 7.1 Badge de delegación siempre visible
1. Inicia sesión con `admin`
2. Navega entre diferentes páginas (inicio, delegaciones, atenciones)
3. ✅ **Esperado:** En todas las páginas aparece en la barra superior: el nombre de usuario, su rol, y la delegación activa con su código

### 7.2 Selector de delegación (admin multi-delegación)
1. Con `admin` activo, busca el selector **"Cambiar Delegación..."** en la barra superior
2. Cambia a otra delegación (ej. D02)
3. ✅ **Esperado:** La página se actualiza y el badge muestra la nueva delegación. Los listados se filtran por esa delegación.

### 7.3 Sin selector (operador una sola delegación)
1. Inicia sesión con `operador_d01`
2. ✅ **Esperado:** La barra superior muestra su delegación fija (D01) pero **NO aparece el selector** para cambiarla

### 6.4 Normas gráficas
Verifica visualmente en cualquier página:
- ✅ Color rojo institucional `#AD0000` en cabeceras de tablas y botones primarios
- ✅ Fuente Arial en todos los textos
- ✅ Logo de la Municipalidad en la barra de navegación principal
- ✅ Todas las páginas usan el mismo template (header + sub-nav + footer)

### 6.5 SweetAlert2
1. Realiza cualquier operación de guardado → ✅ aparece alerta verde de éxito
2. Realiza una eliminación → ✅ aparece confirmación antes de borrar
3. Cancela la eliminación → ✅ el registro no se elimina

---

## BLOQUE 7 — Validaciones de Formularios
**Tiempo estimado: 5 minutos**

### 7.1 Campos obligatorios vacíos
1. En cualquier formulario de creación (ej. Crear Delegación), haz clic en **Guardar** sin completar nada
2. ✅ **Esperado:** El navegador o el servidor señalan los campos obligatorios. No se crea ningún registro.

### 7.2 Sub Atención sin Tipo seleccionado
1. En nueva atención, intenta guardar sin seleccionar Tipo de Atención
2. ✅ **Esperado:** Validación que impide guardar sin el Tipo seleccionado

### 7.3 Contraseña débil en recuperación
1. En `/recuperar/nueva-clave/`, ingresa clave `123`
2. ✅ **Esperado:** La clave es rechazada por ser muy corta o débil

---

## Checklist Final de Entrega

Marca cada ítem al completarlo:

- [ ] Inicio de sesión funciona con todos los roles
- [ ] Logout invalida la sesión correctamente
- [ ] Rutas protegidas redirigen a login
- [ ] Flujo de recuperación de contraseña completo (3 pasos)
- [ ] CRUD Delegaciones: crear, editar, buscar, paginar, Excel, desactivar
- [ ] CRUD Roles: crear, editar, buscar, paginar, Excel, desactivar
- [ ] CRUD Usuarios: crear, editar, buscar, paginar, Excel (sin contraseñas), desactivar
- [ ] CRUD Ítems y Metas: crear, editar, buscar, paginar, Excel, desactivar
- [ ] CRUD Tipo de Atención: crear, editar, buscar, paginar, Excel, desactivar
- [ ] CRUD Sub Atención: crear, editar, buscar, cascada verificada, paginar, Excel, desactivar
- [ ] Fusión de Módulos: Gestión Unificada centraliza Atenciones, Terreno y Social
- [ ] Códigos automáticos autoincrementales: GES-XXXXX, SOC-XXXXX, TUB-XXXXX y EVI-YYYYMMDD-XXXX
- [ ] Formulario Unificado: cascada AJAX Tipo -> Sub Atención sin recargar
- [ ] Formulario Unificado: delegación asignada automáticamente según contexto de sesión
- [ ] Gestor Social: ficha multi-etapa especializada (etapas 1, 2, 3, informe FIBE y visitas)
- [ ] Libro General de Gestiones: 5 pestañas de filtrado (Todas, Atención, Territorial, Social, Tubo) con contadores
- [ ] Tubo de Trabajo: derivación automática desde formulario de gestión con código TUB-XXXXX
- [ ] Tablero Kanban: visualización en 3 columnas (Pendientes, En Proceso, Realizados) con badges de origen
- [ ] Tablero Kanban: transición rápida de estados (A Pendiente, A Proceso, Realizar) con persistencia real
- [ ] Badge de delegación visible en todas las páginas
- [ ] Selector de delegación solo aparece para usuarios multi-delegación
- [ ] Normas gráficas (color #AD0000, Arial, logo) aplicadas
- [ ] SweetAlert2 en todas las operaciones CRUD

---

*Toma capturas de pantalla de cada resultado como evidencia para la entrega.*
