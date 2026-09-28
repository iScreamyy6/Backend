# 📋 Contexto Base del Proyecto — SGR (Sistema de Gestión de Resultados)

> **Propósito de este documento:** Servir como instrucciones base para que cualquier integrante del equipo (o su IA) pueda entender el contexto del proyecto y programar de forma coherente.

---

## 1. Información del Proyecto

| Campo | Valor |
|---|---|
| **Nombre** | Sistema de Gestión de Resultados (SGR) |
| **Institución** | INACAP |
| **Cliente (caso académico)** | Delegaciones municipales — Ilustre Municipalidad de La Serena |
| **Integrantes** | Alvaro Obregon, Benjamin Antipa |
| **Framework** | Django (Python) |
| **Base de datos** | SQLite3 (desarrollo) |
| **Proyecto Django** | `Municipalidad` |

---

## 2. Problema que Resuelve

Las delegaciones municipales de La Serena operan con criterios y registros independientes (planillas Excel), lo que dificulta:

- Una **visión transversal** de la gestión.
- Un **registro consolidado** de solicitudes, actividades, compromisos y servicios.
- La **formalización de metas y ponderaciones** en una herramienta única.
- Que la jefatura tenga **indicadores oportunos** para controlar compromisos.
- Que la **evidencia de ejecución** quede asociada y validada por cada actividad.

### Objetivo General
Centralizar el registro, seguimiento, verificación y medición de la gestión de funcionarios y delegaciones, generando indicadores individuales y colectivos.

---

## 3. Arquitectura Actual del Proyecto

### 3.1 Estructura de Directorios

```
Backend/
├── Municipalidad/          # Proyecto Django principal
│   ├── settings.py
│   ├── urls.py             # URLs raíz
│   └── views.py            # Vista de inicio
├── organizacion/           # App: Delegaciones y Funcionarios
│   ├── views.py            # CRUD lectura de unidades y personas
│   └── urls.py
├── actividades/            # App: Registro de gestiones
│   ├── views.py            # CRUD lectura de actividades y evidencias
│   └── urls.py
├── agenda/                 # App: Tubo de trabajo (compromisos)
│   ├── views.py            # CRUD lectura de compromisos
│   └── urls.py
├── resultados/             # App: Semáforo y metas
│   ├── views.py            # CRUD lectura de metas
│   └── urls.py
├── datos/                  # JSONs de datos ficticios
│   ├── organizacion.json
│   ├── personas.json
│   ├── actividades.json
│   ├── compromisos.json
│   └── metas.json
├── templates/              # Templates HTML (Django Template Language)
│   ├── base.html           # Layout principal con header/nav/footer
│   ├── inicio.html         # Página de inicio
│   ├── organizacion/       # Templates del módulo organización
│   ├── actividades/        # Templates del módulo actividades
│   ├── agenda/             # Templates del módulo agenda
│   └── resultados/         # Templates del módulo resultados
├── static/
│   ├── css/estilos.css     # Hoja de estilos principal
│   └── img/                # Logo de la municipalidad
├── db.sqlite3              # Base de datos SQLite
└── requirements.txt        # Dependencias (Django)
```

### 3.2 División de Trabajo (Eva 1)

| Integrante | Aplicaciones desarrolladas |
|---|---|
| **Alvaro Obregon** | `organizacion`, `resultados` |
| **Benjamin Antipa** | `agenda`, `actividades` |

### 3.3 Estado Actual (Avance Eva 2)

- ✅ **Completado**: Modelos de base de datos (`models.py`) creados y migrados con SQLite para las 4 aplicaciones (`organizacion`, `actividades`, `agenda`, `resultados`).
- ✅ **Completado**: Todos los mockups y templates de la evaluación construidos y funcionales (19 rutas HTTP 200).
- ✅ **Completado**: Formularios de registro para actividades con código verificador y nuevo compromiso en tubo.
- ✅ **Completado**: Bandeja y panel de auditoría/verificación técnica de evidencias fotográficas.
- ✅ **Completado**: Tablero Kanban del Tubo de Trabajo (`/agenda/resumen/`).
- ✅ **Completado**: Ficha Individual Oficial SGR con cálculo de ponderaciones, topes (150%) y bonificaciones (`/resultados/persona/<id>/`).
- ✅ **Completado**: Tablero de Delegación con dotación y semáforos (`/resultados/tablero/<id>/`).
- ✅ **Completado**: Informe Resumen Ejecutivo formal para Alcaldía y Jefaturas (`/resultados/informe/`).

---

## 4. Módulos del Sistema (4 Apps y Pantallas/Mockups)

### 4.1 Organización (`/organizacion/`)
Gestiona delegaciones/unidades organizacionales y funcionarios.

