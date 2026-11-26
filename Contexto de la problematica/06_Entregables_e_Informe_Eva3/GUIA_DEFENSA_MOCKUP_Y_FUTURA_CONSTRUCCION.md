# GUÍA MAESTRA: CÓMO PRESENTAR EL WIREFRAME Y DEFENDER SU CONSTRUCCIÓN FUTURA (10 MINUTOS)
## INGENIERÍA DE SOFTWARE (TI2043) — EVALUACIÓN SUMATIVA N° 3

---

## 1. EL NÚCLEO DE LA EVALUACIÓN EXPLICADO EN SIMPLE

El docente Alex Díaz Araos exige dos cosas textuales:
> 1. *"Presentar un mockup y/o wireframe (Proyecto Integrado)."*  
> 2. *"Defender su construcción futura en un sistema."*  
> 3. *"Demostración de máximo 10 minutos con orden al azar."*

### ¿Qué significa "defender su construcción futura en un sistema"?
En la industria del software, cuando un ingeniero le presenta un mockup a un cliente o a un comité evaluador, el cliente siempre pregunta:  
* *"Se ve muy bonito en la pantalla, pero ¿cómo sé que esto realmente se puede programar?"*  
* *"¿Cómo se conecta este botón con la base de datos?"*  
* *"¿Cómo evitamos que se caiga el servidor si se conectan 500 funcionarios a la vez?"*  
* *"¿Cómo protegemos los datos de los vecinos según la ley?"*

**Defender su construcción futura** es demostrar técnicamente que tu mockup no es solo un dibujo bonito, sino un plano de ingeniería sólido que se traduce perfectamente a:
1. **Arquitectura de Software:** Capas Frontend (HTML/Bootstrap), Backend (Django / Python) y Base de Datos (MySQL).
2. **Modelo Relacional (MER):** Cómo cada campo del formulario (RUT, nombre, teléfono) viaja a una tabla real en Tercera Forma Normal (3NF).
3. **Patrón de Arquitectura MVT (Model-View-Template):** Cómo las vistas de Django controlan la lógica y entregan los datos.
4. **Seguridad y Ciberseguridad:** Cómo se previene que hackeen el sistema mediante OWASP Top 10 y la Ley 21.459 de delitos informáticos.
5. **Infraestructura Cloud:** Cómo se hospeda en AWS EC2 para atender a todas las delegaciones de La Serena sin servidores locales.

---

## 2. GUÍA DE NAVEGACIÓN EN VIVO DEL WIREFRAME (`/wireframes/`)

Tu proyecto cuenta con el artefacto interactivo oficial en:  
`http://localhost:8000/wireframes/` (o en la IP de AWS: `http://3.213.246.194/wireframes/`).

Al exponer, proyecta esa pestaña en pantalla completa y sigue estos 5 pasos:

```
+-----------------------------------------------------------------------------------+
|                        PANTALLA DE WIREFRAMES INTERACTIVOS                        |
|                                                                                   |
|  [Paso 1: Login] ----> [Paso 2: Dashboard] ----> [Paso 3: Formulario Unificado]  |
|                                                              |                    |
|                                                              v                    |
|  [Paso 5: Semáforo Metas] <----------------------- [Paso 4: Kanban Tubo Trabajo]  |
+-----------------------------------------------------------------------------------+
```

### Paso 1: Mostrar Acceso al Sistema y Recuperación de Contraseña
* **Qué haces en pantalla:** Muestras el recuadro de Login con el logo municipal y el formulario de recuperación.
* **Qué dices (Defensa técnica):**
  > *"Comenzamos con la puerta de entrada al SGR. Este wireframe responde al Caso de Uso CU-01. Diseñamos un acceso dual (nombre de usuario o correo corporativo). En su construcción futura en Django, esto no se guarda como texto plano: implementamos hashing criptográfico PBKDF2 con sal y protección contra ataques de fuerza bruta. El flujo de recuperación en 3 pasos genera un token seguro de un solo uso con expiración matemática de 15 minutos."*

