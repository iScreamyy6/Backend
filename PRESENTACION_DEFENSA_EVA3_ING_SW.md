# PRESENTACIÓN Y DEFENSA ORAL: EVALUACIÓN SUMATIVA N° 3
## INGENIERÍA DE SOFTWARE (TI2043) — INACAP SEDE LA SERENA

**Proyecto:** Sistema de Gestión de Resultados (SGR) — Ilustre Municipalidad de La Serena  
**Ponderación:** 35% de la Asignatura  
**Modalidad:** Exposición Oral de 10 Minutos Cronometrados con Demostración en Vivo  
**Artefactos Centrales:** Prototipo Interactivo de Wireframes (`/wireframes/`), Prototipo Django en AWS EC2 y Justificación de Artefactos UML de la Evaluación 2  

---

## 1. ESTRUCTURA Y CRONOGRAMA DE LA PRESENTACIÓN (10 MINUTOS)

Para cumplir al 100% con la rúbrica de 100 puntos del profesor, la presentación se organiza en 6 bloques cronometrados:

```
[0:00 - 1:30]   Bloque 1: Portada, Problemática Territorial y Tendencias Cloud (SaaS / IaaS)
[1:30 - 3:00]   Bloque 2: Defensa de la Metodología de la Evaluación 2 (Híbrida: Cascada + Scrum)
[3:00 - 5:00]   Bloque 3: Trazabilidad UML Eva 2 vs. Wireframes Interactivos (Casos de Uso a Pantallas)
[5:00 - 7:00]   Bloque 4: Demostración en Vivo del Prototipo Funcional (Roles RBAC y Tubo de Trabajo)
[7:00 - 8:30]   Bloque 5: Estándares de Calidad y Ciberseguridad (OWASP, Ley 21.459 y Testing)
[8:30 - 10:00]  Bloque 6: Conclusiones, Retorno de Inversión y Ronda de Preguntas
```

---

## 2. GUION DE DIAPOSITIVAS (SLIDE BY SLIDE) CON EL LIBRETO EXACTO (SPEECH)

---

### DIAPOSITIVA 1: PORTADA Y PRESENTACIÓN DEL EQUIPO (0:00 – 0:45)
* **Título:** Sistema de Gestión de Resultados (SGR) — Ilustre Municipalidad de La Serena
* **Subtítulo:** Prototipado, Calidad de Software y Validación de Requerimientos de Co-Creación (Etapa 3)
* **Elementos Visuales:** Logo de INACAP, Escudo Oficial de la Municipalidad de La Serena, nombres de los integrantes del equipo y fecha.
* **Qué debes decir en voz alta (Speech):**
  > *"Buenos días profesor y compañeros. Hoy presentamos la defensa final de la Evaluación Sumativa N° 3 de Ingeniería de Software para el Sistema de Gestión de Resultados (SGR) de la Ilustre Municipalidad de La Serena.*
  > 
  > *El objetivo de esta presentación es doble: primero, demostrar nuestro prototipo interactivo funcional en producción; y segundo, defender con fundamentos técnicos las decisiones de modelamiento, arquitectura y metodología tomadas en la Evaluación 2, demostrando cómo cada requerimiento levantado con el municipio se convirtió en una solución real, segura y trazable."*

---

### DIAPOSITIVA 2: EL PROBLEMA TERRITORIAL Y TENDENCIAS CLOUD (0:45 – 1:30)
* **Título:** Diagnóstico Operativo y Arquitectura Cloud (IaaS / SaaS)
* **Elementos Visuales:** Esquema de La Serena dividida en delegaciones (Las Compañías, La Antena, Centro, Avenida del Mar, Rural) y diagrama de nube AWS EC2.
* **Criterio de Rúbrica Evaluado:** 3.1.1 (Nuevas tendencias tecnológicas SaaS, IaaS y Cloud Computing).
* **Qué debes decir en voz alta (Speech):**
  > *"El problema que diagnosticamos en el municipio fue la fragmentación operativa: cada delegación territorial operaba con planillas Excel aisladas. Si un vecino pedía una reparación de luminaria en Las Compañías y luego consultaba en el edificio consistorial central, nadie tenía registro del requerimiento. Se duplicaban esfuerzos y no había trazabilidad.*
  > 
  > *Para dar respuesta a esto bajo las nuevas tendencias tecnológicas, descartamos la instalación de servidores locales en cada delegación y optamos por una arquitectura en la nube bajo el modelo **IaaS (Infraestructura como Servicio)** desplegada en **Amazon Web Services (AWS EC2)** con Ubuntu Server y MySQL.*
  > 
  > *Esto permite al municipio operar bajo un modelo **SaaS (Software como Servicio)** interno: los funcionarios no requieren instalar nada; ingresan por navegador web o dispositivos móviles con alta disponibilidad y respaldo centralizado."*