| URL | Vista | Descripción |
|---|---|---|
| `/organizacion/` | `lista_unidades` | Listado de delegaciones con tarjetas |
| `/organizacion/unidad/<id>/` | `detalle_unidad` | Ficha detallada de una delegación |
| `/organizacion/personas/` | `lista_personas` | Nómina de funcionarios con cargos y estados |
| `/organizacion/persona/<id>/` | `detalle_persona` | Perfil del funcionario con enlace directo a su ficha SGR |

**Modelos:** `Delegacion`, `Funcionario`

### 4.2 Actividades (`/actividades/`)
Registro de gestiones/solicitudes territoriales y auditoría de evidencias fotográficas.

| URL | Vista | Descripción |
|---|---|---|
| `/actividades/` | `lista_actividades` | Tabla general de gestiones territoriales y botones de acción |
| `/actividades/nueva/` | `formulario_actividad` | Formulario de registro con asignación automática de código verificador |
| `/actividades/actividad/<id>/` | `detalle_actividad` | Detalle exhaustivo de la gestión en terreno |
| `/actividades/evidencias/` | `lista_evidencias` | Bandeja de evidencias fotográficas con contadores y estados |
| `/actividades/evidencia/<id>/` | `detalle_evidencia` | Panel de verificación y checklist de conformidad técnica |

**Modelos:** `Actividad`, `Evidencia`

### 4.3 Agenda (`/agenda/`)
Tubo de trabajo colectivo y compromisos intersectoriales de la delegación.

| URL | Vista | Descripción |
|---|---|---|
| `/agenda/` | `lista_compromisos` | Tabla general del tubo de trabajo |
| `/agenda/nuevo/` | `formulario_compromiso` | Formulario de ingreso de compromisos al tubo de gestión |
| `/agenda/compromiso/<id>/` | `detalle_compromiso` | Ficha técnica y seguimiento del compromiso |
| `/agenda/resumen/` | `resumen_agenda` | Tablero Kanban / Pipeline operativo del Tubo por estados |

**Modelos:** `Compromiso`

### 4.4 Resultados (`/resultados/`)
Semáforo de cumplimiento, metas ponderadas, tablero de mando e informe ejecutivo.

| URL | Vista | Descripción |
|---|---|---|
| `/resultados/` | `lista_metas` | Semáforo general de cumplimiento por áreas |
| `/resultados/meta/<id>/` | `detalle_meta` | Detalle específico de meta y semáforo |
| `/resultados/persona/<id>/` | `resultado_persona` | **Ficha Individual SGR**: Ponderadores, % cumplimiento, méritos y gestiones |
| `/resultados/tablero/<id>/` | `tablero_unidad` | **Tablero de Delegación**: Dotación, licencias, promedio y semáforo grupal |
| `/resultados/informe/` | `informe_resumen` | **Informe Ejecutivo**: Reporte institucional formal para Alcaldía (imprimible) |

**Modelos:** `PeriodoEvaluacion`, `MetaFuncionario`, `IndicadorDelegacion`
**Datos clave de una Meta:**
- `id`, `area`, `responsable`, `avance`, `estado_semaforo`

**Semáforo:** `verde` (≥ meta esperada), `amarillo` (≥ 60% de meta), `rojo` (< 60% de meta)


---

## 5. Diseño Visual y Estilos

### 5.1 Paleta de Colores
```css
--petroleo: #b80003;           /* Rojo municipalidad (color principal) */
--cobre-claro: #ef7772;        /* Acento claro */
--marfil: #f7f1ed;             /* Fondo general */
--papel: #fffdfa;              /* Fondo tarjetas/tablas */
--tinta: #302326;              /* Texto principal */
--muted: #786a6b;              /* Texto secundario */
--linea: #e4d9d5;              /* Bordes */
--verde: #2c7765;              /* Estado óptimo */
--rojo: #b44f4b;               /* Estado crítico */
```

### 5.2 Tipografías
- **Títulos:** `'Libre Baskerville', Georgia, serif`
- **Cuerpo:** `'DM Sans', 'Segoe UI', sans-serif`

### 5.3 Componentes CSS Disponibles
| Clase | Uso |
|---|---|
| `.contenedor` | Wrapper centrado `max-width: 1160px` |
| `.grilla` | Grid de 4 columnas para tarjetas |
| `.tarjeta` | Card con borde superior, hover elevable |
| `.tarjeta-destacada` | Card invertida (fondo oscuro) |
| `.tabla-operativa` | Tabla con borde rojo superior |
| `.tabla-semaforo` | Tabla para resultados/metas |
| `.detalle-tarjeta` | Card de detalle con borde izquierdo |
| `.estado`, `.estado-optimo`, `.estado-alerta`, `.estado-critico`, `.estado-neutral` | Badges de estado (pills redondeados) |
| `.etiqueta` | Label uppercase pequeño |
| `.titulo` | Header de sección con contador |
| `.hero` | Sección hero de la página de inicio |
| `.boton-volver` | Link de regreso |