### Paso 2: Mostrar el Dashboard con Selector de Roles (RBAC)
* **Qué haces en pantalla:** En la barra superior del wireframe, haz clic en los botones de cambio de rol: **Administrador**, **Supervisor** y **Operador**. Muestra cómo cambian las tarjetas y los menús.
* **Qué dices (Defensa técnica):**
  > *"Este es el corazón de la usabilidad del sistema (CU-09). Para defender su construcción futura, aplicamos el principio de **Control de Acceso Basado en Roles (RBAC)**. Si el usuario es Administrador, el backend le consulta a MySQL las métricas de toda la comuna. Si el usuario es Supervisor de La Antena, un middleware inyecta un filtro obligatorio en el ORM de Django (`filter(id_delegacion=user.delegacion)`), garantizando que jamás se mezclen los datos entre delegaciones territoriales."*

### Paso 3: Mostrar el Formulario Unificado de Atención Ciudadana
* **Qué haces en pantalla:** Baja a la sección de ingreso de gestiones. Muestra el campo RUT del vecino solicitante.
* **Qué dices (Defensa técnica):**
  > *"Aquí resolvemos el dolor principal de los funcionarios: la lentitud en la atención. En este wireframe (CU-05), el funcionario ingresa el RUT del vecino y, en la construcción del sistema, una llamada asíncrona (AJAX/Fetch) consulta la tabla `vecinos`. Si ya existe en el padrón comunal, autocompleta nombre, teléfono y sector en menos de un segundo. Además, incorpora un switch para clasificar si es una Gestión Social con visita a terreno o una derivación directa a la cuadrilla municipal."*

### Paso 4: Mostrar el Tablero Kanban del Tubo de Trabajo
* **Qué haces en pantalla:** Ve a la sección del Kanban de 4 columnas (*Ingresada*, *En Proceso*, *Atrasadas*, *Realizado*).
* **Qué dices (Defensa técnica):**
  > *"El Tubo de Trabajo responde al CU-07. Diseñamos tarjetas visuales con códigos únicos relacionales `[TUB-XXXXX]`. En la construcción del backend, este tablero no es un dibujo: está conectado a una máquina de estados en el modelo `Compromiso`. Cuando un funcionario arrastra o marca una tarea como 'Realizada', el backend actualiza la fecha de cierre, sincroniza el estado con la gestión ciudadana de origen y recalcula el avance de metas en tiempo real."*

### Paso 5: Mostrar el Semáforo de Cumplimiento de Metas
* **Qué haces en pantalla:** Muestra las barras de progreso verdes, amarillas y rojas.
* **Qué dices (Defensa técnica):**
  > *"Finalmente, el Semáforo de Metas (CU-08). Cada gestión clasificada como 'Cuantitativa' y respaldada con evidencia aprobada incrementa el ponderador del funcionario según la fórmula matemática definida en la base de datos, impidiendo que la suma supere el 100%. Esto entrega a la alcaldía y directores de DIDECO una herramienta de auditoría gerencial transparente."*

---

## 3. CÓMO DEMOSTRAR QUE NO ES SOLO UN WIREFRAME, SINO UN SISTEMA REAL (EL GOLPE DE EFECTO)

La mayoría de los estudiantes se quedará solo en el wireframe estático. **Tu gran ventaja competitiva es que tú ya construiste el sistema real**.

Hacia el **minuto 6 de tu presentación**, haz esta transición maestra:

> *"Profesor, la rúbrica nos pide 'defender su construcción futura en un sistema'. Nuestro equipo fue un paso más allá de la teoría: **construimos, probamos y desplegamos el sistema real en producción** para validar empíricamente cada mockup."*

1. **Abre una pestaña nueva y entra a `http://localhost:8000/login/` (o tu IP de AWS):**
   * Inicia sesión con `admin`.
   * Muestra el Dashboard real con las 24 gestiones cargadas.
   * Ve al Tablero Kanban de Tubo de Trabajo (`/agenda/resumen/`).
   * Muestra cómo la gestión tiene el mismo diseño, colores y flujo que prometiste en el wireframe.