---

### DIAPOSITIVA 3: DEFENSA DE LA METODOLOGÍA ELEGIDA EN EVA 2 (1:30 – 3:00)
* **Título:** Justificación Metodológica: ¿Por qué un Enfoque Híbrido (Cascada + Scrum)?
* **Elementos Visuales:** Comparativa de fases: Fase 1 (Cascada para análisis estricto) + Fase 2 y 3 (Scrum iterativo con 3 Sprints).
* **Criterio de Rúbrica Evaluado:** Criterio 2 (20 puntos: Aplicación y dominio de metodologías).
* **Qué debes decir en voz alta (Speech):**
  > *"Uno de los puntos centrales solicitados en la pauta es justificar las elecciones tomadas en la Evaluación 2. Nosotros seleccionamos y defendemos un **Enfoque Híbrido de Ingeniería de Software**:*
  > 
  > *1. **¿Por qué Cascada para la Etapa de Análisis?** En la administración pública rige el principio de legalidad y rendición de cuentas. No podíamos improvisar la estructura de datos. Fue mandatorio utilizar un ciclo secuencial para levantar los 38 Requerimientos Funcionales, normalizar la base de datos en Tercera Forma Normal (3NF) y diseñar los diagramas de Casos de Uso antes de codificar.*
  > 
  > *2. **¿Por qué Scrum para el Desarrollo y Prototipado?** Una vez congelado el alcance base, pasamos a Scrum con **3 Sprints de dos semanas**. Dividimos el backlog en Historias de Usuario estimadas en Story Points:*
  > * * **Sprint 1:** Autenticación, perfiles y navegación base.*
  > * * **Sprint 2:** Mantenedores CRUD de delegaciones, vecinos y gestión unificada.*
  > * * **Sprint 3:** Tablero Kanban Tubo de Trabajo, evidencias fotográficas y despliegue cloud.*
  > 
  > *Este modelo híbrido nos dio lo mejor de dos mundos: la rigurosidad documental del modelo tradicional y la velocidad adaptativa de Scrum."*

---

### DIAPOSITIVA 4: MATRIZ DE TRAZABILIDAD (EVA 2 -> EVA 3) (3:00 – 4:00)
* **Título:** Trazabilidad Estricta: De los Requerimientos al Prototipo
* **Elementos Visuales:** Cadena de valor: Requerimiento Funcional (RF) -> Caso de Uso (CU) -> Diagrama de Clases -> Wireframe -> Pantalla Final.
* **Criterio de Rúbrica Evaluado:** Criterio 5 (20 puntos: Reflejo de los diagramas de Caso de Uso en el prototipo).
* **Qué debes decir en voz alta (Speech):**
  > *"Para asegurar calidad de software, implementamos una **cadena de trazabilidad bidireccional**: ningún botón en la pantalla existe por azar; cada elemento responde a un artefacto de la Evaluación 2:*
  > * * El **RF-01 (Autenticación)** dio origen al **CU-01 (Iniciar Sesión)** y **CU-02 (Recuperar Clave)**, reflejados en el Mockup 1 y en el login con CSRF token.*
  > * * El **RF-05 (Gestión Unificada)** generó el **CU-05 (Registrar Atención Ciudadana)**, que consume la clase `Actividad` y vincula automáticamente al `Vecino` por RUT.*
  > * * El **RF-07 (Tubo de Trabajo)** originó el **CU-07 (Monitorear Compromisos)**, modelado en el Diagrama de Clases mediante la relación entre `Actividad` y `Compromiso`, y materializado en nuestro Tablero Kanban interactivo.*
  > 
  > *Cada uno de los 10 Casos de Uso del informe técnico tiene su contraparte exacta en el sistema."*

---