### 5.4 Template Base (`base.html`)
```html
<!-- Estructura -->
<header>  → Logo + Navegación (Organización | Actividades | Agenda | Resultados)
<main>    → {% block contenido %}
<footer>  → © 2026 Ilustre Municipalidad de La Serena
```

---

## 6. Actores del Sistema (según la guía SGR)

| Actor | Rol |
|---|---|
| **Administrador** | Configura delegaciones, usuarios, cargos, catálogos, períodos, metas, ponderaciones y permisos |
| **Coordinador del sistema** | Supervisa operación transversal, revisa indicadores, resuelve criterios |
| **Delegado / Jefatura** | Consulta gestión de su delegación, asigna o revisa compromisos |
| **Funcionario** | Registra actividades, compromisos, avances, contactos, servicios y evidencias |
| **Verificador** | Revisa evidencias, valida o rechaza registros |
| **Usuario de consulta** | Accede a tableros e informes según ámbito autorizado |

---

## 7. Cargos y Roles de Funcionarios (del sistema real)

Cada delegación tiene los siguientes cargos:

| Cargo | Abreviatura | Ítems de evaluación |
|---|---|---|
| **Delegado** | — | Supervisión general |
| **Apoyo Administrativo** | A ADM | Atención usuario tel/presencial, Llamadas preventivas, Informe inventarios, Informe comunicaciones, Emergencia |
| **Territorial OO.CC.** | T OO CC / COM | Atención usuario tel/presencial, Visitas/reuniones con organizaciones, Conformación directivas definitiva, Gestión talleres y actividades, Emergencia |
| **Coordinador DISERCO** | COSERCO | Informes, Operativos, Talleres, Terreno, Atención requerimiento usuario, Emergencia |
| **Gestor Social** | SOC | Atención social a usuario presencial, Visita terreno, Entrega informe, Entrega beneficio, Emergencia |
| **Planificación y Control** | P y C / PLA | Reunión semanal con el equipo, Solución de problemas a usuarios particulares, Soluciones de ingresos al tubo, Pendientes en tubo menor a 10%, Emergencia |
| **Gestor Seguridad** | G SEGUR | Formación comités seguridad, Levantamiento incivilidades, Gestión mediación, Recuperación espacios públicos, Infracciones varias, Salidas a terreno |

---

## 8. Reglas de Negocio Clave

### 8.1 Cálculos
```
Avance actual = cantidad de actividades válidas por ítem en el período
% Cumplimiento = (avance actual / meta del período) × 100
Cumplimiento ponderado = ponderador × % cumplimiento
Meta esperada al día = (días transcurridos / días totales) × 100
```

### 8.2 Semáforo
| Color | Condición |
|---|---|
| 🟢 Verde | Avance ≥ meta esperada al día |
| 🟡 Ámbar | Avance ≥ 60% de meta esperada Y < meta esperada |
| 🔴 Rojo | Avance < 60% de meta esperada |

### 8.3 Parámetros
- **Tope máximo de cumplimiento:** 150%
- **Umbral mínimo colectivo:** 80%
- **Suma de ponderadores por cargo:** 100%
- **Felicitaciones:** +10% (máx 3)
- **Reclamos:** -20% a -30% (penalización)

### 8.4 Estados de Compromisos (Agenda/Tubo)
`Ingresado` → `Pendiente` → `En proceso` → `Realizado`

### 8.5 Flujo de Evidencias
1. Funcionario registra actividad → Sistema genera código único
2. Funcionario adjunta evidencia (foto/archivo) con el código
3. Verificador revisa → Aprueba / Rechaza / Solicita corrección
4. Solo evidencia aprobada aporta al avance/meta

---

## 9. Estructura de la Hoja Excel Original

El sistema real opera con una planilla Excel que contiene:

### Vista Resumen de Delegación
- Tabla de áreas, responsables, avance, semáforo (verde/amarillo/rojo)
- Período: fecha inicio, fecha cierre, días totales, días al cierre
- Nómina de funcionarios por cargo

### Vista por Funcionario (Hoja individual)
- **Cabecera:** Nombre, cargo, tipo de cumplimiento mínimo (80%)
- **Tabla de ponderaciones:** Ítems, ponderador, meta trimestral, avance actual, % cumplimiento, cumplimiento ponderado
- **Tabla de gestiones:** Nº, Fecha, Actividad/Solicitud/Problema, Contacto, Teléfono, Ingreso a tubo, Ítem, Código foto, Imagen verif, Verificador válido, Resultado

### Vista Tubo de Trabajo (Agenda Colectiva)
- Nº, Fecha solicitud, Actividad/Solicitud/Problema, Int/Ext, Solicitante, Territorio, Responsable, Fecha de compromiso, Meses, Área/Persona apoyo, Avance/Observaciones, Estatus, Unidad

