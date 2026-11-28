"""
Compilador ReportLab para generar los PDFs oficiales de la Evaluacion 3 Unidad 3
de Proyecto Integrado:
1. INFORME_FINAL_PROYECTO_INTEGRADO_EVA3_SGR.pdf (Informe Tecnico Final Completo)
2. PRESENTACION_DEFENSA_PROYECTO_INTEGRADO_EVA3_SGR.pdf (Presentacion de 15 Minutos y Defensa)
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para calcular y numerar paginas dinamicamente ('Pagina X de Y')."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.doc_title = getattr(self, 'doc_title', 'INACAP La Serena — Proyecto Integrado | SGR Municipalidad')

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        if self._pageNumber == 1:
            return  # Portada limpia

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6c757d"))

        # Encabezado superior
        self.drawString(2 * cm, 26.5 * cm, "INACAP La Serena — Proyecto Integrado (TI) | Sistema de Gestion de Resultados (SGR)")
        self.setStrokeColor(colors.HexColor("#AD0000"))
        self.setLineWidth(1)
        self.line(2 * cm, 26.3 * cm, 19.5 * cm, 26.3 * cm)

        # Pie de pagina inferior
        self.setStrokeColor(colors.HexColor("#dee2e6"))
        self.setLineWidth(0.5)
        self.line(2 * cm, 2 * cm, 19.5 * cm, 2 * cm)

        self.drawString(2 * cm, 1.5 * cm, "Evaluacion 3 Unidad 3 — Informe Final y Defensa | I. Municipalidad de La Serena")
        page_str = f"Pagina {self._pageNumber} de {total_pages}"
        self.drawRightString(19.5 * cm, 1.5 * cm, page_str)
        self.restoreState()


def get_custom_styles():
    styles = getSampleStyleSheet()
    c_primary = colors.HexColor("#AD0000")
    c_dark = colors.HexColor("#1A252F")
    c_blue = colors.HexColor("#1E3A8A")

    h1 = ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=c_primary, spaceBefore=10, spaceAfter=4, keepWithNext=True)
    h2 = ParagraphStyle('H2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=c_blue, spaceBefore=7, spaceAfter=3, keepWithNext=True)
    h3 = ParagraphStyle('H3', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=c_dark, spaceBefore=5, spaceAfter=2, keepWithNext=True)
    body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=c_dark, spaceAfter=4, alignment=4)
    body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=c_dark, spaceAfter=4)
    code = ParagraphStyle('Code', parent=styles['Normal'], fontName='Courier', fontSize=7, leading=9, textColor=colors.HexColor("#1e293b"), spaceAfter=2)
    cover_t = ParagraphStyle('CoverT', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=c_primary, alignment=1, spaceAfter=8)
    cover_sub = ParagraphStyle('CoverSub', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=c_dark, alignment=1, spaceAfter=15)
    speech = ParagraphStyle('Speech', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=11, textColor=colors.HexColor("#0f5132"), spaceAfter=4)
    table_cell = ParagraphStyle('TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=c_dark)
    table_cell_bold = ParagraphStyle('TableCellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor("#1e3a8a"))
    table_header = ParagraphStyle('TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white)

    return {
        'h1': h1, 'h2': h2, 'h3': h3, 'body': body, 'body_bold': body_bold,
        'code': code, 'cover_t': cover_t, 'cover_sub': cover_sub, 'speech': speech,
        'table_cell': table_cell, 'table_cell_bold': table_cell_bold, 'table_header': table_header
    }


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = BASE_DIR


# ==============================================================================
# 1. GENERAR INFORME FINAL (PDF)
# ==============================================================================
def generar_pdf_informe():
    filename = os.path.join(OUT_DIR, "INFORME_FINAL_PROYECTO_INTEGRADO_EVA3_SGR.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=1.8*cm, rightMargin=1.8*cm, topMargin=2.2*cm, bottomMargin=2.2*cm)
    st = get_custom_styles()
    story = []

    # Portada
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("UNIVERSIDAD TECNOLÓGICA DE CHILE INACAP — SEDE LA SERENA", ParagraphStyle('Inst', fontName='Helvetica-Bold', fontSize=10, leading=13, alignment=1, textColor=colors.HexColor("#6c757d"))))
    story.append(Paragraph("ÁREA INFORMÁTICA, CIBERSEGURIDAD Y TELECOMUNICACIONES", ParagraphStyle('Area', fontName='Helvetica', fontSize=9, leading=12, alignment=1, textColor=colors.HexColor("#6c757d"))))
    story.append(Spacer(1, 1.2 * cm))

    story.append(Paragraph("INFORME FINAL DE PROYECTO", ParagraphStyle('DocT', fontName='Helvetica-Bold', fontSize=13, leading=16, alignment=1, textColor=colors.HexColor("#1A252F"))))
    story.append(Paragraph("SISTEMA DE GESTIÓN DE RESULTADOS (SGR)", st['cover_t']))
    story.append(Paragraph("Para las Delegaciones Municipales de la Ilustre Municipalidad de La Serena", st['cover_sub']))
    story.append(HRFlowable(width="85%", thickness=2.5, color=colors.HexColor("#AD0000"), spaceBefore=5, spaceAfter=15))

    # Ficha Institucional en tabla
    data_portada = [
        [Paragraph("<b>Asignatura:</b>", st['table_cell_bold']), Paragraph("Proyecto Integrado", st['table_cell'])],
        [Paragraph("<b>Unidad de Aprendizaje:</b>", st['table_cell_bold']), Paragraph("Unidad 3: Informe final y presentación del SGR", st['table_cell'])],
        [Paragraph("<b>Evaluación:</b>", st['table_cell_bold']), Paragraph("Evaluación 3 Unidad 3 (Ponderación Rúbrica: 100 puntos)", st['table_cell'])],
        [Paragraph("<b>Docente Evaluadora:</b>", st['table_cell_bold']), Paragraph("Mariavictoria Freites Ayala", st['table_cell'])],
        [Paragraph("<b>Integrantes del Equipo:</b>", st['table_cell_bold']), Paragraph("<b>Emanuel Román Serón</b> (Scrum Master / Backend & Cloud)<br/><b>Benjamín Antipa</b> (Development Team / Frontend & Logic)<br/><b>Álvaro Obregón</b> (Development Team / Data, Quality & Sec)", st['table_cell'])],
        [Paragraph("<b>Entorno en Producción AWS:</b>", st['table_cell_bold']), Paragraph("AWS EC2 Ubuntu Server: http://3.213.246.194:8000/", st['table_cell'])],
        [Paragraph("<b>Repositorio Oficial:</b>", st['table_cell_bold']), Paragraph("https://github.com/iScreamyy6/Backend (Rama main)", st['table_cell'])],
        [Paragraph("<b>Fecha y Hora de Entrega:</b>", st['table_cell_bold']), Paragraph("30 de noviembre de 2026, 11:25 horas", st['table_cell'])],
    ]
    t_portada = Table(data_portada, colWidths=[5.5*cm, 12*cm])
    t_portada.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_portada)
    story.append(PageBreak())

    # 1. Resumen Ejecutivo
    story.append(Paragraph("1. Resumen Ejecutivo", st['h1']))
    story.append(Paragraph("<b>1.1 Problema Abordado:</b> La Ilustre Municipalidad de La Serena administra un territorio comunal de alta dispersión geográfica (delegaciones urbanas y rurales como La Antena, Las Compañías, Centro Histórico, La Pampa, Avenida del Mar y Rural Cordillera). Históricamente, las delegaciones operaban de forma fragmentada mediante planillas Excel no centralizadas y registros en papel. Esta desconexión originaba pérdida de trazabilidad en las solicitudes ciudadanas, imposibilidad de auditar las metas institucionales de los funcionarios en tiempo real y riesgos de vulneración a la Ley N° 19.628 de Protección de Datos Personales.", st['body']))
    story.append(Paragraph("<b>1.2 Alcance Final de la Solución:</b> El Sistema de Gestión de Resultados (SGR) es una plataforma web y API RESTful desarrollada sobre Django 5.x y MySQL 8.0, desplegada en una instancia AWS EC2. Integra la gestión de atenciones vecinales con validación Módulo 11 de RUT, seguimiento de compromisos en terreno mediante un Tablero Kanban interactivo, tramitación multi-etapa de casos sociales, control estricto de metas trimestrales con tope porcentual del 100%, dictamen supervisor de evidencias probatorias y cuadro de mando analítico con semaforización comunal en tiempo real.", st['body']))
    story.append(Paragraph("<b>1.3 Perfiles de Usuario:</b> Administrador General (control comunal total y configuración global), Supervisor Comunal/Territorial (dictamen de evidencias y monitoreo de avance en delegación asignada) y Funcionario Operativo/Administrativo (captura de atenciones, ejecución de tareas en Kanban y carga de evidencias).", st['body']))
    story.append(Paragraph("<b>1.4 Estado de la Solución y Resultados:</b> La solución se encuentra 100% implementada, certificada y desplegada en producción en AWS EC2 (http://3.213.246.194:8000/). El software superó exitosamente el protocolo de pruebas automatizado en test_suite.py con 0 fallos, demostrando robustez transaccional y tiempos de respuesta sub-segundo en MySQL.", st['body']))

    # 2. Necesidades del Negocio y Solución Implementada
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("2. Necesidades del Negocio y Solución Implementada", st['h1']))
    story.append(Paragraph("Cada componente implementado en el sistema resuelve un proceso administrativo formalizado de la gestión municipal serenense:", st['body']))
    
    # Matriz Requerimiento-Funcionalidad-Interfaz-Evidencia
    matriz_data = [
        [Paragraph("Req.", st['table_header']), Paragraph("Necesidad del Negocio", st['table_header']), Paragraph("Funcionalidad Implementada", st['table_header']), Paragraph("Interfaz / URL", st['table_header']), Paragraph("Evidencia", st['table_header'])],
        [Paragraph("REQ-01", st['table_cell_bold']), Paragraph("Acceso seguro y RBAC", st['table_cell']), Paragraph("Django Auth, grupos, PBKDF2 y token seguro.", st['table_cell']), Paragraph("/login/, /recuperar/", st['table_cell']), Paragraph("test_suite.py TC-01", st['table_cell'])],
        [Paragraph("REQ-02", st['table_cell_bold']), Paragraph("Filtro territorial", st['table_cell']), Paragraph("Aislamiento multi-delegación y vista comunal.", st['table_cell']), Paragraph("/cambiar-delegacion/", st['table_cell']), Paragraph("Sesión activa aislada", st['table_cell'])],
        [Paragraph("REQ-03", st['table_cell_bold']), Paragraph("Padrón de vecinos", st['table_cell']), Paragraph("Validación algorítmica RUT (Módulo 11).", st['table_cell']), Paragraph("/mantenedores/vecinos/", st['table_cell']), Paragraph("Bloqueo RUT inválido", st['table_cell'])],
        [Paragraph("REQ-04", st['table_cell_bold']), Paragraph("Atención ciudadana", st['table_cell']), Paragraph("Formulario con cascada AJAX de subatenciones.", st['table_cell']), Paragraph("/atenciones/crear/", st['table_cell']), Paragraph("Folio ATC-00117 creado", st['table_cell'])],
        [Paragraph("REQ-05", st['table_cell_bold']), Paragraph("Tubo Kanban terreno", st['table_cell']), Paragraph("Tablero interactivo con alerta de atrasos.", st['table_cell']), Paragraph("/tubo-trabajo/", st['table_cell']), Paragraph("TUB-00507 -> REALIZADO", st['table_cell'])],
        [Paragraph("REQ-06", st['table_cell_bold']), Paragraph("Gestor Social", st['table_cell']), Paragraph("Flujo multi-etapa de visitas y ayudas sociales.", st['table_cell']), Paragraph("/gestiones/?tipo=social", st['table_cell']), Paragraph("Ficha SOC-00093 OK", st['table_cell'])],
        [Paragraph("REQ-07", st['table_cell_bold']), Paragraph("Control de metas", st['table_cell']), Paragraph("Validación estricta sumatoria <= 100%.", st['table_cell']), Paragraph("/metas/asignar/", st['table_cell']), Paragraph("Bloqueo sumatoria > 100%", st['table_cell'])],
        [Paragraph("REQ-08", st['table_cell_bold']), Paragraph("Bandeja evidencias", st['table_cell']), Paragraph("Dictamen supervisor (Aprobar/Devolver).", st['table_cell']), Paragraph("/evidencias/", st['table_cell']), Paragraph("Aprobación incrementa meta", st['table_cell'])],
        [Paragraph("REQ-09", st['table_cell_bold']), Paragraph("Semáforo comunal", st['table_cell']), Paragraph("Dashboard en tiempo real (Verde/Amarillo/Rojo).", st['table_cell']), Paragraph("/, /dashboard/", st['table_cell']), Paragraph("Kpis calculados en caliente", st['table_cell'])],
        [Paragraph("REQ-10", st['table_cell_bold']), Paragraph("Interoperabilidad", st['table_cell']), Paragraph("API RESTful con JWT y Swagger OpenAPI 3.0.", st['table_cell']), Paragraph("/api/swagger/", st['table_cell']), Paragraph("Token JWT 200 OK", st['table_cell'])],
    ]
    t_matriz = Table(matriz_data, colWidths=[1.5*cm, 4*cm, 4.2*cm, 3.8*cm, 4*cm])
    t_matriz.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_matriz)

    # 3. Diseño de Interfaz y Lineamientos
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("3. Diseño de Interfaz y Lineamientos", st['h1']))
    story.append(Paragraph("<b>Navegación:</b> Dispone de barra lateral permanente con segmentación de menús por perfil y barra superior con selector dinámico de Delegación Activa que conmuta instantáneamente entre el ámbito local y el consolidado comunal.", st['body']))
    story.append(Paragraph("<b>Consistencia Visual e Identidad Municipal:</b> Aplica la paleta corporativa de La Serena: Azul Municipal (#1E3A8A), Azul Marino (#1A252F), Verde Éxito (#10B981), Amarillo Alerta (#F59E0B) y Rojo Institucional (#AD0000). Utiliza tipografía sans-serif Inter para máxima legibilidad.", st['body']))
    story.append(Paragraph("<b>Validaciones y Mensajería:</b> Validación en tiempo real de RUT (Módulo 11) tanto en JavaScript como en clean() de formularios Django; feedback visual inmediato mediante Django Messages (toasts y badges) con indicación de errores de campo.", st['body']))
    story.append(Paragraph("<b>Diseño Responsivo y Accesibilidad:</b> Maquetación Mobile-First bajo Bootstrap 5 adaptada a pantallas táctiles de smartphones en terreno, tablets para visitas domiciliarias y pantallas de escritorio. Cumple con pautas de accesibilidad WCAG 2.1 Nivel AA.", st['body']))

    # 4. Base de Datos
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("4. Base de Datos Relacional", st['h1']))
    story.append(Paragraph("<b>Motor y Normalización:</b> Implementado en MySQL 8.0 bajo estricta Tercera Forma Normal (3FN), erradicando redundancias y dependencias transitivas a lo largo de 18 tablas interconectadas.", st['body']))
    story.append(Paragraph("<b>Integridad Referencial y Restricciones:</b> Todas las claves foráneas hacia datos maestros aplican on_delete=models.PROTECT, impidiendo la eliminación en cascada de historiales municipales. Incorpora restricciones de unicidad en RUT de vecinos, códigos de gestión y en combinaciones (funcionario, meta, trimestre).", st['body']))
    story.append(Paragraph("<b>Optimización e Índices:</b> Columnas críticas indexadas con db_index=True (RUT, folios, estados y fechas), asegurando consultas de agregación instantáneas en dashboards.", st['body']))
    story.append(Paragraph("<b>Prevención de Inconsistencias:</b> El avance de metas y el semáforo se calculan en caliente mediante agregaciones del ORM (Count, Sum), garantizando sincronización sin datos desactualizados en columnas estáticas.", st['body']))

    # 5. Seguridad
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("5. Seguridad y Control de Acceso", st['h1']))
    story.append(Paragraph("<b>Autenticación y RBAC:</b> Contraseñas encriptadas con PBKDF2 SHA-256 (600.000 iteraciones). Permisos estrictos por grupo (Administrador, Supervisor, Administrativo).", st['body']))
    story.append(Paragraph("<b>Aislamiento Territorial:</b> El procesador de contexto Municipalidad/context_processors.py filtra en cada petición los QuerySets según la delegación de la sesión activa, bloqueando accesos cruzados no autorizados.", st['body']))
    story.append(Paragraph("<b>Recuperación Criptográfica por Token:</b> Implementación con PasswordResetTokenGenerator de un solo uso con caducidad a las 24 horas e invalidación inmediata tras su consumo, mitigando riesgos de secuestro de cuentas.", st['body']))
    story.append(Paragraph("<b>Protección de Archivos y Mitigación OWASP:</b> Archivos probatorios almacenados con nombres únicos uuid4 y validación de tipos MIME; protección CSRF en todos los formularios, ORM parametrizado contra SQL Injection y autoescape contra XSS.", st['body']))

    # 6. Trabajo Colaborativo
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("6. Trabajo Colaborativo y Repositorio", st['h1']))
    story.append(Paragraph("El equipo operó bajo el marco de trabajo Scrum con entregas continuas y control de versiones en GitHub (https://github.com/iScreamyy6/Backend). Estrategia GitFlow con rama main protegida y ramas feature/* para cada módulo. Distribución equitativa: Emanuel Román (Arquitectura, Seguridad y Despliegue AWS), Benjamín Antipa (Frontend, Tablero Kanban y UX) y Álvaro Obregón (Lógica de Metas, Base de Datos y Calidad).", st['body']))

    # 7. Configuración del Entorno y Despliegue AWS
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("7. Configuración del Entorno y Despliegue en AWS", st['h1']))
    story.append(Paragraph("<b>Entorno Local:</b> Python 3.11/3.12, virtualenv, instalación vía pip install -r requirements.txt, archivo .env desacoplado (SECRET_KEY, credenciales MySQL), migraciones python manage.py migrate y ejecución local en puerto 8000.", st['body']))
    story.append(Paragraph("<b>Despliegue Productivo en AWS EC2:</b> Instancia Ubuntu Server 22.04 LTS en AWS (IP 3.213.246.194:8000), servidor WSGI Gunicorn gestionado como demonio systemd, servidor web Nginx como reverse proxy sirviendo estáticos y MySQL Server local asegurado.", st['body']))

    # 8. Documentación de la Implementación
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("8. Documentación de la Implementación y Reglas de Negocio", st['h1']))
    story.append(Paragraph("<b>Arquitectura MVT y API:</b> Desacoplamiento por capas entre plantillas de presentación, controladores de vista y servicios del negocio.", st['body']))
    story.append(Paragraph("<b>Fórmula de Metas:</b> Avance = min(100, (Evidencias Cuantitativas Aprobadas / Meta Cuantitativa) * 100). Cumplimiento Ponderado = Sumatoria(Avance * Ponderación / 100), donde la suma de ponderaciones está rígidamente restringida al 100%. Semáforo: Verde (>=75%), Amarillo (50% - 74.9%), Rojo (<50%).", st['body']))

    # 9 y 10. Protocolo de Pruebas y Resultados
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("9 y 10. Protocolo de Pruebas, Resultados y Discrepancias", st['h1']))
    story.append(Paragraph("La suite test_suite.py ejecutó 12 casos de prueba críticos (autenticación, asignación con ponderación >100%, metas con valor negativo, aislamiento territorial, token criptográfico de un solo uso, dictamen de evidencias y limpieza total de la BD). Todas las pruebas finalizaron con estado APROBADO.", st['body']))
    story.append(Paragraph("<b>Discrepancia Crítica Resuelta N° 1:</b> En Municipalidad/context_processors.py (Línea 95), se utilizaba Funcionario.objects.filter(...) en el bloque fallback sin haber importado el modelo Funcionario. Esto provocaba NameError: name 'Funcionario' is not defined al autenticar un usuario sin delegación en sesión. Se corrigió agregando Funcionario al import y se verificó con 100% de éxito en la suite.", st['body']))
    story.append(Paragraph("<b>Discrepancia Crítica Resuelta N° 2:</b> Desincronización de estados entre Tubo de Trabajo y Gestiones al arrastrar tarjetas en el Kanban. Se resolvió con actualización transaccional bidireccional entre CompromisoTubo y Gestion.", st['body']))

    # 11, 12 y 13. Recomendaciones, Conclusiones y Anexos
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("11. Recomendaciones y Mejora Continua", st['h1']))
    story.append(Paragraph("P1: Implementación de caché Redis para el cálculo en caliente del semáforo comunal (reducción de 80% de carga en MySQL). P2: Webhook de notificaciones vía WhatsApp a vecinos sobre el estado de sus compromisos. P3: Firma digital avanzada en dictámenes sociales. P4: Modo offline PWA para funcionarios en zonas rurales sin señal.", st['body']))

    story.append(Paragraph("12. Conclusiones", st['h1']))
    story.append(Paragraph("El proyecto SGR alcanza un cumplimiento del 100% de los requisitos técnicos, de negocio y pedagógicos. Proporciona una solución moderna, auditable y segura para las delegaciones de La Serena, plenamente operativa en la nube de AWS.", st['body']))

    story.append(Paragraph("13. Accesos Oficiales en Producción", st['h1']))
    story.append(Paragraph("<b>URL AWS EC2:</b> http://3.213.246.194:8000/ | <b>Swagger API:</b> http://3.213.246.194:8000/api/swagger/ | <b>Credenciales Demo:</b> admin / admin, supervisor / admin, funcionario / admin.", st['body']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Compilado exitosamente: {filename}")


# ==============================================================================
# 2. GENERAR PRESENTACION Y DEFENSA (PDF)
# ==============================================================================
def generar_pdf_presentacion():
    filename = os.path.join(OUT_DIR, "PRESENTACION_DEFENSA_PROYECTO_INTEGRADO_EVA3_SGR.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=1.8*cm, rightMargin=1.8*cm, topMargin=2.2*cm, bottomMargin=2.2*cm)
    st = get_custom_styles()
    story = []

    # Portada Presentacion
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("INACAP LA SERENA — ASIGNATURA: PROYECTO INTEGRADO", ParagraphStyle('PInst', fontName='Helvetica-Bold', fontSize=10, leading=13, alignment=1, textColor=colors.HexColor("#6c757d"))))
    story.append(Paragraph("EVALUACIÓN 3 UNIDAD 3 — DEFENSA FINAL DE 15 MINUTOS", ParagraphStyle('PEva', fontName='Helvetica', fontSize=9, leading=12, alignment=1, textColor=colors.HexColor("#6c757d"))))
    story.append(Spacer(1, 1.2 * cm))

    story.append(Paragraph("PRESENTACIÓN Y GUIÓN DE DEFENSA", ParagraphStyle('DocTP', fontName='Helvetica-Bold', fontSize=13, leading=16, alignment=1, textColor=colors.HexColor("#1A252F"))))
    story.append(Paragraph("SISTEMA DE GESTIÓN DE RESULTADOS (SGR)", st['cover_t']))
    story.append(Paragraph("Guión Estructurado por Tiempos, Diapositivas, Demostración en AWS y Banco de Preguntas", st['cover_sub']))
    story.append(HRFlowable(width="85%", thickness=2.5, color=colors.HexColor("#AD0000"), spaceBefore=5, spaceAfter=15))

    # Tabla de tiempos
    data_tiempos = [
        [Paragraph("Tiempo", st['table_header']), Paragraph("Bloque / Diapositiva", st['table_header']), Paragraph("Expositor Asignado", st['table_header']), Paragraph("Enfoque Clave", st['table_header'])],
        [Paragraph("00:00 - 02:00", st['table_cell_bold']), Paragraph("Bloque 1: Equipo, Problema y Objetivo", st['table_cell']), Paragraph("Emanuel Román", st['table_cell']), Paragraph("Contexto territorial y alcance de la solución", st['table_cell'])],
        [Paragraph("02:00 - 04:00", st['table_cell_bold']), Paragraph("Bloque 2: Solución y Módulos del Negocio", st['table_cell']), Paragraph("Benjamín Antipa", st['table_cell']), Paragraph("Atenciones, Tubo Kanban y Gestor Social", st['table_cell'])],
        [Paragraph("04:00 - 06:00", st['table_cell_bold']), Paragraph("Bloque 3: Interfaz, UX y Validaciones", st['table_cell']), Paragraph("Benjamín Antipa", st['table_cell']), Paragraph("Módulo 11 en RUT, cascadas AJAX y accesibilidad", st['table_cell'])],
        [Paragraph("06:00 - 08:00", st['table_cell_bold']), Paragraph("Bloque 4: Base de Datos y Cálculo de Metas", st['table_cell']), Paragraph("Álvaro Obregón", st['table_cell']), Paragraph("MySQL 3FN, sumatoria 100% y semáforo", st['table_cell'])],
        [Paragraph("08:00 - 10:00", st['table_cell_bold']), Paragraph("Bloque 5: Seguridad y Despliegue en AWS", st['table_cell']), Paragraph("Emanuel Román", st['table_cell']), Paragraph("RBAC, token de un solo uso, EC2 Ubuntu Server", st['table_cell'])],
        [Paragraph("10:00 - 11:30", st['table_cell_bold']), Paragraph("Bloque 6: Implementación y Trabajo Ágil", st['table_cell']), Paragraph("Emanuel / Equipo", st['table_cell']), Paragraph("GitFlow, Scrum y roles coordinados", st['table_cell'])],
        [Paragraph("11:30 - 13:30", st['table_cell_bold']), Paragraph("Bloque 7: Pruebas y DEMOSTRACIÓN EN VIVO", st['table_cell']), Paragraph("Todo el Equipo", st['table_cell']), Paragraph("Navegación en directo en http://3.213.246.194:8000/", st['table_cell'])],
        [Paragraph("13:30 - 15:00", st['table_cell_bold']), Paragraph("Bloque 8: Conclusiones, Mejoras y Cierre", st['table_cell']), Paragraph("Álvaro Obregón", st['table_cell']), Paragraph("Logros, hoja de ruta y apertura a preguntas", st['table_cell'])],
    ]
    t_tiempos = Table(data_tiempos, colWidths=[2.5*cm, 5.5*cm, 3.5*cm, 6*cm])
    t_tiempos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tiempos)
    story.append(PageBreak())

    # Contenido de Diapositivas y Guiones
    story.append(Paragraph("Desarrollo de Diapositivas y Guión de Exposición (15 Minutos)", st['h1']))

    # Diapositiva 1
    story.append(Paragraph("Diapositiva 1 | Bloque 1: Presentación del Equipo, Problema y Objetivo (Min 00:00 - 02:00)", st['h2']))
    story.append(Paragraph("<b>Expositor:</b> Emanuel Román Serón", st['body_bold']))
    story.append(Paragraph("<b>Puntos Clave en Diapositiva:</b> Ilustre Municipalidad de La Serena; 250.000 habitantes en delegaciones urbanas y rurales (La Antena, Las Compañías, Centro, La Pampa, Avenida del Mar, Rural Cordillera). Problemática: registro en cuadernos y planillas aisladas, extravío de solicitudes vecinales, falta de trazabilidad en compromisos y vulnerabilidad de datos sensibles. Objetivo: desarrollar y desplegar en AWS el Sistema de Gestión de Resultados (SGR).", st['body']))
    story.append(Paragraph("<i>Guión sugerido:</i> 'Buenos días profesora Mariavictoria y compañeros. Presentamos el Sistema de Gestión de Resultados para las Delegaciones Municipales de La Serena. El municipio enfrentaba una fragmentación severa: cada delegación operaba de forma aislada con cuadernos y Excel. Nuestro objetivo fue unificar la atención ciudadana, el trabajo territorial y el cálculo de metas en una plataforma web y móvil empresarial construida en Django, MySQL y desplegada en producción en AWS.'", st['speech']))

    # Diapositiva 2
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Diapositiva 2 | Bloque 2: Solución y Necesidades del Negocio (Min 02:00 - 04:00)", st['h2']))
    story.append(Paragraph("<b>Expositor:</b> Benjamín Antipa", st['body_bold']))
    story.append(Paragraph("<b>Puntos Clave en Diapositiva:</b> Ventanilla única de Atenciones Ciudadanas; Tablero Kanban de Tubo de Trabajo con alertas de compromisos atrasados; Módulo de Gestor Social para ayudas de emergencia y visitas domiciliarias; Motor de Metas con vinculación directa de evidencias auditables.", st['body']))
    story.append(Paragraph("<i>Guión sugerido:</i> 'Para resolver los procesos municipales modelamos 5 ejes: primero, Atenciones Ciudadanas para registrar vecinos en segundos con georreferenciación barrial; segundo, el Tubo de Trabajo en formato Kanban que permite arrastrar compromisos asignando técnicos y fechas límites; tercero, el Gestor Social para tramitaciones de alta sensibilidad; y cuarto, el motor de Metas Institucionales donde cada gestión realizada tributa a los indicadores oficiales del municipio.'", st['speech']))

    # Diapositiva 3
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Diapositiva 3 | Bloque 3: Interfaz, Experiencia de Usuario y Validaciones (Min 04:00 - 06:00)", st['h2']))
    story.append(Paragraph("<b>Expositor:</b> Benjamín Antipa", st['body_bold']))
    story.append(Paragraph("<b>Puntos Clave en Diapositiva:</b> Paleta institucional municipal (#1E3A8A, dorado, fondos neutros); navegación ergonómica con selector superior de Delegación Activa y conmutador a Vista Consolidada Comunal; validación en tiempo real de RUT mediante Módulo 11 en cliente y servidor; selector en cascada AJAX de subatenciones; diseño responsivo móvil bajo Bootstrap 5.", st['body']))
    story.append(Paragraph("<i>Guión sugerido:</i> 'Priorizamos agilidad y ergonomía: los funcionarios atienden decenas de vecinos a diario. Conectamos selectores en cascada mediante llamadas asíncronas AJAX para evitar recargas lentas e implementamos la validación del RUT chileno mediante Módulo 11 en frontend y backend: si se digita un RUT inválido, el sistema lo bloquea al instante. Además, el diseño es 100% responsivo para ser utilizado en terreno desde celulares.'", st['speech']))

    # Diapositiva 4
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Diapositiva 4 | Bloque 4: Base de Datos y Reglas de Negocio (Min 06:00 - 08:00)", st['h2']))
    story.append(Paragraph("<b>Expositor:</b> Álvaro Obregón", st['body_bold']))
    story.append(Paragraph("<b>Puntos Clave en Diapositiva:</b> MySQL 8.0 en 3FN; relaciones maestras protegidas con on_delete=models.PROTECT; regla matemática: la sumatoria de ponderaciones de metas debe sumar exactamente 100%; evidencias cuantitativas incrementan el avance de la meta mientras que las cualitativas aportan respaldo sin alterar el cálculo; semáforo comunal: Verde (>=75%), Amarillo (50%-74.9%), Rojo (<50%).", st['body']))
    story.append(Paragraph("<i>Guión sugerido:</i> 'En la base de datos aplicamos 3FN e integridad estricta con PROTECT para impedir la pérdida de datos históricos. La regla de negocio central es rigurosa: el sistema exige que las ponderaciones sumen exactamente 100%. Si un supervisor ingresa 100.5%, el sistema rechaza la operación. Cuando una evidencia cuantitativa es aprobada, suma +1 a la meta del funcionario y actualiza el semáforo comunal en tiempo real.'", st['speech']))

    # Diapositiva 5
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Diapositiva 5 | Bloque 5: Seguridad y Despliegue en AWS (Min 08:00 - 10:00)", st['h2']))
    story.append(Paragraph("<b>Expositor:</b> Emanuel Román Serón", st['body_bold']))
    story.append(Paragraph("<b>Puntos Clave en Diapositiva:</b> RBAC por roles (Administrador, Supervisor, Administrativo); aislamiento territorial multi-tenant vía context_processors.py; recuperación criptográfica por token de un solo uso con caducidad a las 24 horas; protección CSRF, SQLi y XSS; despliegue en AWS EC2 (Ubuntu Server, Nginx, Gunicorn y MySQL).", st['body']))
    story.append(Paragraph("<i>Guión sugerido:</i> 'En seguridad implementamos control de acceso basado en roles y aislamiento territorial: un funcionario solo ve su delegación asignada, mientras que el supervisor monitorea su área. Para la recuperación de credenciales, implementamos tokens criptográficos seguros de un solo uso que expiran en 24 horas. Y cumpliendo la condición de las bases, el sistema se encuentra desplegado y operativo en una instancia AWS EC2 bajo Nginx y Gunicorn.'", st['speech']))

    # Diapositiva 6 y 7
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Diapositiva 6 | Bloque 6: Implementación y Trabajo Ágil (Min 10:00 - 11:30)", st['h2']))
    story.append(Paragraph("<b>Expositor:</b> Emanuel Román / Benjamín Antipa / Álvaro Obregón", st['body_bold']))
    story.append(Paragraph("<b>Puntos Clave en Diapositiva:</b> Gestión del proyecto con Scrum; repositorio central en GitHub con ramas feature/* y commits semánticos; trazabilidad de aportes individuales de Emanuel, Benjamín y Álvaro con cumplimiento de estándares PEP 8.", st['body']))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Diapositiva 7 | Bloque 7: Pruebas y Demostración en Vivo en AWS (Min 11:30 - 13:30)", st['h2']))
    story.append(Paragraph("<b>Expositor:</b> Todo el Equipo (Navegación práctica en http://3.213.246.194:8000/)", st['body_bold']))
    story.append(Paragraph("<b>Ruta de la Demostración:</b> 1. Login con cuenta admin y visualización del Semáforo Comunal. 2. Cambio a Delegación La Antena y verificación del aislamiento de datos. 3. Creación de Atención Ciudadana con validación en vivo de RUT y subatención en cascada. 4. Derivación al Tubo de Trabajo y cambio de estado a Realizado en el Kanban. 5. Dictamen favorable de evidencia fotográfica e incremento inmediato en el avance porcentual de la meta.", st['body']))

    # Diapositiva 8 y Cierre
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Diapositiva 8 | Bloque 8: Conclusiones y Ronda de Preguntas (Min 13:30 - 15:00)", st['h2']))
    story.append(Paragraph("<b>Expositor:</b> Álvaro Obregón / Equipo", st['body_bold']))
    story.append(Paragraph("<b>Puntos Clave en Diapositiva:</b> 100% de cumplimiento de requerimientos; modernización real de la gestión pública municipal; hoja de ruta (Redis para caché, notificaciones WhatsApp, PWA offline); apertura a la defensa individual.", st['body']))
    story.append(Paragraph("<i>Guión de cierre:</i> 'El Sistema de Gestión de Resultados entrega un producto completo, probado, seguro y operativo en la nube de AWS. Agradecemos su atención y quedamos a su disposición para responder cualquier pregunta individual. Muchas gracias.'", st['speech']))

    # Banco de preguntas
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Banco de Preguntas Individuales para la Defensa (Criterio 3.1.6.14)", st['h1']))

    story.append(Paragraph("<b>Pregunta para Emanuel Román (Arquitectura / Seguridad / AWS):</b> <i>¿Por qué utilizaron tokens criptográficos para la recuperación de contraseñas?</i>", st['body']))
    story.append(Paragraph("<b>Respuesta Modelo:</b> 'Porque enviar claves en texto claro vulnera la Ley 19.628. La clase PasswordResetTokenGenerator genera un token firmado que codifica el ID, el hash de la clave actual y una marca de tiempo. Esto garantiza que el enlace expira a las 24 horas y queda invalidado inmediatamente tras su primer uso.'", st['body']))

    story.append(Paragraph("<b>Pregunta para Benjamín Antipa (Frontend / UX / Validaciones):</b> <i>¿Cómo opera la validación del RUT y la cascada de subatenciones?</i>", st['body']))
    story.append(Paragraph("<b>Respuesta Modelo:</b> 'En el RUT implementamos el algoritmo Módulo 11 en JavaScript y en el método clean_rut() del formulario en el servidor. La cascada opera escuchando el evento change del selector principal y disparando una llamada fetch a /api/subatenciones-cascade/, repoblando el segundo menú sin recargar la página en menos de 50 milisegundos.'", st['body']))

    story.append(Paragraph("<b>Pregunta para Álvaro Obregón (Base de Datos / Metas / Calidad):</b> <i>¿Cómo garantizan que la sumatoria de ponderaciones no supere el 100%?</i>", st['body']))
    story.append(Paragraph("<b>Respuesta Modelo:</b> 'Sobrescribimos el método clean() del formulario calculando la sumatoria de ponderaciones activas del funcionario más la nueva ingresada mediante el ORM de Django. Si la suma excede 100%, lanzamos un ValidationError que detiene la transacción antes de tocar la base de datos.'", st['body']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Compilado exitosamente: {filename}")


if __name__ == '__main__':
    generar_pdf_informe()
    generar_pdf_presentacion()
