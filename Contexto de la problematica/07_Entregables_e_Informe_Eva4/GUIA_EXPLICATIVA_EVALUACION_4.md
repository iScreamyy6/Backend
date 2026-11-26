# GUÍA EXPLICATIVA DEFINITIVA: EVALUACIÓN SUMATIVA #4
## Entendiendo la API RESTful, JWT, Swagger y el SGR desde Cero

**Asignatura:** Programación Back End (TI3V41) — INACAP La Serena  
**Docente:** Alex Díaz Araos  
**Proyecto:** Sistema de Gestión de Resultados (SGR) — Municipalidad de La Serena  

---

## 1. ¿QUÉ ES LO QUE HABÍA QUE HACER? (EL OBJETIVO DE LA EVALUACIÓN)

Hasta la Evaluación #3, todo lo que construiste en Django era una **página web tradicional**:
* El usuario entraba con un navegador a `http://localhost:8000/login/`.
* Django leía la base de datos, armaba un archivo HTML con botones y colores en el servidor (`templates/`), y se lo enviaba al navegador.
* Si mañana la Municipalidad de La Serena quiere crear una **aplicación móvil para Android o iPhone** para que los funcionarios en terreno suban fotos de baches o podas, o si el Gobierno Regional quiere consultar datos de las delegaciones, **un archivo HTML no les sirve**. Una app móvil o un sistema externo necesita **datos puros (texto estructurado en formato JSON)**, sin diseño ni colores.

El objetivo de la **Evaluación Sumativa #4** fue precisamente ese:
> **Convertir tu sistema en un proveedor de datos mediante una API RESTful**, para que cualquier aplicación (móvil, web, o software externo) pueda conectarse de forma segura, autenticarse con un token digital (JWT) y consultar o guardar información en el SGR.

---

## 2. CONCEPTOS CLAVE EXPLICADOS DE FORMA SIMPLE

### A. ¿Qué es una API RESTful? (La analogía del restaurante)
Imagina que vas a un restaurante:
* Tú eres el **Cliente** (el navegador web o la app móvil de la municipalidad).
* La cocina es el **Servidor y la Base de Datos** (donde están guardadas las 24 gestiones, los vecinos y las delegaciones).
* Tú no puedes entrar directamente a la cocina a cocinar ni a revisar los refrigeradores.
* Por eso existe el **Mozo / Mesero**: esa es la **API**.
* El mozo te pasa la carta con opciones bien definidas:
  * **GET** = *"Mozo, tráigame la lista de delegaciones"* (Solo leer datos).
  * **POST** = *"Mozo, quiero crear una nueva gestión"* (Guardar un nuevo plato en la cocina).
  * **PUT / PATCH** = *"Mozo, cámbieme el estado de esta gestión de Pendiente a Realizado"* (Modificar datos existentes).
  * **DELETE** = *"Mozo, elimine este registro que está duplicado"* (Borrar datos).
* Y la respuesta que te entrega el mozo no es un plato pintado en HTML, sino un formato liviano llamado **JSON** (que son datos en texto plano organizados con llaves `{ "nombre": "Las Compañías", "estado": "Activa" }`).

---

### B. ¿Qué es un Token JWT? (La pulsera VIP de un concierto)
En una página web normal, cuando inicias sesión, el servidor guarda una "sesión" en su memoria o en una cookie. Pero en las APIs modernas esto no escala bien si hay miles de celulares haciendo consultas por segundo.

Aquí entra **JWT (JSON Web Token)**:
* Funciona igual que la **pulsera que te ponen en un festival o en un hotel resort**:
  1. Vas a la entrada (`/api/token/`) y muestras tu carnet con usuario y contraseña (`admin` / `admin`).
  2. El portero valida tus datos y te coloca una **pulsera sellada e infalsificable** (un texto largo y cifrado llamado **Access Token**).
  3. A partir de ese momento, cada vez que vas a la barra a pedir algo (`/api/v1/gestiones/`), ya no muestras tu carnet de identidad; solo muestras tu pulsera en la cabecera de la petición (`Authorization: Bearer <tu_token>`).
  4. La pulsera dura **60 minutos**. Si vence, tienes una contraseña de reemplazo (**Refresh Token**) que te da una pulsera nueva sin tener que volver a escribir tu usuario y contraseña.

