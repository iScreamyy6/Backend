# 📋 Contexto Base del Proyecto — SGR (Sistema de Gestión de Resultados)

> **Propósito de este documento:** Servir como instrucciones base y fuente de verdad técnica para que cualquier integrante del equipo (o su IA) pueda entender el contexto del proyecto, su arquitectura unificada y programar de forma coherente.

---

## 1. Información del Proyecto

| Campo | Valor |
|---|---|
| **Nombre** | Sistema de Gestión de Resultados (SGR) |
| **Institución** | INACAP — Sede La Serena |
| **Asignatura** | Programación Back End (TI3041) |
| **Docente** | Alex Díaz Araos |
| **Cliente (caso institucional)** | Delegaciones territoriales — Ilustre Municipalidad de La Serena |
| **Integrantes** | Álvaro Obregón, Benjamín Antipa, Emanuel Román |
| **Framework** | Django 6.x (Python 3.12 / 3.14) |
| **Base de datos** | MySQL 8.0 (Producción en AWS EC2) / SQLite3 (Desarrollo local) |
| **Servidor Producción** | AWS EC2 Ubuntu Linux (`3.229.11.31`), Apache Proxy Inverso (Puerto 80), `systemd` (`sgr-django.service`) |
| **Repositorio GitHub** | [https://github.com/iScreamyy6/Backend](https://github.com/iScreamyy6/Backend) |

---

## 2. Problema que Resuelve

Las delegaciones territoriales de la Municipalidad de La Serena operaban históricamente con planillas Excel independientes, generando dificultades críticas:

- Falta de una **visión transversal y unificada** de la gestión municipal descentralizada.
- **Fragmentación y duplicidad** entre las solicitudes vecinales (atención ciudadana), los operativos en terreno y los compromisos adquiridos.
- Carencia de un **método estandarizado de seguimiento** para compromisos intersectoriales con plazos y juntas de vecinos.
- Ausencia de **códigos únicos correlativos** para auditar y verificar con evidencias fotográficas el trabajo realizado.
- Dificultad para medir el **cumplimiento de metas individuales y colectivas** en un semáforo gerencial objetivo.

### Objetivo General
Centralizar en una plataforma web back-end modular el registro, seguimiento intersectorial, verificación con evidencias y medición del desempeño de las delegaciones municipales de La Serena.

---

## 3. Arquitectura del Proyecto y Evolución Conceptual

### 3.1 Estructura de Directorios Actual

```
Backend/
├── Municipalidad/                    # Configuración central del proyecto Django
│   ├── settings.py                   # Configuración multi-entorno (.env)
│   ├── urls.py                       # Enrutamiento raíz y endpoints API
│   ├── views.py                      # Dashboard de inicio con métricas por rol
│   ├── views_auth.py                 # Login, logout y recuperación de clave (3 pantallas)
│   ├── views_mantenedores.py         # 6 CRUDs + Catálogos oficiales + Exportación Excel
│   └── context_processors.py         # Contexto de delegación activa y roles para templates
├── organizacion/                     # App: Delegaciones, Roles, Usuarios y Funcionarios
│   ├── models.py                     # Delegacion, Rol, PerfilUsuario, Funcionario
│   ├── views.py                      # Vistas y fichas de unidades y personas
│   └── urls.py
├── actividades/                      # App: Módulo Unificado de Gestiones
│   ├── models.py                     # Actividad (fusión unificada), Evidencia, TipoAtencion, SubAtencion, AtencionCiudadana, GestionSocial
│   ├── views.py                      # Lista unificada con filtros, Formulario unificado, Detalle y Evidencias
│   └── urls.py
├── agenda/                           # App: Módulo Tubo de Trabajo (Método de seguimiento)
│   ├── models.py                     # Compromiso (con FK id_actividad y código TUB-XXXXX)
│   ├── views.py                      # Tablero Kanban por estados y cambio de estado directo
│   └── urls.py
├── resultados/                       # App: Medición, Semáforos y Metas SGR
│   ├── models.py                     # ItemMeta, PeriodoEvaluacion, MetaFuncionario, IndicadorDelegacion
│   ├── views.py                      # Ficha individual (150%), Tablero delegación, Informe Alcaldía
│   └── urls.py
├── static/
│   ├── css/estilos.css               # Hoja de estilos bajo Normas Gráficas de La Serena (#AD0000, Arial)
│   └── img/                          # Logo y escudos oficiales
├── templates/                        # Templates Django organizados por módulo
│   ├── base.html                     # Layout maestro con cabecera y sub-barra contextual
│   ├── inicio.html                   # Dashboard de inicio personalizado según rol
│   ├── actividades/                  # lista_actividades (tabs), formulario_actividad (unificado), detalle
│   ├── agenda/                       # resumen_agenda (Tablero Kanban), lista_compromisos, detalle
│   ├── mantenedores/                 # Plantillas de los 6 CRUDs con SweetAlert2
│   ├── auth/                         # Login y flujo de recuperación en 3 pasos
│   ├── organizacion/                 # Fichas de delegaciones y funcionarios
│   └── resultados/                   # Semáforo general, tablero por unidad e informe formal
├── test_suite.py                     # Suite completa de pruebas automatizadas (100% pass)
├── requirements.txt                  # Dependencias Python (Django, mysqlclient, openpyxl, python-dotenv)
├── SGR-Municipalidad.pem             # Llave privada de conexión segura SSH a AWS EC2
├── Contexto de la problematica/      # Documentación, pautas de evaluación, planes de prueba y wireframes UML
│   ├── 01_Bases_y_Requisitos_Docente/  # Guías y pautas docentes (incluyendo Ingeniería de Software TI2043)
│   ├── 02_Modelamiento_y_Diseno/       # Modelo ER, Wireframes interactivos y cadena de trazabilidad
│   └── 04_Planes_de_Pruebas_SGR/       # Planes de prueba funcionales y de ejecución manual
└── manage.py                         # Interfaz CLI de Django
```

### 3.2 La Gran Fusión de Módulos (Resolución de la Retroalimentación de Entrega)

En las etapas iniciales existía dispersión: *Atención Ciudadana*, *Gestiones Diarias* y *Gestor Social* operaban como pantallas separadas, provocando redundancia y formularios duplicados.

Con la reestructuración arquitectónica:
1. **Atención Ciudadana, Gestiones Territoriales y Casos Sociales se fusionaron prácticamente en un solo flujo:** Toda solicitud vecinal o actividad es conceptualmente una **Gestión**.
2. **El Módulo "Gestiones" (`/actividades/`) es la fuente central de verdad:** Muestra **todas las gestiones** del municipio en una sola vista con pestañas de filtrado rápido y un formulario de ingreso único.
3. **El Módulo "Tubo de Trabajo" (`/agenda/resumen/`) es el Tablero Kanban:** Ya no es un formulario aislado de compromisos redundantes, sino el **método de seguimiento intersectorial** que muestra exclusivamente las gestiones que *se decidió derivar a ese método* (por ejemplo, porque requieren coordinación entre departamentos, obras públicas, maquinaria o plazos acordados con juntas de vecinos).

### 3.3 Estructura de Base de Datos y Saneamiento Relacional

Para dar soporte íntegro a la unificación de módulos y asegurar que ningún registro quede desincronizado o huérfano, el modelo de datos en MySQL cuenta con las siguientes definiciones y relaciones:

1. **Tabla Central `actividades` (Modelo `Actividad` — Módulo Unificado de Gestiones):**
   * **Identificador y Folio Único:** `id_actividad` (PK autoincremental), `codigo` (`GES-XXXXX` o `SOC-XXXXX` autoincremental).
   * **Datos del Solicitante / Vecino:** `solicitante`, `rut_solicitante`, `telefono`, `correo`, `direccion`, `contacto`.
   * **Campo Territorial Dedicado:** `territorio` (`VARCHAR(200)`), permite almacenar el sector, barrio o jurisdicción territorial específica para filtros geográficos y sincronización con el Tubo de Trabajo.
   * **Clasificación por Catálogo Municipal:** `id_tipo` (FK a `TipoAtencion`), `id_subatencion` (FK a `SubAtencion`).
   * **Detalle Operativo:** `solicitud`, `accion`, `responsable`, `id_funcionario` (FK), `id_delegacion` (FK), `item_evaluacion`, `estado` (`Pendiente`, `En Proceso`, `Realizado`).
   * **Integración Relacional y Trazabilidad:**
     * `ingreso_tubo`: Indicador booleano de si la gestión fue derivada al método de Tubo de Trabajo.
     * `id_compromiso`: Clave foránea al registro correlativo en `Compromiso` (`TUB-XXXXX`).
     * `id_atencion`: Clave foránea opcional a `AtencionCiudadana` para trazabilidad unificada.
     * `id_gestion_social`: Clave foránea opcional a `GestionSocial` para enlace a la ficha social.
   * **Ficha Especializada del Gestor Social (Flujo Multi-Etapa):** `es_gestion_social`, `requiere_visita`, `fecha_programada_visita`, `observaciones_sociales`, `primera_gestion`, `segunda_gestion`, `fecha_visita`, `fecha_entrega_informe`, `tercera_gestion`, `fecha_entrega_beneficio`.
   * **Auditoría:** `codigo_evidencia` (`EVI-YYYYMMDD-XXXX`), `fecha_registro`.

2. **Tabla `compromisos_tubo` (Modelo `Compromiso` — Módulo Tubo de Trabajo):**
   * **Identificador y Código:** `id_compromiso` (PK autoincremental), `codigo` (`TUB-XXXXX`).
   * **Vínculo con la Gestión de Origen:** `id_actividad` (FK a `Actividad`, `on_delete=models.SET_NULL`). Toda tarjeta en el Tablero Kanban visualiza de qué gestión proviene mediante la insignia interactiva `[GES-XXXXX]` o `[SOC-XXXXX]`.
   * **Campos del Compromiso:** `actividad` (descripción/acuerdos), `solicitante`, `territorio`, `responsable`, `id_responsable` (FK), `id_delegacion` (FK), `fecha_solicitud`, `fecha_compromiso`, `area_apoyo`, `estado` (`INGRESADO`, `PENDIENTE`, `EN PROCESO`, `REALIZADO`), `observaciones`.

3. **Saneamiento y Coherencia Relacional Implementado:**
   * **Eliminación de huérfanos:** Se depuraron compromisos de pruebas previas y se vincularon de forma estricta los registros activos.
   * **Orden de persistencia atómico:** Cuando se registra una gestión que deriva al Tubo, el sistema guarda primero la `Actividad` y luego el `Compromiso` inyectando inmediatamente `id_actividad=actividad`, asegurando enlace bidireccional instantáneo.
   * **Backfill territorial:** Se completó el campo `territorio` en todos los registros preexistentes de la base de datos tanto en local como en producción (`3.229.11.31`).

---

## 4. Módulos del Sistema y Flujo Operativo

### 4.1 Módulo Central de Gestiones (`/actividades/`)
Reúne la totalidad de los requerimientos ingresados en la comuna, eliminando silos de información.

| URL | Vista | Descripción |
|---|---|---|
| `/actividades/` | `lista_actividades` | **Libro General de Gestiones** con pestañas de filtro con conteo en tiempo real: `Todas`, `Atención Ciudadana`, `Gestión Territorial`, `Casos Gestor Social` y `Derivadas al Tubo`. |
| `/actividades/nueva/` | `formulario_actividad` | **Formulario de Registro Unificado**: captura solicitante, RUT, teléfono, catálogo temático dependiente (Tipo/SubAtención), campos de terreno, switch para ficha de Gestor Social y switch para derivar al Tubo. |
| `/actividades/actividad/<id>/` | `detalle_actividad` | Ficha técnica completa de la gestión con trazabilidad, cronograma multi-etapa y enlace directo a su tarjeta en el Tubo de Trabajo. |
| `/actividades/evidencias/` | `lista_evidencias` | Bandeja y auditoría técnica de evidencias fotográficas vinculadas a gestiones. |
| `/actividades/evidencia/<id>/` | `detalle_evidencia` | Panel de aprobación/rechazo de evidencia con checklist técnico. |

#### Códigos Correlativos Autoincrementales en Gestiones:
- **`GES-XXXXX`**: Para gestiones generales, atenciones vecinales y operativos territoriales.
- **`SOC-XXXXX`**: Para gestiones especializadas del Gestor Social.
- **`EVI-YYYYMMDD-XXXX`**: Código único de evidencia fotográfica asociado para auditoría.

#### Ficha Especializada Gestor Social (Flujo Multi-Etapa):
Cuando una gestión es de tipo social, el formulario unificado activa la ficha detallada del Gestor Social con 3 etapas correlativas:
1. **Etapa 1 (Atención Inicial):** Atención presencial/diagnóstico, verificación de vulnerabilidad y coordinación de visita en terreno con fecha programada.
2. **Etapa 2 (Visita e Informe):** Visita domiciliaria realizada, fecha de visita y emisión de informe social/ficha FIBE con fecha de entrega.
3. **Etapa 3 (Beneficio y Cierre):** Resolución social, asignación de subsidio/ayuda en materiales y fecha formal de entrega de beneficio.

---

### 4.2 Módulo Tubo de Trabajo — Agenda Colectiva (`/agenda/`)
Es el **método de seguimiento intersectorial** del SGR.

| URL | Vista | Descripción |
|---|---|---|
| `/agenda/resumen/` | `resumen_agenda` | **Tablero Kanban del Tubo**: Cuatro columnas operativas (*Ingresados*, *Pendientes*, *En Proceso*, *Realizados*) que muestran exclusivamente las gestiones derivadas al método. |
| `/agenda/` | `lista_compromisos` | Vista en formato tabla de los compromisos activos en el tubo. |
| `/agenda/nuevo/` | `formulario_compromiso` | Entrada directa de compromisos comunitarios al tubo (genera código `TUB-XXXXX`). |
| `/agenda/compromiso/<id>/` | `detalle_compromiso` | Ficha de seguimiento intersectorial con área de apoyo y acuerdos vecinales. |
| `/agenda/cambiar-estado/<id>/<estado>/` | `cambiar_estado_compromiso` | Endpoint para mover de etapa en el Tablero Kanban (`PENDIENTE`, `EN PROCESO`, `REALIZADO`). |

#### Integración Bidireccional Gestión $\leftrightarrow$ Tubo:
- Si en el formulario de gestión se activa *"¿Mandar al método de Tubo de Trabajo?"*, el sistema crea automáticamente el compromiso con código **`TUB-XXXXX`**.
- La tarjeta en el Kanban muestra el código de la gestión de origen (`[GES-XXXXX]` o `[SOC-XXXXX]`), el solicitante, el territorio y el área de apoyo requerida.
- Al pasar a estado **`REALIZADO`** en el Tubo, se actualiza automáticamente el estado de la gestión en el Módulo Central de Gestiones.

---

### 4.3 Catálogos Institucionales y Mantenedores CRUD (`/mantenedores/`)
Los 6 mantenedores exigidos para la administración global y parametrización:

| CRUD | URL | Entidad | Características Clave |
|---|---|---|---|
| **1. Delegaciones** | `/mantenedores/delegaciones/` | `Delegacion` | Código `DEL-XX` automático, estado Activa/Inactiva, comuna, exportación Excel. |
| **2. Roles** | `/mantenedores/roles/` | `Rol` | Código `ROL-XX` automático, alcance COMUNAL / DELEGACION, permisos. |
| **3. Usuarios** | `/mantenedores/usuarios/` | `User` + `PerfilUsuario` | Vinculación de cuenta, asignación de rol, delegación activa y delegaciones autorizadas. |
| **4. Ítems y Metas** | `/mantenedores/items/` | `ItemMeta` | Código `ITM-XX` automático, clasificación cualitativa/cuantitativa y metas SGR. |
| **5. Tipo de Atención** | `/mantenedores/tipos-atencion/` | `TipoAtencion` | Código `TIP-XX` automático, clasificador macro de atenciones. |
| **6. Sub Atención** | `/mantenedores/subatenciones/` | `SubAtencion` | Código `SUB-XX` automático, dependiente en cascada vía AJAX de Tipo de Atención. |

- Todos los mantenedores cuentan con: búsqueda insensible a mayúsculas/acentos, paginación a 10 registros, modal de confirmación SweetAlert2 y descarga de reportes en Excel (`.xlsx`).

---

### 4.4 Organización (`/organizacion/`)
Gestiona la estructura orgánica de las delegaciones y la dotación funcionaria.

| URL | Vista | Descripción |
|---|---|---|
| `/organizacion/` | `lista_unidades` | Directorio de delegaciones territoriales con tarjetas institucionales. |
| `/organizacion/unidad/<id>/` | `detalle_unidad` | Ficha descriptiva y límites territoriales de la delegación. |
| `/organizacion/personas/` | `lista_personas` | Nómina general de funcionarios clasificados por cargo y sector. |
| `/organizacion/persona/<id>/` | `detalle_persona` | Perfil del funcionario con enlace directo a su Ficha Individual SGR. |

---

### 4.5 Resultados y Medición del Desempeño (`/resultados/`)
Monitoreo gerencial y semáforos de cumplimiento por metas ponderadas.

| URL | Vista | Descripción |
|---|---|---|
| `/resultados/` | `lista_metas` | Semáforo comunal de avance agrupado por delegaciones y áreas. |
| `/resultados/persona/<id>/` | `resultado_persona` | **Ficha Individual SGR**: Ponderadores por cargo, avance actual, % cumplimiento, tope máximo del 150%, bonificaciones por felicitaciones y descuentos por reclamos. |
| `/resultados/tablero/<id>/` | `tablero_unidad` | **Tablero de Delegación**: Dotación total, personal disponible, licencias, promedio grupal y semáforo general del sector. |
| `/resultados/informe/` | `informe_resumen` | **Informe Ejecutivo**: Reporte institucional formal imprimible diseñado para Alcaldía y Administrador Municipal. |

---

## 5. Reglas de Negocio del SGR

### 5.1 Fórmulas de Cumplimiento
```
Avance actual = Cantidad de actividades/gestiones con evidencia validada en el período
% Cumplimiento = (Avance actual / Meta del período) × 100
Cumplimiento Ponderado = Ponderador del ítem × % Cumplimiento
Meta Esperada al Día = (Días transcurridos / Días totales del período) × 100
```

### 5.2 Parámetros Institucionales
- **Tope Máximo de Cumplimiento:** 150% (evita sobre-estimaciones desmedidas).
- **Umbral Mínimo Colectivo:** 80%.
- **Suma de Ponderadores por Cargo:** Debe totalizar exactamente 100%.
- **Bonificación por Felicitaciones:** +10% por felicitación formal (máximo 3).
- **Penalización por Reclamos Vecinales:** -20% a -30% sobre el cumplimiento ponderado.

### 5.3 Lógica del Semáforo
- 🟢 **Verde (Óptimo):** Avance actual $\ge$ Meta esperada al día.
- 🟡 **Ámbar (Alerta):** Avance actual $\ge 60\%$ de la meta esperada y $<$ meta esperada al día.
- 🔴 **Rojo (Crítico):** Avance actual $< 60\%$ de la meta esperada al día.

---

## 6. Roles de Usuario y Accesos en la Plataforma

| Rol | Código | Ámbito | Capacidades en el Sistema |
|---|---|---|---|
| **Administrador General** | `ROL-ADM` | Comunal | Acceso total a los 6 Mantenedores CRUD, administración de usuarios, cambio libre de delegación activa, panel Django Admin y reportes. |
| **Coordinador Municipal** | `ROL-COORD` | Comunal | Supervisión comunal de todas las delegaciones, acceso a catálogo de delegaciones e ítems, visualización del libro general de gestiones, monitoreo del Tubo de Trabajo y generación de informes ejecutivos. |
| **Delegado Municipal** | `ROL-DEL` | Delegación asignada | Jefatura territorial: supervisión del libro de gestiones de su delegación, control del Tubo de Trabajo del sector y seguimiento del Tablero de Metas de su delegación. |
| **Operador Territorial / Funcionario** | `ROL-OPE` | Delegación asignada | Registro de atenciones vecinales y gestiones en terreno con formulario unificado, carga de evidencias fotográficas y seguimiento de compromisos. |

---

## 7. Despliegue en Servidor de Producción AWS EC2

| Componente | Configuración Implementada |
|---|---|
| **Instancia Cloud** | AWS EC2 Ubuntu 24.04 LTS (`3.229.11.31`) |
| **Gestor de Procesos** | `systemd` gestionando servicio `sgr-django.service` en puerto 8000 |
| **Servidor Web / Proxy** | Apache2 en puerto 80 redirigiendo tráfico inverso hacia Django |
| **Base de Datos** | MySQL 8.0 local en servidor (`sgr_municipalidad`), usuario `sgr_user` |
| **Memoria de Intercambio** | 2 GB de memoria SWAP activa para asegurar estabilidad y evitar OOM |
| **Archivos Estáticos** | Recopilados en `staticfiles/` mediante `python manage.py collectstatic` |
| **Seguridad de Variables** | Archivo `.env` en servidor protegido por permisos y excluido de Git |
| **Suite de Pruebas** | Ejecución de `test_suite.py` con 100% de aserciones válidas |
