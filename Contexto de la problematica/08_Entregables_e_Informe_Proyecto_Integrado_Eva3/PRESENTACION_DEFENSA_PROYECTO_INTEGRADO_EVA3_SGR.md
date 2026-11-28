# PRESENTACIÓN Y DEFENSA FINAL DE PROYECTO INTEGRADO (15 MINUTOS)
## SISTEMA DE GESTIÓN DE RESULTADOS (SGR) — ILUSTRE MUNICIPALIDAD DE LA SERENA

---

### FICHA TÉCNICA DE LA EVALUACIÓN

| Parámetro | Detalle |
| :--- | :--- |
| **Asignatura** | Proyecto Integrado (TI - INACAP La Serena) |
| **Evaluación** | Evaluación 3 Unidad 3: Informe Final y Presentación del SGR |
| **Docente Evaluadora** | Mariavictoria Freites Ayala |
| **Tiempo Máximo** | 15 Minutos cronometrados por equipo |
| **Integrantes y Roles** | **Emanuel Román Serón** (Scrum Master / Backend & Cloud Architecture)<br/>**Benjamín Antipa** (Development Team / Frontend & UX Logic)<br/>**Álvaro Obregón** (Development Team / Data, Quality & Security) |
| **Despliegue Productivo** | AWS EC2: [http://3.213.246.194:8000/](http://3.213.246.194:8000/) |
| **Swagger UI** | [http://3.213.246.194:8000/api/swagger/](http://3.213.246.194:8000/api/swagger/) |
| **Repositorio GitHub** | [https://github.com/iScreamyy6/Backend](https://github.com/iScreamyy6/Backend) |

---

## ESTRUCTURA DE TIEMPOS Y PARTICIPACIÓN (15 MINUTOS EXACTOS)

```
[00:00 - 02:00] Bloque 1: Equipo, Problemática Territorial y Objetivo SGR  (Emanuel Román)
[02:00 - 04:00] Bloque 2: Solución Municipal y Módulos del Negocio         (Benjamín Antipa)
[04:00 - 06:00] Bloque 3: Interfaz, Experiencia de Usuario y Validaciones (Benjamín Antipa)
[06:00 - 08:00] Bloque 4: Base de Datos Relacional y Fórmula de Metas     (Álvaro Obregón)
[08:00 - 10:00] Bloque 5: Patrones de Seguridad, Roles y Despliegue AWS   (Emanuel Román)
[10:00 - 11:30] Bloque 6: Arquitectura, Repositorio y Colaboración Ágil   (Emanuel / Equipo)
[11:30 - 13:30] Bloque 7: Protocolo de Pruebas y DEMOSTRACIÓN EN VIVO     (Todo el Equipo)
[13:30 - 15:00] Bloque 8: Conclusiones, Mejoras Continuas y Cierre         (Álvaro Obregón)
```

---

## DIAPOSITIVA 1 | BLOQUE 1: PRESENTACIÓN DEL EQUIPO, PROBLEMA Y OBJETIVO
**Tiempo:** Minuto 00:00 a 02:00 | **Expositor:** Emanuel Román Serón

### Contenido Visual de la Diapositiva
- **Contexto Municipal:** La Serena cuenta con más de 250.000 habitantes y una amplia dispersión geográfica distribuida en delegaciones urbanas y rurales (La Antena, Las Compañías, Centro Histórico, La Pampa, Avenida del Mar, Rural Cordillera).
- **El Problema Crítico:**
  - Registro artesanal y desconectado en planillas Excel y cuadernos.
  - Cero trazabilidad en los compromisos vecinales adquiridos por los funcionarios en terreno.
  - Imposibilidad de medir el avance real de las metas de gestión institucional (PMG).
  - Vulnerabilidad de los datos de los vecinos (Ley N° 19.628).
- **El Objetivo del Proyecto:** Diseñar, desarrollar, probar y desplegar en la nube de AWS el **Sistema de Gestión de Resultados (SGR)**, centralizando la atención ciudadana, el trabajo territorial y la evaluación de metas con semaforización en tiempo real.

> **Guión de Exposición (Emanuel):**
> *"Buenos días profesora Mariavictoria y compañeros. Como equipo compuesto por Benjamín Antipa, Álvaro Obregón y quien les habla, Emanuel Román, presentamos el Sistema de Gestión de Resultados para las Delegaciones Municipales de La Serena.
> El municipio enfrentaba una problemática severa: las delegaciones operaban como islas de información, utilizando cuadernos y planillas de cálculo dispersas. Cuando un vecino pedía un arreglo o una ayuda social, la solicitud se extraviaba y el alcalde o los directores no tenían forma de medir si las metas se estaban cumpliendo con evidencias reales.
> Nuestro objetivo fue resolver esto de raíz mediante una plataforma web y móvil empresarial construida en Django, MySQL y desplegada en AWS, que no se quedó en una maqueta teórica, sino que hoy está 100% operativa en producción."*

---

## DIAPOSITIVA 2 | BLOQUE 2: SOLUCIÓN Y NECESIDADES DEL NEGOCIO
**Tiempo:** Minuto 02:00 a 04:00 | **Expositor:** Benjamín Antipa

### Contenido Visual de la Diapositiva
- **Módulos Principales de la Solución:**
  1. **Atenciones Ciudadanas:** Registro unificado de vecinos con georreferenciación barrial y selección de subatenciones en cascada.
  2. **Tubo de Trabajo (Tablero Kanban):** Gestión visual de compromisos con estados (Por Iniciar, En Proceso, En Espera, Realizado) y alerta de atrasos.
  3. **Gestor Social:** Flujo especializado multi-etapa para ayudas sociales de emergencia, visitas domiciliarias y fichas socioeconómicas.
  4. **Metas y Ponderaciones:** Motor institucional que vincula cada labor operativa a una meta cuantitativa con tope estricto del 100%.
  5. **Bandeja de Evidencias:** Auditoría y dictamen de archivos adjuntos por supervisores.
- **Relación Proceso - Solución:** Desde la ventanilla de atención vecinal hasta el reporte comunal para el Concejo Municipal.

> **Guión de Exposición (Benjamín):**
> *"Para dar respuesta exacta a los procesos de negocio de la municipalidad, modelamos el sistema en 5 ejes fundamentales.
> Primero, la ventanilla única de Atenciones Ciudadanas: un funcionario registra al vecino en segundos con validación de identidad.
> Segundo, cuando la solicitud requiere trabajo en terreno (por ejemplo, reparar una luminaria en Las Compañías), se deriva al Tubo de Trabajo, un tablero Kanban interactivo que sincroniza tareas con fechas límites y técnicos asignados.
> Tercero, el módulo de Gestor Social, que maneja casos de alta sensibilidad social con un flujo formal de visitas y acreditaciones.
> Y lo más innovador: cada acción realizada alimenta directamente el módulo de Metas Institucionales, garantizando que cada peso de inversión municipal cuente con respaldo auditable."*

---

## DIAPOSITIVA 3 | BLOQUE 3: INTERFAZ, EXPERIENCIA DE USUARIO Y VALIDACIONES
**Tiempo:** Minuto 04:00 a 06:00 | **Expositor:** Benjamín Antipa

### Contenido Visual de la Diapositiva
- **Lineamientos Estéticos Institucionales:**
  - Identidad corporativa de La Serena: Azul Municipal (`#1E3A8A`), Dorado institucional y fondo ergonómico neutro (`#F8FAFC`).
  - Cumplimiento de accesibilidad **WCAG 2.1 AA** con ratios de contraste superiores a 4.5:1 y tipografía de alta legibilidad (*Inter*).
- **Ergonomía y Navegación:** Menú lateral persistente, selector global de **Delegación Activa** en el encabezado (con cambio dinámico a vista comunal consolidada).
- **Validaciones en Tiempo Real:**
  - Validación del RUT chileno mediante algoritmo Módulo 11 tanto en cliente como en servidor.
  - Desplegables dependientes vía peticiones asíncronas AJAX para no saturar al usuario.
  - Alertas inmediatas (Django Messages) con feedback semántico (éxito, advertencia, error).
- **Diseño Responsivo:** Adaptación fluida para tablets y teléfonos móviles utilizados por funcionarios en terreno.

> **Guión de Exposición (Benjamín):**
> *"En el diseño de la interfaz priorizamos dos factores: la rapidez operativa y la identidad municipal.
> Los funcionarios atienden decenas de personas al día, por lo que la interfaz debía evitar recargas innecesarias. Diseñamos un selector de subatenciones en cascada con AJAX y una barra superior donde el supervisor puede alternar entre su delegación local o ver el consolidado de toda la comuna en un clic.
> Además, implementamos la validación algorítmica del RUT chileno mediante Módulo 11: si un funcionario tipea mal el dígito verificador, el sistema lo detecta al instante, impidiendo registros erróneos.
> La interfaz es 100% responsiva bajo Bootstrap 5, lo que permite a las cuadrillas en terreno consultar su Kanban desde cualquier smartphone o tablet."*

---

## DIAPOSITIVA 4 | BLOQUE 4: BASE DE DATOS Y REGLAS DE NEGOCIO
**Tiempo:** Minuto 06:00 a 08:00 | **Expositor:** Álvaro Obregón

### Contenido Visual de la Diapositiva
- **Esquema Relacional en MySQL 8.0:** 18 entidades normalizadas en Tercera Forma Normal (3FN).
- **Integridad Referencial Estricta:** Uso sistemático de `on_delete=models.PROTECT` en entidades maestras para impedir borrados accidentales de historial municipal.
- **Índices de Optimización:** Búsquedas optimizadas con `db_index=True` en RUT, folios, delegaciones y fechas.
- **La Fórmula Matemática de Metas Institucionales:**
  $$\text{Avance Meta } (\%) = \min\left(100, \left(\frac{\text{Evidencias Cuantitativas Aprobadas}}{\text{Meta Cuantitativa}}\right) \times 100\right)$$
  $$\text{Cumplimiento Funcionario } (\%) = \sum_{i=1}^n \left( \text{Avance Meta}_i \times \frac{\text{Ponderación}_i}{100} \right) \quad \text{donde } \sum P_i = 100\%$$
- **Regla del Semáforo Comunal:** Verde ($\ge 75\%$), Amarillo ($50\% - 74.9\%$), Rojo ($< 50\%$).

> **Guión de Exposición (Álvaro):**
> *"La base de datos se implementó en MySQL 8.0 bajo estricta normalización en Tercera Forma Normal. Para evitar anomalías, protegemos las claves foráneas con `PROTECT`: si un territorio tiene atenciones o vecinos asociados, la base de datos jamás permitirá eliminarlo por error, preservando la trazabilidad legal.
> Pero el corazón del sistema radica en sus reglas de negocio: el cálculo de metas no es un dato arbitrario. El sistema exige que las ponderaciones de cada funcionario sumen exactamente el 100%. Si un supervisor intenta asignar 100.1%, el sistema bloquea la transacción.
> Además, las evidencias cualitativas (como un informe descriptivo) aportan respaldo pero no alteran el porcentaje cuantitativo, mientras que las cuantitativas incrementan el avance solo tras el dictamen favorable del supervisor, alimentando el semáforo comunal en tiempo real."*

---

## DIAPOSITIVA 5 | BLOQUE 5: SEGURIDAD, ROLES Y DESPLIEGUE EN AWS
**Tiempo:** Minuto 08:00 a 10:00 | **Expositor:** Emanuel Román Serón

### Contenido Visual de la Diapositiva
- **Control de Acceso Basado en Roles (RBAC):**
  - Administrador (control comunal), Supervisor (dictamen y monitoreo de delegación), Funcionario (operación de campo).
- **Aislamiento Multi-Tenant por Delegación:** QuerySets filtrados por delegación de sesión activa mediante `context_processors.py`.
- **Criptografía y Mitigación de Vulnerabilidades:**
  - Hashing PBKDF2 SHA-256 (600.000 iteraciones).
  - Tokens de recuperación criptográficos (`PasswordResetTokenGenerator`) de un solo uso con expiración a las 24 horas.
  - Sanitización estricta contra OWASP: Protección CSRF, ORM parametrizado contra SQLi y autoescape contra XSS.
- **Despliegue Productivo en AWS EC2:**
  - Ubuntu Server 22.04 LTS en AWS (IP elástica: `3.213.246.194`).
  - Pila de producción: Nginx (Reverse Proxy) + Gunicorn (WSGI Daemon) + MySQL Server.
  - Variables de entorno desacopladas (`.env` con `python-decouple`, `DEBUG=False`).

> **Guión de Exposición (Emanuel):**
> *"La seguridad y la disponibilidad fueron tratadas con estándares de nivel bancario y de gobierno electrónico.
> Implementamos RBAC estricto: un funcionario operativo no puede ver las metas de sus compañeros ni acceder a la consola de usuarios; un supervisor territorial solo tiene visibilidad sobre su delegación asignada, a menos que el administrador active la vista comunal total.
> Para la recuperación de credenciales, implementamos el flujo criptográfico exigido en la Evaluación 3: tokens firmados digitalmente de un solo uso que caducan automáticamente tras su uso o al vencer el plazo.
> Y lo más importante: el sistema no está en `localhost`. Está desplegado en una instancia AWS EC2 con Nginx y Gunicorn, cumpliendo la condición excluyente de la pauta de evaluación."*

---

## DIAPOSITIVA 6 | BLOQUE 6: IMPLEMENTACIÓN Y COLABORACIÓN ÁGIL
**Tiempo:** Minuto 10:00 a 11:30 | **Expositor:** Emanuel Román / Equipo

### Contenido Visual de la Diapositiva
- **Metodología Ágil:** Scrum con sprints de 1 semana, ceremonias diarias y entregas continuas.
- **Repositorio Oficial:** [GitHub: iScreamyy6/Backend](https://github.com/iScreamyy6/Backend)
- **Estrategia de Ramas:** GitFlow estructurado (`main` para producción, ramas `feature/*` para módulos aislados).
- **Trazabilidad de Participación:**
  - Emanuel Román: Arquitectura de datos, seguridad, despliegue AWS, API REST y testing automatizado.
  - Benjamín Antipa: Frontend responsivo, Tablero Kanban, experiencia de usuario y validaciones cliente.
  - Álvaro Obregón: Lógica de negocio de metas, bandeja de evidencias, modelos entidad-relación y auditoría.

> **Guión de Exposición (Emanuel):**
> *"El trabajo colaborativo se gestionó mediante Scrum y control de versiones en GitHub. Aplicamos una disciplina rigurosa de ramas de características y commits semánticos en español.
> Cada módulo fue desarrollado de manera equilibrada: Benjamín lideró la experiencia de usuario y el frontend del Kanban; Álvaro se concentró en la lógica matemática de metas, normalización de la base de datos y la bandeja de evidencias; y yo coordiné la arquitectura de backend, la seguridad y el despliegue productivo en AWS.
> Esta sinergia nos permitió llegar al día de la entrega con el 100% de los requisitos aprobados."*

---

## DIAPOSITIVA 7 | BLOQUE 7: PROTOCOLO DE PRUEBAS Y DEMOSTRACIÓN EN VIVO
**Tiempo:** Minuto 11:30 a 13:30 | **Expositor:** Todo el Equipo (Demostración Práctica)

### Contenido Visual de la Diapositiva
- **Resultados de la Suite Automatizada (`test_suite.py`):**
  - 100% de casos de prueba aprobados (Funcionales, Seguridad, Casos de Borde e Integridad).
  - Cero fallos en la versión final desplegada.
- **Discrepancia Resuelta Documentada:** Corrección del error de importación de `Funcionario` en `context_processors.py` (L95) y sincronización transaccional del Kanban.
- **Ruta de la Demostración en Vivo en AWS ([http://3.213.246.194:8000/](http://3.213.246.194:8000/)):**
  1. Login con rol Administrador -> Vista de Dashboard con Semáforo Comunal.
  2. Cambio de Delegación activa -> Aislamiento de datos en pantalla.
  3. Creación de Atención Ciudadana con validación de RUT -> Derivación a Tubo de Trabajo.
  4. Tablero Kanban -> Transición de estado a "Realizado".
  5. Bandeja de Evidencias -> Dictamen de supervisor e impacto inmediato en el porcentaje de metas.

> **Guión de Demostración en Vivo (Todo el Equipo):**
> *(Emanuel abre el navegador en `http://3.213.246.194:8000/`)*
> **Emanuel:** *"Profesora, pasamos a la demostración sobre el sistema real en AWS. Iniciamos sesión como administrador. Observen en el panel principal el Semáforo Comunal, calculado en tiempo real sobre las 6 delegaciones."*
> **Benjamín:** *(Toma el control)* *"Ahora ingresamos a Atenciones Ciudadanas. Si intento tipear un RUT con dígito verificador inválido, el sistema bloquea inmediatamente. Ingresamos un vecino válido, seleccionamos 'Atención Social' y la subatención se carga automáticamente por AJAX. Guardamos y el folio ATC-00117 queda creado y derivado a terreno."*
> **Álvaro:** *(Toma el control)* *"Vamos al Tubo de Trabajo: aquí vemos el compromiso. Lo arrastramos a 'Realizado'. Ahora el funcionario adjunta su evidencia fotográfica. Como supervisor, ingreso a la Bandeja de Evidencias, reviso el archivo y dicto 'Aprobado'. En este preciso instante, la meta cuantitativa sube a 1 y el porcentaje del semáforo se actualiza en pantalla sin recargas fraudulentas."*

---

## DIAPOSITIVA 8 | BLOQUE 8: CONCLUSIONES, MEJORA CONTINUA Y CIERRE
**Tiempo:** Minuto 13:30 a 15:00 | **Expositor:** Álvaro Obregón / Equipo

### Contenido Visual de la Diapositiva
- **Cumplimiento de Objetivos:** 100% de requerimientos funcionales, no funcionales y de seguridad satisfechos.
- **Aporte al Municipio:** Transformación digital real de las delegaciones de La Serena, reemplazando la opacidad de los cuadernos por trazabilidad y auditoría pública.
- **Hoja de Ruta y Mejora Continua:**
  - P1: Integración de caché en memoria con Redis para optimizar el Semáforo Comunal.
  - P2: Notificaciones automáticas por WhatsApp a los vecinos.
  - P3: App móvil PWA con capacidades offline para zonas rurales cordilleranas.
- **Cierre:** Agradecimientos y apertura formal a la ronda de preguntas individuales.

> **Guión de Cierre (Álvaro):**
> *"En conclusión, el Sistema de Gestión de Resultados demuestra cómo la ingeniería de software aplicada resuelve problemas reales de la gestión pública. Entregamos un producto terminado, probado exhaustivamente, seguro y funcionando en la nube de AWS.
> Agradecemos su atención y quedamos a su entera disposición para responder a sus preguntas sobre cualquier módulo del sistema. Muchas gracias."*

---

## BANCO DE PREGUNTAS INDIVIDUALES PREVISTAS (CRITERIO 3.1.6.14)

### Para Emanuel Román (Arquitectura, Seguridad y Despliegue):
- **Pregunta Docente:** *¿Por qué utilizaron tokens criptográficos para la recuperación de contraseña en lugar de enviar la clave por correo?*
  - **Respuesta Emanuel:** *"Porque enviar contraseñas en texto claro viola la norma ISO 27001 y la Ley 19.628. La clase `PasswordResetTokenGenerator` genera un token firmado con un hash de la contraseña actual, el ID del usuario y la marca temporal. De este modo, el token solo puede usarse una vez, expira a las 24 horas y, si el usuario cambia su clave por otra vía, el token se invalida automáticamente."*
- **Pregunta Docente:** *¿Cómo opera Gunicorn y Nginx en la instancia AWS?*
  - **Respuesta Emanuel:** *"Nginx actúa como proxy inverso en el puerto 80/8000, sirviendo directamente el contenido estático y media sin consumir recursos de Python. Cuando llega una petición dinámica, Nginx la transfiere mediante un socket UNIX local a Gunicorn, que administra un pool de workers WSGI asíncronos para ejecutar Django de forma concurrente y segura."*

### Para Benjamín Antipa (Frontend, UX y Validaciones):
- **Pregunta Docente:** *¿Cómo implementaron la carga de subatenciones en cascada sin recargar la página?*
  - **Respuesta Benjamín:** *"Utilizamos JavaScript nativo con la API `fetch` escuchando el evento `change` del selector de tipo de atención. Este dispara una llamada asíncrona al endpoint `/api/subatenciones-cascade/?tipo_id=X`, recibe un arreglo JSON con las subatenciones filtradas por delegación y vacía y repuebla dinámicamente el segundo menú desplegable en menos de 50 milisegundos."*
- **Pregunta Docente:** *¿Cómo garantizan que un funcionario en terreno pueda usar el sistema desde su celular?*
  - **Respuesta Benjamín:** *"Mediante el sistema de grillas flexbox de Bootstrap 5 con breakpoints móviles `< 768px`. La barra de navegación se colapsa en un menú offcanvas accesible con el pulgar, las tablas complejas ofrecen desplazamiento lateral protegido y los formularios disponen de inputs táctiles nativos (numéricos para RUT y teléfonos), facilitando la captura bajo luz solar en terreno."*

### Para Álvaro Obregón (Base de Datos, Reglas de Negocio y Metas):
- **Pregunta Docente:** *¿Cómo garantizan que la sumatoria de ponderaciones de un funcionario no supere el 100%?*
  - **Respuesta Álvaro:** *"La validación opera en dos capas. En el formulario Django sobrescribimos el método `clean()`, calculando mediante el ORM la sumatoria de las metas activas del funcionario más la nueva ponderación ingresada. Si la suma supera 100%, lanzamos un `ValidationError`. Y a nivel de modelo, implementamos una restricción de comprobación para garantizar consistencia incluso si la inserción se intentara por shell o API."*
- **Pregunta Docente:** *¿Cuál es la diferencia entre una evidencia cuantitativa y una cualitativa en el avance de metas?*
  - **Respuesta Álvaro:** *"La evidencia cuantitativa representa una unidad de producto medible (por ejemplo, 1 operativo de limpieza realizado). Al ser aprobada por el supervisor, suma +1 al numerador de la meta cuantitativa. La evidencia cualitativa (por ejemplo, un acta de reunión vecinal) respalda el cumplimiento de estándares de calidad o cumplimiento normativo, pero no altera el divisor de cálculo para no falsear el avance porcentual del semáforo."*