### DIAPOSITIVA 5: DEMOSTRACIÓN 1 — WIREFRAMES INTERACTIVOS (4:00 – 5:30)
* **Título:** Artefacto de Wireframes y Mockups Interactivos
* **Acción:** Abrir en el navegador la URL `http://3.213.246.194/wireframes/` (o en localhost).
* **Qué debes mostrar y decir en voz alta (Speech):**
  > *(Mostrando la pantalla interactiva de Wireframes)*
  > *"Aquí observamos nuestro artefacto de Wireframes Interactivos, desarrollado con HTML5 y Bootstrap 5, respetando la guía de estilo institucional de La Serena (`#AD0000` carmesí).*
  > 
  > *Quiero destacar tres aspectos clave validados con los usuarios:*
  > 1. * **Mockup 2 (Dashboard Multirrol):** Si selecciono el perfil Administrador, veo métricas globales de toda la comuna. Si cambio al perfil Supervisor, el menú se adapta y solo me permite ver mi delegación asignada.*
  > 2. * **Mockup 3 (Ingreso de Gestión):** Diseñamos un formulario ágil donde al escribir el RUT del vecino, se ejecuta una búsqueda asíncrona que autocompleta nombre, teléfono y dirección, reduciendo el tiempo de atención de 8 minutos a menos de 90 segundos.*
  > 3. * **Mockup 4 (Tubo de Trabajo Kanban):** Las tarjetas visualizan el estado de los compromisos barriales. Los funcionarios pueden arrastrar compromisos entre 'Ingresada', 'En Proceso' y 'Realizado'."*

---

### DIAPOSITIVA 6: DEMOSTRACIÓN 2 — PROTOTIPO FUNCIONAL Y CONTROL RBAC (5:30 – 7:00)
* **Título:** Demostración del Prototipo en Producción (AWS EC2)
* **Acción:** Entrar a `http://3.213.246.194/` con usuario `admin` o supervisor.
* **Criterio de Rúbrica Evaluado:** Criterio 1 (25 puntos: Cumplimiento de RF y RNF).
* **Qué debes mostrar y decir en voz alta (Speech):**
  > *(Iniciando sesión en la aplicación real)*
  > *"Ahora pasamos al sistema real operando en AWS EC2:*
  > * * **Control de Acceso Basado en Roles (RBAC):** Demostramos que un usuario Administrativo tiene bloqueado el acceso a la creación de usuarios y roles, respondiendo con redirección segura y mensaje de denegación.*
  > * * **Filtro Territorial Estricto:** Un supervisor asignado a la Delegación La Antena no puede ver ni modificar gestiones pertenecientes a Las Compañías o Centro Histórico. Los datos están estrictamente segmentados.*
  > * * **Bandeja de Evidencias:** Cada gestión completada exige la carga de evidencia respaldatoria y pasa por un ciclo de revisión ('En Revisión', 'Aprobada', 'Requiere Información'). Si la gestión es cuantitativa, impacta automáticamente en el semáforo comunal de metas de los funcionarios."*

---

### DIAPOSITIVA 7: ESTÁNDARES DE CALIDAD Y PRUEBAS AUTOMATIZADAS (7:00 – 8:00)
* **Título:** Calidad del Software: Arnés de Pruebas y Versionamiento
* **Elementos Visuales:** Captura de la terminal con `test_suite.py` pasando con 100% de éxito, ramas de Git semántico.
* **Criterio de Rúbrica Evaluado:** Criterio 3 (20 puntos: Estándares de calidad y gestión).
* **Qué debes decir en voz alta (Speech):**
  > *"En ingeniería de software la calidad no se presume, se prueba. Implementamos un arnés automatizado en `test_suite.py` con **14 suites de pruebas** ejecutadas sobre la base de datos:*
  > * * Validamos que ninguna sumatoria de metas supere el 100% por funcionario.*
  > * * Validamos la expiración matemática e invalidación de tokens de recuperación de clave.*
  > * * Validamos la integridad referencial de los 6 mantenedores CRUD.*
  > * * Validamos la idempotencia: las pruebas se ejecutan, limpian sus datos y dejan la base de datos en estado canónico perfecto sin basura.*
  > 
  > *En la gestión del proyecto usamos Git con mensajes semánticos convencionales (`feat:`, `fix:`, `docs:`) sincronizados en GitHub."*

---

### DIAPOSITIVA 8: CIBERSEGURIDAD Y MARCO NORMATIVO CHILENO (8:00 – 9:00)
* **Título:** Ciberseguridad Aplicada: OWASP Top 10 y Ley N° 21.459
* **Elementos Visuales:** Diagrama de capas de seguridad: Protección CSRF, Cifrado Argon2/PBKDF2, Prevención de SQL Injection y Protección de Datos Personales (Ley 19.628).
* **Criterio de Rúbrica Evaluado:** Criterio 4 (15 puntos: Estándares de seguridad).
* **Qué debes decir en voz alta (Speech):**
  > *"En el apartado de seguridad, diseñamos la solución alineada con el estándar **OWASP Top 10** y la legislación chilena vigente:*
  > 1. * **Inyección SQL (OWASP A03):** Mitigada al 100% mediante el ORM de Django con consultas parametrizadas.*
  > 2. * **Cross-Site Request Forgery (OWASP A01):** Todos los formularios POST exigen token criptográfico `csrf_token`.*
  > 3. * **Ley N° 21.459 de Delitos Informáticos:** Implementamos auditoría interna registrando fecha, hora, IP y usuario autor de cada modificación de evidencia.*
  > 4. * **Ley N° 19.628 de Protección de Datos Personales:** Los datos sensibles de los vecinos (RUT, teléfonos y correos) cuentan con control de visualización y enmascaramiento según el perfil del funcionario."*