2. **Abre la terminal y ejecuta las pruebas en vivo:**
   * Muestra la terminal con `python test_suite.py`.
   * Di con seguridad:
     > *"Profesor, aquí están las 14 baterías de pruebas automatizadas que demuestran que el sistema no falla, que no permite ponderaciones sobre el 100%, que protege las contraseñas y que opera con total integridad referencial."*

---

## 4. CRONOGRAMA MINUTO A MINUTO PARA NO PASARTE DE LOS 10 MINUTOS

| Minuto | Qué mostrar en pantalla | Qué decir | Artefacto a respaldar |
|---|---|---|---|
| **0:00 – 1:30** | Portada e imagen de La Serena | Saludo, problema territorial de delegaciones y justificación Cloud (IaaS en AWS / SaaS). | Criterio 3.1.1 (Tendencias Cloud) |
| **1:30 – 3:00** | Diapositiva Metodología Híbrida | Por qué Cascada en la Etapa 1 (auditoría y MER 3NF) y por qué Scrum en Etapas 2 y 3 (3 Sprints). | Criterio 2 (Metodologías) |
| **3:00 – 5:30** | Pestaña `/wireframes/` en vivo | Recorrido de los 5 Mockups: Login, Dashboard RBAC, Formulario Unificado, Kanban y Semáforo. | Criterio 5 (Casos de Uso en Wireframes) |
| **5:30 – 7:30** | Pestaña del Sistema Real Django | Demostración de la construcción real: roles, filtros territoriales y subida de evidencias. | Criterio 1 (Cumplimiento de RF y RNF) |
| **7:30 – 9:00** | Terminal con `test_suite.py` | Explicación de calidad (testing), seguridad OWASP y leyes chilenas (Ley 21.459 y 19.628). | Criterio 3 y 4 (Calidad y Seguridad) |
| **9:00 – 10:00** | Diapositiva de Conclusiones | Cierre formal, impacto en la ciudadanía de La Serena y disposición para preguntas. | Cierre impecable |

---

## 5. RESPUESTAS TÉCNICAS A LAS 3 PREGUNTAS MÁS PROBABLES DE LA COMISIÓN

1. **Profesor:** *"¿Cómo garantiza este prototipo que un funcionario de La Antena no modifique atenciones de Las Compañías?"*
   * **Tu respuesta:**
     > *"Profesor, a nivel de wireframe se diseñó la vista filtrada por delegación; pero en su construcción en Django, implementamos un filtro a nivel de ORM en la consulta (`Actividad.objects.filter(id_delegacion=request.user.perfil.delegacion_activa)`). Incluso si un usuario intentara adivinar la URL de otra delegación, el sistema valida la pertenencia y bloquea el acceso con un error 403 Forbidden."*

2. **Profesor:** *"¿Por qué dicen que el sistema cumple con la Ley 21.459 de Delitos Informáticos?"*
   * **Tu respuesta:**
     > *"Porque la Ley 21.459 sanciona el acceso ilícito y la falsificación de datos informáticos. En nuestro sistema implementamos campos de auditoría inmutables: cada vez que se sube, aprueba o subsana una evidencia, el sistema estampa automáticamente el ID del usuario, la fecha y hora del servidor y la dirección IP de origen, impidiendo el repudio o la alteración clandestina de registros."*

3. **Profesor:** *"¿Qué pasa si el servidor de base de datos se satura con miles de vecinos?"*
   * **Tu respuesta:**
     > *"Por eso defendimos una arquitectura desacoplada en AWS EC2: el servidor web corre Nginx y Gunicorn de forma asíncrona, y la base de datos MySQL 8.4 cuenta con índices B-Tree en las columnas más consultadas (`rut`, `codigo`, `fecha` e `id_delegacion`). Si la carga comunal aumenta, podemos separar la base de datos hacia Amazon RDS con réplicas de solo lectura sin tocar el código fuente."*
