# 📁 Carpeta de Contexto, Requisitos y Documentación — SGR

Bienvenido a la carpeta documental del **Sistema de Gestión de Resultados (SGR)** de la Municipalidad de La Serena. Este espacio recopila y organiza cronológicamente toda la documentación de respaldo, especificaciones docentes, modelos de datos, evidencias de prueba e informes de entrega del proyecto.

---

## 🗺️ Estructura y Cronología de la Documentación

```
Contexto de la problematica/
│
├── 📄 contexto.md                       # DOCUMENTO MAESTRO: Visión global, arquitectura, correcciones y estado actual
├── 📄 README.md                         # Índice y guía de navegación de esta carpeta
│
├── 📂 01_Bases_y_Requisitos_Docente/    # Especificaciones y pautas oficiales entregadas por el docente
│   ├── Guia_Proyecto_Software_SGR_Alumnos.md / .pdf      (Guía marco general del proyecto)
│   ├── Relación entre los artefactos.md / .pdf          (Relaciones e interoperabilidad entre módulos)
│   ├── Eva Sumativa 2 (1).md / .pdf                     (Rúbrica y pauta formal de la Evaluación #2)
│   ├── Requisitos_y_Plan_Pruebas_Segunda_Evaluacion_SGR (Requisitos funcionales y especificación base de pruebas)
│   └── imagenes_pdf/                                    (Imágenes y diagramas extraídos de los documentos oficiales)
│
├── 📂 02_Modelamiento_y_Diseno/         # Diseño conceptual, base de datos y pantallas de referencia
│   ├── Diagramas/                                       (Modelo Entidad-Relación: MER.png y modelo-sgr-MER.mwb)
│   └── Mockups_Galeria/                                 (Maquetas de interfaces municipales por rol y vistas)
│
├── 📂 03_Datos_y_Scripts_Iniciales/     # Semillas iniciales y script DDL de creación de tablas
│   ├── script_mysql_sgr.sql                             (Script SQL DDL/DML base para MySQL)
│   ├── actividades.json                                 (Datos JSON de actividades iniciales)
│   ├── compromisos.json                                 (Datos JSON de compromisos del Tubo iniciales)
│   ├── metas.json                                       (Datos JSON de metas y ponderaciones)
│   ├── organizacion.json                                (Datos JSON de delegaciones y unidades)
│   └── personas.json                                    (Datos JSON de funcionarios y vecinos)
│
├── 📂 04_Planes_de_Pruebas_SGR/         # Planes de prueba actualizados con Módulo Unificado y Tubo
│   ├── Plan_Pruebas_Ejecucion_SGR.md                    (Matriz formal de pruebas funcionales, integración y estrés)
│   ├── Plan_Pruebas_Manual_SGR.md                       (Guía de prueba manual en navegador con checklist de entrega)
│   └── Plan_Pruebas_Manual_SGR.pdf                      (Versión imprimible/PDF del plan manual)
│
└── 📂 05_Entregables_e_Informe_Eva2/    # Informes consolidados de la Evaluación 2 y Guía de Defensa
    ├── INFORME_EVA2_SGR.md / .pdf                       (Informe formal de entrega para el docente)
    ├── GUIA_DEFENSA_EVA2.md                             (Guía estratégica de defensa oral y argumentación técnica)
    └── cuadros_casos_de_uso_sgr.pdf                     (Diagramas y cuadros detallados de casos de uso)
```

---

## 📌 Guía Rápida: ¿Dónde encuentro cada cosa?

1. **¿Cómo entender rápidamente todo el sistema y las últimas modificaciones?**
   👉 Revisa [contexto.md](file:///d:/Django/Backend/Contexto%20de%20la%20problematica/contexto.md). Contiene la arquitectura unificada, explicación de la fusión de módulos, códigos autoincrementales y stack de producción en AWS EC2.

2. **¿Cómo preparar la defensa ante las preguntas del profesor?**
   👉 Revisa [GUIA_DEFENSA_EVA2.md](file:///d:/Django/Backend/Contexto%20de%20la%20problematica/05_Entregables_e_Informe_Eva2/GUIA_DEFENSA_EVA2.md). Incluye el guion de presentación paso a paso y la respuesta exacta a las observaciones de corrección (Paso 7).

3. **¿Cómo ejecutar las pruebas en el navegador o revisar la matriz de validación?**
   👉 Consulta la carpeta [04_Planes_de_Pruebas_SGR/](file:///d:/Django/Backend/Contexto%20de%20la%20problematica/04_Planes_de_Pruebas_SGR/). Incluye los casos de prueba `GES-01` a `GES-06` (Módulo Unificado) y `TUB-01` a `TUB-03` (Tubo de Trabajo Kanban).

4. **¿Dónde están los requerimientos originales del profesor?**
   👉 En la carpeta [01_Bases_y_Requisitos_Docente/](file:///d:/Django/Backend/Contexto%20de%20la%20problematica/01_Bases_y_Requisitos_Docente/).