---

### DIAPOSITIVA 9: CONCLUSIONES Y RETORNO DE INVERSIÓN (9:00 – 10:00)
* **Título:** Conclusiones, Impacto Ciudadano y Cierre
* **Elementos Visuales:** Cuadro comparativo Antes (Planillas manuales, 8 min por trámite) vs Después (SGR Centralizado, <90 seg, trazabilidad 100%).
* **Qué debes decir en voz alta (Speech):**
  > *"Para concluir:*
  > * * Cumplimos el 100% de los requerimientos funcionales y no funcionales solicitados en las guías 1, 2 y 3.*
  > * * Entregamos un prototipo funcional en la nube de AWS que optimiza los tiempos de gestión territorial de la Municipalidad de La Serena.*
  > * * Demostramos que una sólida etapa de modelamiento UML en la Evaluación 2 es la clave para que la construcción y prototipado en la Evaluación 3 sea limpia, robusta y sin retrabajo.*
  > 
  > *Agradecemos su atención y quedamos a disposición de la comisión para sus preguntas. Muchas gracias."*

---

## 3. BANCO DE PREGUNTAS DIFÍCILES DEL PROFESOR Y CÓMO RESPONDERLAS

### Pregunta 1: *"¿Por qué no usaron Scrum desde el día uno si es la metodología que más se usa en la industria?"*
* **Respuesta Correcta:**
  > *"Profesor, porque en el contexto municipal y público rigen normativas de auditoría estrictas donde los requerimientos de datos no pueden cambiar arbitrariamente en cada sprint. Si hubiésemos iniciado con Scrum puro sin un modelamiento relacional previo, habríamos cometido errores graves en la normalización de la base de datos (como duplicar vecinos o romper la integridad referencial de los compromisos). Por eso usamos un modelo Híbrido: Cascada para el análisis estructural y Scrum para la construcción ágil de los componentes visuales y funcionales."*

### Pregunta 2: *"¿Dónde se refleja el Diagrama de Componentes que hicieron en la Evaluación 2?"*
* **Respuesta Correcta:**
  > *"Se refleja directamente en la arquitectura física de nuestro código: la capa web desacoplada en `templates/`, los controladores modulares en `views.py` y `views_mantenedores.py`, los modelos encapsulados en `models.py` respetando las claves foráneas, y la conexión centralizada hacia el motor MySQL mediante variables de entorno en `settings.py`."*

### Pregunta 3: *"¿Cómo aseguran que un funcionario no suplante a otro o modifique evidencias aprobadas?"*
* **Respuesta Correcta:**
  > *"Mediante dos controles estrictos: primero, el control de roles RBAC a nivel de vista donde solo el rol Supervisor puede dictaminar o aprobar evidencias; y segundo, mediante campos inmutables de auditoría (`usuario_creador`, `usuario_revisor`, `fecha_revision`) que no pueden ser alterados desde los formularios del cliente, cumpliendo con la Ley 21.459 de integridad de datos."*

---

## 4. CHECKLIST FINAL ANTES DE ENTRAR A LA SALA DE PRESENTACIÓN

1. Servidor AWS EC2 activo y respondiendo en `http://3.213.246.194/`.
2. Pestaña de Wireframes abierta y precargada en `http://3.213.246.194/wireframes/`.
3. Pestaña de la aplicación real abierta con login listo.
4. Terminal abierta en la carpeta del proyecto con el comando `python test_suite.py` listo para pulsar Enter si el profesor pide ver pruebas en vivo.
5. Copia en PDF del informe técnico disponible: [INFORME_EVA3_INGENIERIA_DE_SOFTWARE_SGR.pdf](file:///d:/Django/Backend/Contexto%20de%20la%20problematica/06_Entregables_e_Informe_Eva3/INFORME_EVA3_INGENIERIA_DE_SOFTWARE_SGR.pdf).
