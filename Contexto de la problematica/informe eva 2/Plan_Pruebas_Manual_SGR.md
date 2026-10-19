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

## BLOQUE 4 — Atención Ciudadana
**Tiempo estimado: 10 minutos**

### 4.1 Formulario con cascada AJAX
1. Inicia sesión con `operador_d01`
2. Ve a → **http://3.229.11.31/atenciones/nueva/**
3. Verifica que el campo **Delegación** ya aparece completado con **D01** automáticamente
4. Selecciona un **Tipo de Atención** del selector
5. ✅ **Esperado:** El campo **Sub Atención** se actualiza AUTOMÁTICAMENTE con las subatenciones del tipo seleccionado (sin recargar la página)
6. Cambia el tipo de atención a otro distinto
7. ✅ **Esperado:** El campo Sub Atención se **limpia** y carga las del nuevo tipo

### 4.2 Registrar atención completa
1. Completa todos los campos del formulario:
   - **Solicitante:** Nombre ficticio, ej. `Juan Pérez Test`
   - **Tipo de Atención:** selecciona uno
   - **Sub Atención:** selecciona una (que se haya cargado por AJAX)
   - **Descripción:** `Prueba de registro de atención ciudadana`
2. Haz clic en **Guardar Atención**
3. ✅ **Esperado:** SweetAlert2 con el folio `ATC-XXXXX`. El registro aparece en el libro.

### 4.3 Prevención de doble envío
1. En el formulario completo, haz **doble clic rápido** en el botón Guardar
2. ✅ **Esperado:** Solo se crea un registro (el botón se deshabilita tras el primer clic)

### 4.4 Libro de atenciones
1. Ve a → **http://3.229.11.31/atenciones/**
2. ✅ **Esperado:** Aparece el listado con la atención recién creada y su folio
3. Haz clic en el folio para ver el detalle
4. ✅ **Esperado:** Se muestra la ficha completa con todos los datos

### 4.5 Exportar atenciones a Excel
1. En el listado de atenciones, haz clic en **Exportar a Excel**
2. ✅ **Esperado:** Se descarga el Excel con todas las atenciones registradas

### 4.6 Prueba con operador D02 (aislamiento)
1. Cierra sesión e inicia con `operador_d02`
2. Ve a nueva atención
3. ✅ **Esperado:** La delegación aparece como **D02**, no D01

---

## BLOQUE 5 — Contexto de Delegación e Interfaz
**Tiempo estimado: 5 minutos**

### 5.1 Badge de delegación siempre visible
1. Inicia sesión con `admin`
2. Navega entre diferentes páginas (inicio, delegaciones, atenciones)
3. ✅ **Esperado:** En todas las páginas aparece en la barra superior: el nombre de usuario, su rol, y la delegación activa con su código

### 5.2 Selector de delegación (admin multi-delegación)
1. Con `admin` activo, busca el selector **"Cambiar Delegación..."** en la barra superior
2. Cambia a otra delegación (ej. D02)
3. ✅ **Esperado:** La página se actualiza y el badge muestra la nueva delegación. Los listados se filtran por esa delegación.

### 5.3 Sin selector (operador una sola delegación)
1. Inicia sesión con `operador_d01`
2. ✅ **Esperado:** La barra superior muestra su delegación fija (D01) pero **NO aparece el selector** para cambiarla

### 5.4 Normas gráficas
Verifica visualmente en cualquier página:
- ✅ Color rojo institucional `#AD0000` en cabeceras de tablas y botones primarios
- ✅ Fuente Arial en todos los textos
- ✅ Logo de la Municipalidad en la barra de navegación principal
- ✅ Todas las páginas usan el mismo template (header + sub-nav + footer)

### 5.5 SweetAlert2
1. Realiza cualquier operación de guardado → ✅ aparece alerta verde de éxito
2. Realiza una eliminación → ✅ aparece confirmación antes de borrar
3. Cancela la eliminación → ✅ el registro no se elimina

---

## BLOQUE 6 — Validaciones de Formularios
**Tiempo estimado: 5 minutos**

### 6.1 Campos obligatorios vacíos
1. En cualquier formulario de creación (ej. Crear Delegación), haz clic en **Guardar** sin completar nada
2. ✅ **Esperado:** El navegador o el servidor señalan los campos obligatorios. No se crea ningún registro.

### 6.2 Sub Atención sin Tipo seleccionado
1. En nueva atención, intenta guardar sin seleccionar Tipo de Atención
2. ✅ **Esperado:** Validación que impide guardar sin el Tipo seleccionado

### 6.3 Contraseña débil en recuperación
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
- [ ] Atención: cascada AJAX funciona al cambiar tipo
- [ ] Atención: delegación se asigna automáticamente desde el contexto
- [ ] Atención: folio ATC-XXXXX se genera al guardar
- [ ] Atención: SweetAlert2 muestra el folio tras guardar
- [ ] Libro de atenciones: listado y exportación Excel
- [ ] Badge de delegación visible en todas las páginas
- [ ] Selector de delegación solo aparece para usuarios multi-delegación
- [ ] Normas gráficas (color #AD0000, Arial, logo) aplicadas
- [ ] SweetAlert2 en todas las operaciones CRUD

---

*Toma capturas de pantalla de cada resultado como evidencia para la entrega.*