### Vista Semáforo
- Área, Responsable, Licencias, Vacaciones, Emergencias, Compensatorios administrativos, Días totales, Objetivo al día de hoy, 60%, Avance, Indicador (semáforo)

---

## 10. Entregables Eva 2

La segunda evaluación requiere los siguientes artefactos:

### 10.1 Diagrama de Requerimientos
Representación gráfica de los RF y RNF organizados por épicas.

### 10.2 Diagrama de Caso de Uso General
Visión global del sistema con actores principales y funcionalidades.

### 10.3 Diagrama de Caso de Uso Específico + Cuadro Descriptivo
Detalle de cada caso de uso con include/extend y tabla de documentación.

### 10.4 Modelo Entidad-Relación (MER)
Diagrama de la base de datos con entidades, atributos y relaciones.

### 10.5 Diagrama de Clases
Clases del dominio con atributos, métodos y relaciones.

### 10.6 Mockups (Templates)
Prototipos de interfaces que representen las pantallas del sistema.

---

## 11. Convenciones de Desarrollo

### 11.1 Nombrado
- **Apps Django:** Nombres en español, minúsculas (`organizacion`, `actividades`, `agenda`, `resultados`)
- **Modelos:** CamelCase en español (`Delegacion`, `Funcionario`, `Actividad`, etc.)
- **URLs:** Rutas descriptivas en español (`/organizacion/unidad/<id>/`)
- **Templates:** snake_case (`lista_unidades.html`, `detalle_persona.html`)
- **CSS:** Clases en español con guiones (`tarjeta-cabecera`, `estado-optimo`)

### 11.2 Patrones de Código
- **Vistas:** Funciones (function-based views), no clases
- **Carga de datos:** Actualmente desde JSON (`datos/*.json`), migrar a modelos Django
- **Templates:** Herencia desde `base.html` con `{% extends %}` / `{% block contenido %}`
- **Navegación:** Links activos con `{% if '/ruta/' in request.path %}`

### 11.3 Estructura de Templates
```html
{% extends "base.html" %}
{% block titulo %}Título | SGM La Serena{% endblock %}
{% block contenido %}
  <!-- Cabecera de sección -->
  <div class="titulo">
    <div>
      <p class="etiqueta">MÓDULO NOMBRE</p>
      <h1>Título de la Vista</h1>
    </div>
    <span>N registros</span>
  </div>
  <!-- Contenido (grilla de tarjetas o tabla) -->
{% endblock %}
```

---

## 12. Archivos de Referencia

| Archivo | Descripción |
|---|---|
| `Contexto de la problematica/Guia_Proyecto_Software_SGR_Alumnos.md` | Guía completa del proyecto con requerimientos, historias de usuario, reglas de negocio y plan |
| `Contexto de la problematica/Relación entre los artefactos.md` | Explicación de cómo se relacionan los diagramas entre sí |
| `Contexto de la problematica/Galería-20260928/` | Capturas de pantalla de la planilla Excel real del sistema |
| `Contexto de la problematica/imagenes_pdf/` | Imágenes extraídas de los PDFs de referencia |

---

## 13. Mapeo Épicas → Funcionalidades → Pantallas

| Épica | Historias P1 | Módulo Django | Pantallas Principales |
|---|---|---|---|
| EP-01: Registro y gestión de actividades | HU-01, HU-02, HU-04 | `actividades` | Lista actividades, Formulario registro, Detalle actividad |
| EP-02: Medición y desempeño | HU-05, HU-06, HU-07 | `resultados` | Definición de metas, Panel de avance, Tablero delegación |
| EP-03: Evidencias y verificación | HU-09, HU-10, HU-11 | `actividades` | Carga evidencia, Validación evidencia, Código verificador |
| EP-04: Agenda colectiva | HU-12, HU-13, HU-14 | `agenda` | Lista compromisos, Formulario compromiso, Seguimiento |
| EP-05: Monitoreo y control | HU-16, HU-17, HU-18 | `resultados` | Semáforo, Comparación avance, Resumen ejecutivo |
| EP-06: Reportabilidad | HU-20 | Transversal | Informes, Exportación |
| EP-07: Plataforma colaborativa | HU-23, HU-25 | Transversal | Trabajo simultáneo, Configuración |
| EP-08: Administración y seguridad | HU-26 a HU-30 | `organizacion` + nuevo | Admin delegaciones, roles, catálogos, períodos, auditoría |

---

> **⚠️ Nota para IAs:** Este documento es la fuente de verdad del contexto del proyecto. Antes de programar, leer las secciones relevantes. Respetar las convenciones de nombrado, la paleta de colores, la estructura de templates y los patrones de código existentes.
