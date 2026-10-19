# INFORME TÉCNICO Y DE DESPLIEGUE — EVALUACIÓN SUMATIVA N°2 (25%)
## SISTEMA DE GESTIÓN DE RESULTADOS (SGR) — ILUSTRE MUNICIPALIDAD DE LA SERENA

---

### IDENTIFICACIÓN DEL PROYECTO Y EQUIPO

* **Institución:** INACAP — Sede La Serena
* **Área Académica:** Informática, Ciberseguridad y Telecomunicaciones
* **Carrera:** Ingeniería en Informática
* **Asignatura:** Proyecto Integrado D-IEI-N4-P2-C3
* **Docente Guía:** Mariavictoria Freites Ayala
* **Equipo de Desarrollo:**
  * **Benjamín Antipa**
  * **Emanuel Román**
  * **Álvaro Obregón**


---

## 1. PRESENTACIÓN Y CONTEXTO DEL PROYECTO

### 1.1 ¿Qué problemática estamos resolviendo?
La Ilustre Municipalidad de La Serena cuenta con diversas delegaciones territoriales (como La Serena Centro, Las Compañías, La Pampa, Avenida del Mar, entre otras) cuyo rol es estar en contacto directo con los vecinos, atendiendo requerimientos que van desde subsidios sociales y trámites comunitarios, hasta inspecciones de obras vecinales y gestión de seguridad.

En la etapa diagnóstica identificamos que cada delegación trabajaba de manera aislada utilizando planillas Excel y anotaciones manuales. Esto generaba importantes cuellos de botella:
* **Falta de visibilidad para las jefaturas:** No existía un lugar unificado donde la Dirección Comunitaria o la Alcaldía pudieran revisar la carga de trabajo en tiempo real por cada territorio.
* **Compromisos que se perdían en el tiempo:** Cuando un funcionario asumía un compromiso con un vecino, el seguimiento dependía de recordatorios informales, provocando retrasos no detectados.
* **Ausencia de verificación en terreno:** No se contaba con un respaldo fotográfico formal y trazable que demostrara que una actividad efectivamente se ejecutó.
* **Dificultad para medir el cumplimiento de metas:** Calcular el porcentaje de avance de cada funcionario según su cargo tomaba semanas de consolidación manual.

### 1.2 La Evolución del Sistema SGR (De Eva 1 a Eva 2)
Durante la Evaluación N°1 construimos un primer prototipo modular en Django, validando los flujos mediante archivos JSON estáticos. 

Para esta **Evaluación Sumativa N°2**, asumimos el desafío de dar un salto cualitativo hacia una aplicación web profesional de nivel de producción:
1. **Persistencia Relacional Real:** Migramos el 100% de la lógica hacia un modelo relacional en MySQL/MariaDB, aplicando el ORM de Django con migraciones controladas e integridad referencial estricta.
2. **Administración Centralizada:** Personalizamos Django Admin para gestionar usuarios, delegaciones, cargos y catálogos, permitiendo una administración ágil y segura.
3. **Despliegue Productivo en la Nube (AWS EC2):** Llevamos la aplicación a un servidor Linux Ubuntu en Amazon Web Services, configurando Gunicorn, Nginx y variables de entorno seguras para recrear un entorno real de explotación.
4. **Seguridad y Control Territorial:** Implementamos autenticación obligatoria y aislamiento de datos por delegación, asegurando que ningún funcionario acceda a datos que no correspondan a su jurisdicción.

---

## 2. PUNTOS DE ACCESO, REPOSITORIO Y ARTEFACTOS DEL SISTEMA

Para facilitar la revisión técnica por parte de la docente guía Mariavictoria Freites Ayala, dejamos a disposición todos los enlaces activos del proyecto en la nube:

### 🌐 Aplicación en Producción (AWS EC2)
* **Dirección Web Pública:** [http://3.229.11.31/](http://3.229.11.31/)
* **Descripción:** Aplicación corriendo en vivo sobre una instancia Ubuntu Linux en Amazon Web Services con servidor web Nginx y gestor de procesos Gunicorn. Permite probar la navegación, el inicio de sesión y la operación diaria del sistema.

### ⚙️ Panel de Administración Django (Django Admin)
* **URL de Acceso:** [http://3.229.11.31/admin/](http://3.229.11.31/admin/)
* **Usuario:** `admin`
* **Contraseña:** `admin123`
* **Descripción:** Panel administrativo para la gestión de entidades (`Delegacion`, `Persona`, `Actividad`, `Compromiso`, `Meta`, `Evidencia`), con filtros avanzados, búsquedas y permisos.

### 🗄️ Base de Datos en phpMyAdmin
* **URL de Acceso:** [http://3.229.11.31/phpmyadmin/](http://3.229.11.31/phpmyadmin/)
* **Usuario:** `sgr_user`
* **Contraseña:** `Municipalidad2026!`
* **Descripción:** Entorno gráfico para verificar directamente las tablas físicas creadas por las migraciones de Django, claves foráneas y registros persistidos.

### 🐙 Repositorio de Código Fuente en GitHub
* **URL del Repositorio:** [https://github.com/iScreamyy6/Backend](https://github.com/iScreamyy6/Backend)
* **Descripción:** Repositorio oficial con el historial íntegro de commits, control de versiones, ramas de desarrollo y archivos de configuración.

### 📊 Diagramas de Arquitectura y Casos de Uso (Google Drive Oficial)
* **Enlace de Acceso:** [👉 CARPETA OFICIAL DE DIAGRAMAS SGR EN GOOGLE DRIVE 👈](https://drive.google.com/drive/folders/1tsG66Q9NEwbjVQfpdaVqwpMd4AZmfVxt?usp=sharing)
* **URL Directa:** `https://drive.google.com/drive/folders/1tsG66Q9NEwbjVQfpdaVqwpMd4AZmfVxt?usp=sharing`
* **Contenido Disponible:**
  * Diagrama de Requerimientos Funcionales y No Funcionales.
  * Diagrama de Casos de Uso de Alto Nivel / General.
  * Diagramas de Casos de Uso Detallados por módulo.
  * Modelo Entidad-Relación (MER) oficial en alta resolución.
  * Archivo fuente editable de MySQL Workbench: [`modelo-sgr-MER.mwb`](./modelo-sgr-MER.mwb).

---

## 3. ARQUITECTURA DE LA SOLUCIÓN Y DECISIONES TÉCNICAS

Como equipo estructuramos la solución en **cuatro aplicaciones Django independientes pero interconectadas**, garantizando alta cohesión y bajo acoplamiento:

1. **`organizacion` (Gestión Territorial y Funcionarios):**  
   Modela las delegaciones municipales, las unidades de apoyo y las fichas de los funcionarios (`Persona`). Incorpora el control de acceso territorial mediante el usuario autenticado.
2. **`actividades` (Registro Operativo y Evidencias):**  
   Gestiona las atenciones vecinales diarias, clasifica por servicio e implementa el **Código Único de Evidencia (CU11)**, mecanismo diseñado para vincular inequívocamente cada foto de respaldo con su respectiva atención. Además, provee el módulo de validación técnica donde un supervisor puede aprobar o rechazar evidencias.
3. **`agenda` (Tubo de Trabajo y Compromisos Colectivos):**  
   Implementa un tablero visual estilo Kanban con los estados de cada compromiso (`Ingresado`, `Pendiente`, `En proceso`, `Realizado`). Cada cambio de estado queda registrado con fecha y autor inalterable para auditoría.
4. **`resultados` (Motor de Metas y Semáforo):**  
   Aplica la lógica de negocio municipal: compara el avance real ponderado contra la meta esperada calculada al día, controlando topes máximos (hasta 150%) y determinando el semáforo operativo (**Verde** para ≥90%, **Ámbar** entre 60% y 89%, y **Rojo** para <60%).

### Decisiones de Seguridad y Buenas Prácticas
* **Variables de Entorno (`.env`):** Siguiendo las directrices de la evaluación, ninguna clave secreta, contraseña de base de datos ni credencial de AWS fue escrita en el código de Django. Todas son inyectadas mediante `python-dotenv`.
* **Protección de Rutas (`@login_required`):** Ninguna pantalla interna del sistema es accesible sin haber iniciado sesión previamente. Los intentos de acceso anónimo son interceptados y redirigidos al login.
* **Separación de Ambientes:** El despliegue en AWS opera con `DEBUG = False` y sirve archivos estáticos optimizados mediante WhiteNoise / Nginx.

---

## 4. ESPECIFICACIÓN DETALLADA DE CASOS DE USO (CU01 AL CU10)

A continuación documentamos en detalle los diez casos de uso del sistema. Hemos estructurado cada uno en formato de **Ficha Técnica Ejecutiva**, especificando con claridad sus actores, objetivos, precondiciones, flujo principal paso a paso, postcondiciones y relaciones con otros casos de uso (`<<include>>` y `<<extend>>`), conforme a la documentación oficial del proyecto.

---

### FICHA CU01: Administrar Usuarios, Roles y Delegaciones

* **Identificador:** `CU01`
* **Nombre:** Administrar Usuarios, Roles y Delegaciones
* **Actor Principal:** Administrador del Sistema
* **Propósito:**  
  Permitir al administrador dar de alta, modificar o desactivar delegaciones municipales y mantener actualizado el catálogo de funcionarios, configurando sus credenciales, cargos y ámbitos de acceso bajo el principio de mínimo privilegio.

* **Precondiciones:**  
  El administrador debe contar con una sesión activa con permisos de superusuario en el sistema.

* **Flujo Principal de Ejecución:**
  1. El Administrador accede al Módulo de Administración.
  2. Selecciona la acción a realizar: crear/modificar una delegación municipal, dar de alta a un funcionario, reasignar su rol o desactivar una cuenta.
  3. Ingresa o actualiza los datos requeridos (RUT chileno válido, nombre completo, cargo institucional y delegación de pertenencia).
  4. El sistema valida obligatoriamente los datos de entrada (formato de RUT, campos obligatorios no vacíos).
  5. El sistema persiste los cambios en la base de datos MySQL y deja constancia del evento en la traza de auditoría.

* **Postcondiciones:**  
  La estructura organizacional y las cuentas de usuario quedan actualizadas con efecto inmediato en todo el sistema.

* **Relaciones del Caso de Uso:**
  * **Casos Incluidos (`<<include>>`):** *Validar Datos de Entrada*.
  * **Casos Extendidos (`<<extend>>`):** Ninguno.

---

### FICHA CU02: Configurar Parámetros, Períodos y Metas

* **Identificador:** `CU02`
* **Nombre:** Configurar Parámetros, Períodos y Metas
* **Actores Principales:** Coordinador del Sistema, Administrador
* **Propósito:**  
  Aperturar y cerrar períodos de medición periódica, definir metas cuantitativas por cada cargo municipal, parametrizar la matriz de ponderadores y fijar los umbrales del semáforo de desempeño.

* **Precondiciones:**  
  El usuario debe estar autenticado con rol de Coordinador o Administrador.

* **Flujo Principal de Ejecución:**
  1. El usuario accede al Módulo de Configuración de Metas.
  2. Crea o abre un período de medición especificando sus fechas de inicio y término.
  3. Configura los ítems medibles y las metas numéricas esperadas para cada cargo municipal.
  4. Asigna los factores de ponderación porcentual a cada ítem y define los umbrales del semáforo.
  5. El sistema valida obligatoriamente que la suma de los ponderadores del cargo sea exactamente 100% y que las fechas del período sean coherentes.
  6. El sistema guarda y congela la versión parametrizada para el período correspondiente.

* **Postcondiciones:**  
  Las metas quedan disponibles para el cálculo de cumplimiento de los funcionarios durante el período abierto. Los períodos cerrados quedan protegidos contra cualquier edición posterior.

* **Relaciones del Caso de Uso:**
  * **Casos Incluidos (`<<include>>`):** *Validar Parametrización y Fechas*.
  * **Casos Extendidos (`<<extend>>`):**
    * *Notificar Error de Ponderación:* Se activa si la suma de ponderadores es distinta al 100%.
    * *Notificar Período Cerrado Inmutable:* Se activa si se intenta alterar un período que ya fue cerrado.

---

### FICHA CU03: Registrar Actividad Diaria

* **Identificador:** `CU03`
* **Nombre:** Registrar Actividad Diaria
* **Actor Principal:** Funcionario Municipal
* **Propósito:**  
  Permitir al funcionario ingresar el detalle de las gestiones y atenciones realizadas durante su jornada laboral (fecha, solicitante, problemática abordada, acción ejecutada e ítem de meta asociado), generando el respaldo operativo de su trabajo.

* **Precondiciones:**  
  El Funcionario debe estar autenticado, pertenecer a una delegación activa y tener asignado un período de medición vigente con ítems medibles asociados a su cargo.

* **Flujo Principal de Ejecución:**
  1. El Funcionario accede al formulario de nueva actividad e ingresa los antecedentes (fecha, descripción del caso, acción realizada y datos del vecino solicitante).
  2. Clasifica la atención vinculándola al ítem medible correspondiente a su labor, servicio y área.
  3. El sistema valida los datos obligatorios y confirma que el ítem seleccionado se encuentre vigente en el período.
  4. El sistema invoca automáticamente la generación del Código Único de Evidencia (CU11).
  5. El sistema almacena la actividad en la base de datos, confirma la creación al usuario y deja el registro habilitado para adjuntar la evidencia fotográfica.

* **Postcondiciones:**  
  La actividad queda registrada de manera inmutable con su código identificador, lista para la carga de su respaldo fotográfico.

* **Relaciones del Caso de Uso:**
  * **Casos Incluidos (`<<include>>`):** *Validar Datos de Actividad*, *CU11: Generar Código Único de Evidencia*.
  * **Casos Extendidos (`<<extend>>`):**
    * *Vincular Compromiso de Agenda:* Se ejecuta cuando la atención genera un compromiso de seguimiento vecinal.
    * *Notificar Error de Validación:* Se activa si faltan campos obligatorios o el formato de fecha es incorrecto.

---

### FICHA CU04: Adjuntar Evidencia Fotográfica

* **Identificador:** `CU04`
* **Nombre:** Adjuntar Evidencia Fotográfica
* **Actor Principal:** Funcionario Municipal
* **Propósito:**  
  Vincular un archivo de imagen (fotografía en terreno o documento digital) a una actividad previamente registrada, utilizando su Código Único de Evidencia para asegurar la trazabilidad y posterior verificación.

* **Precondiciones:**  
  El Funcionario debe estar autenticado y debe existir una actividad registrada con su correspondiente Código Único generado.

* **Flujo Principal de Ejecución:**
  1. El Funcionario selecciona la actividad desde su listado o ingresa el Código Único de Evidencia.
  2. Selecciona y carga el archivo fotográfico desde su dispositivo.
  3. El sistema valida el formato de la imagen (JPG o PNG) y controla que el tamaño no exceda el límite permitido.
  4. El sistema almacena el archivo en el almacenamiento seguro del servidor y asocia la ruta al registro de la actividad.
  5. El sistema actualiza el estado de la evidencia a *'Pendiente de Validación'*.

* **Postcondiciones:**  
  La fotografía queda vinculada permanentemente a la actividad con marca temporal de carga y lista para la revisión del supervisor.

* **Relaciones del Caso de Uso:**
  * **Casos Incluidos (`<<include>>`):** *CU03: Registrar Actividad Diaria* (contexto de vinculación).
  * **Casos Extendidos (`<<extend>>`):**
    * *Notificar Formato o Tamaño Inválido:* Se activa si el archivo no corresponde a imagen o excede el peso permitido.

---

### FICHA CU05: Validar Evidencia de Actividad

* **Identificador:** `CU05`
* **Nombre:** Validar Evidencia de Actividad
* **Actor Principal:** Verificador / Supervisor Técnico
* **Propósito:**  
  Inspeccionar la fotografía de respaldo presentada por un funcionario y emitir un dictamen formal (*Aprobada*, *Rechazada* o *Solicitar Corrección*), ingresando las observaciones pertinentes y autorizando el impacto en el cálculo de metas.

* **Precondiciones:**  
  El usuario debe contar con perfil de Verificador con permisos sobre la delegación a revisar y deben existir evidencias en estado *Pendiente*.

* **Flujo Principal de Ejecución:**
  1. El Verificador ingresa al panel de auditoría de evidencias de su delegación.
  2. Selecciona un registro pendiente, revisa la imagen en alta resolución, la descripción de la actividad y la fecha.
  3. El sistema valida los permisos territoriales del Verificador.
  4. El Verificador emite su dictamen: si aprueba, confirma la acción; si rechaza o pide corrección, ingresa obligatoriamente el motivo.
  5. Al confirmarse la aprobación, el sistema recalcula automáticamente el avance de la meta del funcionario responsable.

* **Postcondiciones:**  
  El dictamen queda registrado con autor y fecha inalterable. El avance acumulado del funcionario se incrementa únicamente si la evidencia fue aprobada.

* **Relaciones del Caso de Uso:**
  * **Casos Incluidos (`<<include>>`):** *CU04: Adjuntar Evidencia Fotográfica*, *Validar Ámbito del Verificador*, *Recalcular Avance e Indicadores*.
  * **Casos Extendidos (`<<extend>>`):**
    * *Notificar Observación Faltante:* Se dispara si el verificador intenta rechazar sin explicar el motivo.

---

### FICHA CU06: Registrar y Asignar Compromisos

* **Identificador:** `CU06`
* **Nombre:** Registrar y Asignar Compromisos
* **Actores Principales:** Funcionario, Delegado / Jefatura
* **Propósito:**  
  Ingresar una solicitud vecinal que requiere gestiones futuras dentro de la agenda colectiva de la delegación, asignando un funcionario responsable, delimitación territorial y una fecha límite comprometida inmutable.

* **Precondiciones:**  
  El usuario debe estar autenticado y pertenecer a una delegación municipal activa.

* **Flujo Principal de Ejecución:**
  1. El usuario accede al formulario de ingreso de compromisos en la agenda.
  2. Registra los datos del solicitante (vecino u organización comunitaria) y el canal de ingreso.
  3. Detalla el problema o tarea requerida, seleccionando el área de apoyo involucrada.
  4. Asigna el funcionario responsable de la ejecución y fija la fecha comprometida.
  5. El sistema valida los campos obligatorios y la coherencia de los plazos.
  6. El sistema almacena el compromiso en la agenda colectiva en estado inicial *'Ingresado'*.

* **Postcondiciones:**  
  El compromiso queda visible en el tubo de trabajo de la delegación con fecha límite inmutable para el seguimiento de plazos.

* **Relaciones del Caso de Uso:**
  * **Casos Incluidos (`<<include>>`):** *Validar Solicitud, Responsable y Plazo*.
  * **Casos Extendidos (`<<extend>>`):**
    * *Notificar Compromiso Duplicado:* Alerta si ya existe un requerimiento idéntico en curso para el mismo solicitante.
    * *Notificar Datos Faltantes:* Alerta al usuario si faltan datos esenciales.

---

### FICHA CU07: Gestionar Estados y Reasignar Compromisos

* **Identificador:** `CU07`
* **Nombre:** Gestionar Estados y Reasignar Compromisos
* **Actores Principales:** Funcionario Responsable, Delegado / Jefatura
* **Propósito:**  
  Actualizar la etapa operativa de un compromiso en el tablero Kanban (`Ingresado` ➔ `Pendiente` ➔ `En proceso` ➔ `Realizado`), agregar notas de avance o reasignar la tarea a otro funcionario para asegurar su cumplimiento.

* **Precondiciones:**  
  El usuario debe estar autenticado y tener asignado el compromiso o contar con rol de jefatura en la delegación.

* **Flujo Principal de Ejecución:**
  1. El usuario selecciona el compromiso desde la agenda colectiva o tablero Kanban.
  2. Actualiza el estado operativo e ingresa una nota explicativa del avance logrado.
  3. En caso de ser Delegado/Jefatura, puede transferir el compromiso a otro funcionario fundamentando la reasignación.
  4. El sistema valida la transición y registra la traza histórica (estado previo, nuevo estado, autor, fecha y notas).
  5. Si el estado cambia a *'Realizado'*, el sistema alimenta automáticamente el indicador de cumplimiento del funcionario.

* **Postcondiciones:**  
  El compromiso avanza de fase, manteniendo un historial completo de cambios que previene manipulaciones.

* **Relaciones del Caso de Uso:**
  * **Casos Incluidos (`<<include>>`):** *Validar Transición y Traza de Estado*, *Alimentar Indicador de Medición*.
  * **Casos Extendidos (`<<extend>>`):**
    * *Notificar Motivo de Reasignación Requerido:* Exige fundamentación si la jefatura cambia al funcionario a cargo.

---

### FICHA CU08: Consultar Ficha Personal y Semáforo

* **Identificador:** `CU08`
* **Nombre:** Consultar Ficha Personal y Semáforo
* **Actor Principal:** Funcionario Municipal
* **Propósito:**  
  Permitir al funcionario acceder a su panel individual de desempeño para monitorear el avance acumulado por cada ítem respecto a la meta esperada al día, verificar su semáforo de alerta y auditar las actividades y fotos que respaldan sus números.

* **Precondiciones:**  
  El funcionario debe estar autenticado y contar con metas parametrizadas en el período activo.

* **Flujo Principal de Ejecución:**
  1. El funcionario ingresa a su panel personal de resultados.
  2. El sistema calcula en tiempo real la meta proporcional esperada a la fecha y pondera los avances reales aprobados.
  3. El sistema evalúa los umbrales de alerta y despliega el color del semáforo correspondiente (*Verde*, *Ámbar* o *Rojo*).
  4. El funcionario revisa el detalle cuantitativo por ítem (porcentajes de avance, topes aplicados y ponderación final).
  5. El funcionario puede explorar el historial de actividades asociadas o consultar períodos anteriores.

* **Postcondiciones:**  
  Se despliega la información consolidada de forma transparente y en tiempo real, sin alterar los datos persistidos.

* **Relaciones del Caso de Uso:**
  * **Casos Incluidos (`<<include>>`):** *Calcular Meta Esperada y Semáforo*.
  * **Casos Extendidos (`<<extend>>`):**
    * *Notificar Avance Rezagado:* Destaca alerta visual en rojo si el cumplimiento es inferior al 60%.
    * *Notificar Período Sin Metas:* Informa al usuario si el período activo aún no cuenta con metas asignadas.

---

### FICHA CU09: Monitorear Tablero de Delegación

* **Identificador:** `CU09`
* **Nombre:** Monitorear Tablero de Delegación
* **Actores Principales:** Delegado Municipal, Jefatura, Usuario de Consulta
* **Propósito:**  
  Proporcionar a las autoridades y jefaturas una visión gerencial consolidada del rendimiento de toda la delegación, comparando el cumplimiento entre funcionarios, monitoreando el semáforo grupal y alertando sobre compromisos vecinales vencidos.

* **Precondiciones:**  
  El usuario debe contar con perfil de Delegado, Jefatura o Auditor con ámbito asignado sobre la delegación a consultar.

* **Flujo Principal de Ejecución:**
  1. El usuario accede al tablero de delegación y selecciona el período de análisis.
  2. El sistema consolida los indicadores de todos los funcionarios de la unidad, calculando promedios y el semáforo grupal.
  3. Se despliega la dotación de personal con sus respectivos semáforos individuales, resumen de compromisos de agenda y alertas de inactividad.
  4. El usuario puede hacer clic en cualquier funcionario para realizar *drill-down* y abrir su ficha personal detallada (CU08).

* **Postcondiciones:**  
  El tablero refleja el estado exacto de la gestión territorial sin intervenir ni alterar los registros de base de datos.

* **Relaciones del Caso de Uso:**
  * **Casos Incluidos (`<<include>>`):** *Consolidar Indicadores y Semáforo Grupal*, *CU08: Drill-Down a Ficha Personal*.
  * **Casos Extendidos (`<<extend>>`):**
    * *Notificar Alerta de Compromisos Vencidos:* Notifica de forma destacada las tareas fuera de plazo.
    * *Notificar Delegación Sin Registros:* Alerta si la delegación aún no registra actividades en el período.

---

### FICHA CU10: Generar Informes y Auditar Operaciones

* **Identificador:** `CU10`
* **Nombre:** Generar Informes y Auditar Operaciones
* **Actores Principales:** Coordinador del Sistema, Delegado / Jefatura, Usuario de Consulta
* **Propósito:**  
  Filtrar la información operativa por fechas, áreas y funcionarios para emitir informes ejecutivos consolidados descargables (PDF y Excel) y revisar la bitácora de auditoría inmutable de eventos críticos.

* **Precondiciones:**  
  El usuario debe estar autenticado con permisos autorizados de consulta o coordinación.

* **Flujo Principal de Ejecución:**
  1. El usuario accede al módulo de reportes y auditoría.
  2. Aplica los filtros deseados (rango de fechas, delegación, área funcional o cargo).
  3. El sistema valida los permisos y ámbitos territoriales del solicitante.
  4. El usuario solicita la generación del informe ejecutivo consolidado en formato descargable.
  5. En caso de contar con perfil de administración, el usuario puede inspeccionar la bitácora inalterable de auditoría para verificar quién creó, editó o validó cada registro.

* **Postcondiciones:**  
  El informe es generado conservando la integridad de los datos filtrados y la bitácora de auditoría permanece inalterable.

* **Relaciones del Caso de Uso:**
  * **Casos Incluidos (`<<include>>`):** *Validar Ámbito y Permisos de Consulta*.
  * **Casos Extendidos (`<<extend>>`):**
    * *Notificar Sin Coincidencias en Filtros:* Informa si la combinación de filtros no arroja resultados.
    * *Notificar Acceso Restringido a Auditoría:* Deniega el acceso a la bitácora a usuarios sin permisos directos.

---

## 5. PLAN DE PRUEBAS DEL SISTEMA Y GUÍA DE DEMOSTRACIÓN

Para la defensa de la evaluación, diseñamos un plan de pruebas manual basado en **escenarios reales de uso**, pensado para ser ejecutado en vivo frente al docente en la instancia de AWS EC2 (`http://3.229.11.31`).

### 5.1 Credenciales de Prueba por Perfil

Para realizar las pruebas sin interferencias de permisos, configuramos cuentas con distintos alcances:

* **Superusuario / Administrador:**  
  * **Usuario:** `admin` | **Contraseña:** `admin`  
  * **Alcance:** Control total del sistema, acceso a Django Admin y todas las delegaciones.
* **Operador Delegación Centro (D01):**  
  * **Usuario:** `operador_d01` | **Contraseña:** `admin`  
  * **Alcance:** Operación exclusiva dentro de la Delegación La Serena Centro.
* **Operador Delegación Las Compañías (D02):**  
  * **Usuario:** `operador_d02` | **Contraseña:** `admin`  
  * **Alcance:** Operación exclusiva dentro de la Delegación Las Compañías.

---

### 5.2 Escenarios de Prueba Paso a Paso

#### BLOQUE 1: Control de Acceso, Autenticación y Cierre de Sesión

* **Prueba 1.1: Inicio de sesión exitoso**  
  * **Objetivo:** Comprobar el ingreso correcto al sistema.  
  * **Pasos:** Ir a `http://3.229.11.31/login/`, ingresar `admin` / `admin` y presionar *Ingresar*.  
  * **Resultado Esperado:** Redirige al panel principal (`/`). La barra superior muestra el nombre del usuario, el rol asignado y el badge de la delegación activa.

* **Prueba 1.2: Rechazo con contraseña inválida**  
  * **Objetivo:** Comprobar que el sistema rechaza credenciales erróneas.  
  * **Pasos:** Cerrar sesión, volver a `/login/`, ingresar `admin` con clave `erronea123` e intentar entrar.  
  * **Resultado Esperado:** El sistema no ingresa, permanece en el login y muestra un mensaje de advertencia seguro sin dar pistas de qué dato falló.

* **Prueba 1.3: Protección de rutas privadas (Sin Sesión)**  
  * **Objetivo:** Validar que ninguna ruta interna es accesible anónimamente.  
  * **Pasos:** En una pestaña limpia sin sesión, escribir directamente:  
    `http://3.229.11.31/mantenedores/delegaciones/`  
  * **Resultado Esperado:** El middleware de Django intercepta la petición y redirige forzosamente a `/login/?next=...`.

* **Prueba 1.4: Cierre de sesión y control del historial**  
  * **Objetivo:** Asegurar que el botón "Atrás" del navegador no recupere datos privados.  
  * **Pasos:** Iniciar sesión, hacer clic en *[Cerrar Sesión]* y luego presionar el botón "Atrás" del navegador.  
  * **Resultado Esperado:** El navegador no muestra la página autenticada y solicita volver a iniciar sesión.

---

#### BLOQUE 2: Recuperación Segura de Contraseña

* **Prueba 2.1: Solicitud de código con correo corporativo**  
  * **Objetivo:** Solicitar código temporal de reseteo.  
  * **Pasos:** Ingresar a `http://3.229.11.31/recuperar/`, escribir el correo corporativo del administrador y presionar enviar.  
  * **Resultado Esperado:** El sistema emite un mensaje neutro de confirmación informando que el correo fue procesado.

* **Prueba 2.2: Prevención de enumeración de usuarios**  
  * **Objetivo:** Proteger la privacidad de los funcionarios ante correos inexistentes.  
  * **Pasos:** En la misma pantalla, ingresar un correo inventado como `noexiste@inacap.test`.  
  * **Resultado Esperado:** El sistema responde exactamente con el mismo mensaje genérico, impidiendo que atacantes descubran qué correos están registrados.

---

#### BLOQUE 3: Módulo Organización y Aislamiento Territorial

* **Prueba 3.1: Alta de una nueva delegación municipal**  
  * **Objetivo:** Verificar la creación de entidades organizacionales en base de datos.  
  * **Pasos:** Con el usuario `admin`, ingresar a `/mantenedores/delegaciones/`, presionar *Nueva Delegación*, ingresar Código `D99` y Nombre `Delegación San Joaquín`.  
  * **Resultado Esperado:** La delegación se guarda en MySQL y aparece de inmediato en el listado oficial.

* **Prueba 3.2: Demostración de Aislamiento Territorial (Prueba de Seguridad)**  
  * **Objetivo:** Asegurar que los operadores no puedan ver datos de otras delegaciones.  
  * **Pasos:**  
    1. Iniciar sesión con `operador_d01` (La Serena Centro).  
    2. Verificar que en la lista de actividades solo aparecen registros de su jurisdicción (D01).  
    3. Intentar acceder por URL a una actividad perteneciente a D02 (Las Compañías).  
  * **Resultado Esperado:** El sistema deniega el acceso o filtra automáticamente la consulta, impidiendo la fuga de datos interdelegacional.

---

#### BLOQUE 4: Registro de Actividades y Códigos de Evidencia

* **Prueba 4.1: Registro de una nueva atención vecinal**  
  * **Objetivo:** Comprobar la captura de atenciones y la generación del código verificador.  
  * **Pasos:** Ir a `/atenciones/nueva/`, ingresar el RUT del vecino, su nombre, seleccionar el tipo de atención (Social/Territorial) y la descripción de la ayuda solicitada. Presionar *Guardar*.  
  * **Resultado Esperado:** Se almacena el registro y el sistema le asigna un Código Único de Evidencia inmutable con formato `EVI-YYYYMMDD-XXXX`.

* **Prueba 4.2: Carga y verificación técnica de respaldo fotográfico**  
  * **Objetivo:** Probar el ciclo completo de validación de evidencias.  
  * **Pasos:**  
    1. Desde la actividad recién creada, adjuntar una imagen fotográfica `.png` o `.jpg`.  
    2. Comprobar que la evidencia pasa al estado *'Pendiente de Validación'*.  
    3. Ingresar al panel de auditoría con perfil supervisor y presionar *Aprobar*.  
  * **Resultado Esperado:** La evidencia queda firmada por el supervisor, cambia a estado *Aprobada* y se suma al cumplimiento de metas del funcionario.

---

#### BLOQUE 5: Agenda Colectiva y Tablero Kanban

* **Prueba 5.1: Creación de un compromiso vecinal**  
  * **Objetivo:** Agendar una tarea territorial con fecha límite inmutable.  
  * **Pasos:** Ir a `/agenda/nuevo/`, seleccionar el vecino solicitante, asignar al funcionario responsable y fijar la fecha comprometida.  
  * **Resultado Esperado:** El compromiso se crea en estado *'Ingresado'* y se posiciona en la primera columna del tubo de trabajo.

* **Prueba 5.2: Transición de estados en el Tablero Kanban**  
  * **Objetivo:** Probar la progresión operativa y la traza histórica.  
  * **Pasos:** En `/agenda/resumen/`, mover el compromiso de *'Ingresado'* a *'En proceso'* y finalmente a *'Realizado'* ingresando una nota de avance.  
  * **Resultado Esperado:** La tarjeta se reubica en la columna correspondiente y en el historial queda grabada la fecha, hora y usuario que efectuó cada cambio.

---

#### BLOQUE 6: Ficha de Resultados, Topes y Semáforo Dinámico

* **Prueba 6.1: Cálculo con topes y bonificaciones en la Ficha Personal**  
  * **Objetivo:** Validar la regla de negocio municipal (tope del 150% por ítem).  
  * **Pasos:** Ingresar a `/resultados/persona/1/` para inspeccionar la ficha oficial de un funcionario.  
  * **Resultado Esperado:** El sistema calcula el porcentaje de avance respecto a la meta esperada a la fecha. Si un ítem supera el 100%, se calcula hasta el tope legal del 150%, protegiendo la ponderación global del funcionario.

* **Prueba 6.2: Dinámica de colores del Semáforo**  
  * **Objetivo:** Verificar las alertas visuales según rendimiento.  
  * **Criterios Evaluados:**  
    * **Verde:** Cumplimiento ≥ 90% (Gestión al día).  
    * **Ámbar:** Cumplimiento entre 60% y 89% (Alerta preventiva).  
    * **Rojo:** Cumplimiento < 60% (Rezago operativo crítico).  
  * **Resultado Esperado:** Los indicadores visuales y barras de progreso reflejan fielmente el color correspondiente según los números del funcionario.

---

#### BLOQUE 7: Comprobación en Django Admin y Persistencia MySQL

* **Prueba 7.1: Demostración en Django Admin**  
  * **Objetivo:** Mostrar los modelos administrables implementados.  
  * **Pasos:** Ir a `/admin/` con credenciales de administrador, entrar a los módulos de `Actividades`, `Personas` y `Metas`.  
  * **Resultado Esperado:** Se demuestran las opciones de búsqueda por RUT, filtros por delegación y edición de campos en el panel de Django.

* **Prueba 7.2: Verificación de tablas físicas en phpMyAdmin**  
  * **Objetivo:** Demostrar la persistencia real en la base de datos relacional de la nube.  
  * **Pasos:** Abrir `http://3.229.11.31/phpmyadmin/`, iniciar sesión como `sgr_user` y seleccionar la base de datos del proyecto.  
  * **Resultado Esperado:** El docente puede inspeccionar las tablas físicas creadas por las migraciones (`organizacion_delegacion`, `actividades_actividad`, `agenda_compromiso`, etc.), sus claves primarias, foráneas y los registros que antes residían en archivos JSON.

---

## 6. MATRIZ DE TRAZABILIDAD INTEGRAL

Para garantizar que cada requerimiento planteado en la evaluación cuente con respaldo directo en código y pruebas, presentamos la correspondencia del sistema:

* **Gestión de Estructura y Funcionarios:**  
  * Requerimiento: `RF-01`  
  * Caso de Uso: `CU01` (Administrar Usuarios y Delegaciones)  
  * Modelos Django: `organizacion.Delegacion`, `organizacion.Persona`  
  * Endpoint Web: `/mantenedores/delegaciones/`  
  * Casos de Prueba: `Prueba 3.1`, `Prueba 3.2`

* **Parametrización de Metas y Períodos:**  
  * Requerimiento: `RF-02`  
  * Caso de Uso: `CU02` (Configurar Parámetros y Metas)  
  * Modelos Django: `resultados.Periodo`, `resultados.Meta`  
  * Endpoint Web: `/admin/resultados/meta/`  
  * Casos de Prueba: `Prueba 6.1`, `Prueba 7.1`

* **Registro Operativo de Atenciones:**  
  * Requerimiento: `RF-03`  
  * Caso de Uso: `CU03` (Registrar Actividad Diaria)  
  * Modelos Django: `actividades.Actividad`  
  * Endpoint Web: `/atenciones/nueva/`  
  * Casos de Prueba: `Prueba 4.1`

* **Carga de Respaldo Fotográfico:**  
  * Requerimiento: `RF-04`  
  * Caso de Uso: `CU04` (Adjuntar Evidencia Fotográfica)  
  * Modelos Django: `actividades.Evidencia`  
  * Endpoint Web: `/atenciones/evidencia/<id>/`  
  * Casos de Prueba: `Prueba 4.2`

* **Auditoría y Validación Técnica:**  
  * Requerimiento: `RF-05`  
  * Caso de Uso: `CU05` (Validar Evidencia de Actividad)  
  * Modelos Django: `actividades.Validacion`  
  * Endpoint Web: `/atenciones/auditoria/`  
  * Casos de Prueba: `Prueba 4.2`

* **Registro de Compromisos en Tubo:**  
  * Requerimiento: `RF-06`  
  * Caso de Uso: `CU06` (Registrar y Asignar Compromisos)  
  * Modelos Django: `agenda.Compromiso`  
  * Endpoint Web: `/agenda/nuevo/`  
  * Casos de Prueba: `Prueba 5.1`

* **Tubo de Trabajo y Seguimiento de Estados:**  
  * Requerimiento: `RF-07`  
  * Caso de Uso: `CU07` (Gestionar Estados y Reasignar)  
  * Modelos Django: `agenda.Compromiso`, `agenda.HistorialEstado`  
  * Endpoint Web: `/agenda/resumen/`  
  * Casos de Prueba: `Prueba 5.2`

* **Ficha Personal y Cálculo de Semáforo:**  
  * Requerimiento: `RF-08`  
  * Caso de Uso: `CU08` (Consultar Ficha Personal)  
  * Modelos Django: Vistas y motor de cálculo SGR  
  * Endpoint Web: `/resultados/persona/<id>/`  
  * Casos de Prueba: `Prueba 6.1`, `Prueba 6.2`

* **Tablero Ejecutivo de Delegación:**  
  * Requerimiento: `RF-09`  
  * Caso de Uso: `CU09` (Monitorear Tablero de Delegación)  
  * Modelos Django: Consolidación de indicadores  
  * Endpoint Web: `/resultados/tablero/<id>/`  
  * Casos de Prueba: `Prueba 6.2`

* **Reportabilidad y Bitácora:**  
  * Requerimiento: `RF-10`  
  * Caso de Uso: `CU10` (Generar Informes y Auditar)  
  * Modelos Django: Vistas de reporte y auditoría Django  
  * Endpoint Web: `/resultados/informe/`  
  * Casos de Prueba: `Prueba 7.1`, `Prueba 7.2`

---

## 7. CONCLUSIONES DEL EQUIPO DE DESARROLLO

El desarrollo de esta segunda evaluación representó un aprendizaje fundamental para nosotros como equipo:

1. **De Prototipo a Sistema Productivo:** Pasar de maquetas con archivos JSON a una base de datos relacional MySQL completamente integrada con Django ORM nos permitió dimensionar la importancia del diseño del Modelo Entidad-Relación y de las migraciones para mantener la consistencia de datos.
2. **Despliegue Real en la Nube:** Configurar una máquina virtual en Amazon EC2 con Linux, gestionar permisos, entornos virtuales y servidores web como Nginx y Gunicorn nos acercó al trabajo real de un equipo de desarrollo profesional.
3. **Seguridad y Criterio Profesional:** La incorporación de variables de entorno y el aislamiento territorial demuestran que una aplicación municipal no solo debe verse bien, sino que debe resguardar la privacidad de los vecinos y garantizar la trazabilidad de cada acción pública.

Con este informe, la carpeta de diagramas en alta resolución y la plataforma desplegada en vivo, damos por cumplidos todos los objetivos de la Evaluación Sumativa N°2.