---

### C. ¿Qué es Swagger UI? (El catálogo interactivo de pruebas)
Normalmente, para probar una API se usan programas externos como Postman o Insomnia.
El docente Alex Díaz pidió en la pauta que la API tuviera **Swagger UI**:
* Swagger es una **página web interactiva** generada automáticamente en `/api/swagger/` (o `/api/docs/`).
* Te muestra todos los botones de la API ordenados por carpetas.
* Tiene un botón verde arriba a la derecha que dice **Authorize**: ahí pegas tu pulsera (el Token JWT).
* Puedes hacer clic en `GET /api/v1/delegaciones/`, presionar el botón azul **Execute**, y verás la respuesta real de tu base de datos de MySQL en milisegundos, sin salir del navegador.

---

## 3. ¿QUÉ SE HIZO EXACTAMENTE EN EL PROYECTO?

Siguiendo la rúbrica del profesor al pie de la letra, se implementaron los siguientes componentes:

### 1. Se creó una nueva aplicación Django llamada `api/`
En la raíz de tu proyecto ahora existe la carpeta [api/](file:///d:/Django/Backend/api/) con sus archivos ordenados:
* `apps.py`: Registra la aplicación en el sistema.
* `urls.py`: Define los caminos (rutas) de la API (`/api/token/`, `/api/swagger/`, `/api/v1/...`).
* `permissions.py`: Reglas de seguridad (quién puede borrar, quién puede editar).
* `serializers.py`: Los traductores que convierten los modelos de la base de datos a formato JSON.
* `views.py`: Los controladores (`ModelViewSet`) que reciben la orden del cliente, la procesan y devuelven la respuesta.

### 2. Se implementaron los 2 Mantenedores requeridos por la rúbrica
* **Mantenedor N° 1: Delegaciones Municipales (`/api/v1/delegaciones/`):**
  * Permite consultar, crear, modificar y eliminar las delegaciones de La Serena (Centro, Las Compañías, La Antena, Rural, etc.).
  * Si entra un operador normal, puede ver las delegaciones. Pero si intenta borrar o crear una, el sistema le dice `403 Forbidden` (Prohibido: solo el Administrador puede).
* **Mantenedor N° 2: Vecinos y Padrón Comunal (`/api/v1/vecinos/`):**
  * Permite consultar, crear y actualizar los datos de los vecinos que piden ayudas o hacen trámites en el municipio.

### 3. Se implementó la Transacción Central del Negocio
* **Gestiones y Actividades Territoriales (`/api/v1/gestiones/`):**
  * Es el núcleo del SGR. Permite registrar solicitudes ciudadanas, derivarlas al Tablero Kanban de Tubo de Trabajo y adjuntar códigos de evidencia fotográfica.

### 4. La exigencia más importante del profesor: "Serializadores Diferenciados" (Protección de Datos)
El profesor Alex Díaz puso una regla estricta en la página de requisitos:
> *"El perfil Administrador debe ver todos los datos sensibles, pero el perfil Usuario/Operador estándar NO debe ver teléfonos privados, correos personales ni notas internas de auditoría."*

¿Por qué se pide esto? Por la **Ley N° 19.628 de Protección de la Vida Privada** en Chile. Un funcionario normal que atiende en ventanilla no debe tener acceso libre a los correos o celulares privados de los vecinos para evitar mal uso o filtraciones.

Para cumplir esto, en `api/serializers.py` se crearon **dos versiones de serializador**:
1. **Para el Administrador (`VecinoAdminSerializer`):**
   * Muestra el RUT real: `15.987.654-3`
   * Muestra el teléfono real: `+56912345678`
   * Muestra el correo real: `carlos.vecino@gmail.com`
   * En Gestiones, muestra las notas secretas de revisión interna de las evidencias.
2. **Para el Operador / Usuario Normal (`VecinoPublicSerializer`):**
   * El RUT aparece censurado automáticamente: `15.***.***-3`
   * El teléfono aparece oculto: `+56 9 ****-****`
   * El correo aparece enmascarado: `c****@gmail.com`
   * En Gestiones, las notas de auditoría y revisión interna quedan **completamente eliminadas** del JSON.

El sistema detecta automáticamente quién está usando el token JWT: si es el Administrador le manda el JSON completo; si es un funcionario normal le manda el JSON censurado.

---

## 4. CÓMO PROBAR Y DEMOSTRAR TODO ESTO PASO A PASO (GUÍA PARA TU EVALUACIÓN)

Cuando el profesor te pida mostrar la API o explicarla, sigue estos 4 pasos sencillos:

### Paso 1: Pedir el Token JWT
1. Abre tu navegador y ve a:
   `http://localhost:8000/api/token/` (o en la IP de AWS si está activa).
2. Verás una pantalla con un formulario. Escribe:
   * **username:** `admin`
   * **password:** `admin` (o tu clave de administrador).
3. Presiona el botón **POST**.
4. En pantalla aparecerá la respuesta con dos textos largos:
   * `"access"`: Ese es tu Token JWT (tu pulsera VIP).
   * `"refresh"`: El token de renovación.
5. Copia todo el texto largo del campo `"access"` (sin las comillas).

### Paso 2: Abrir la Documentación de Swagger
1. En tu navegador ve a:
   `http://localhost:8000/api/swagger/` (o `/api/docs/`).
2. Verás la pantalla oficial de **Swagger UI** con el título del SGR de La Serena y todos los endpoints ordenados:
   * *Mantenedor 1: Delegaciones*
   * *Mantenedor 2: Vecinos / Padrón*
   * *Transacción: Gestiones Municipales*
   * *Token*

### Paso 3: Autorizar la sesión con el Token
1. Arriba a la derecha haz clic en el botón verde con candado que dice **Authorize**.
2. En el cuadro que dice **Value**, escribe:
   `Bearer <pega_aqui_el_token_que_copiaste>`
   *(Ejemplo: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)*
3. Haz clic en el botón **Authorize** dentro del modal y luego en **Close**. El candado ahora aparecerá cerrado (indicando que estás autenticado como Administrador).

### Paso 4: Probar una consulta real
1. Haz clic en `GET /api/v1/delegaciones/`.
2. Haz clic en el botón blanco **Try it out**.
3. Haz clic en el botón azul grande **Execute**.
4. ¡Listo! Abajo verás `Response body` con código `200 OK` y la lista de delegaciones reales de tu base de datos de MySQL.
5. Repite lo mismo con `GET /api/v1/vecinos/` o `GET /api/v1/gestiones/`.

---

## 5. TABLA RESUMEN DE LOS ARCHIVOS DEL PROYECTO

| Archivo | ¿Dónde está? | ¿Para qué sirve? |
|---|---|---|
| [api/serializers.py](file:///d:/Django/Backend/api/serializers.py) | Carpeta `api/` | Convierte los modelos a JSON y censura los datos sensibles (RUT, teléfono, correo) para usuarios que no son Admin. |
| [api/views.py](file:///d:/Django/Backend/api/views.py) | Carpeta `api/` | Controladores que reciben los pedidos GET, POST, PUT, DELETE y deciden qué serializador entregar según el rol. |
| [api/urls.py](file:///d:/Django/Backend/api/urls.py) | Carpeta `api/` | Conecta las URLs (`/api/token/`, `/api/swagger/`, `/api/v1/...`) con las vistas. |
| [api/permissions.py](file:///d:/Django/Backend/api/permissions.py) | Carpeta `api/` | Define que solo el Administrador puede borrar o crear delegaciones (`403 Forbidden` para los demás). |
| [test_api.py](file:///d:/Django/Backend/test_api.py) | Raíz del proyecto | Script automático con 6 pruebas que verifican tokens, bloqueos 401, permisos 403 y censura de datos sensibles (100% aprobado). |
| [INFORME_TECNICO_SGR_EVALUACION_4.pdf](file:///d:/Django/Backend/INFORME_TECNICO_SGR_EVALUACION_4.pdf) | Raíz del proyecto | El informe técnico formal compilado en PDF listo para entregar al profesor Alex Díaz Araos. |

---

## 6. CONCLUSIÓN

Tu sistema ahora cuenta con:
1. Una **interfaz web administrativa** completa (Evaluaciones 1, 2 y 3).
2. Una **API RESTful moderna, segura y documentada** (Evaluación 4).
3. **Cero deuda técnica:** Todas las pruebas pasan al 100% y el código cumple con los más altos estándares exigidos por la institución.
