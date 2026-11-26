"""
Compilador ReportLab para generar el Informe Técnico Formal en PDF de la
Evaluación Sumativa #4: API RESTful con DRF, SimpleJWT, Swagger UI y AWS EC2.
Genera: INFORME_TECNICO_SGR_EVALUACION_4.pdf
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para calcular y numerar páginas dinámicamente ('Página X de Y')."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

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
        self.drawString(
            2 * cm, 26.5 * cm,
            "INACAP La Serena — TI3V41 Programación Back End | API RESTful SGR Municipalidad"
        )
        self.setStrokeColor(colors.HexColor("#AD0000"))
        self.setLineWidth(1)
        self.line(2 * cm, 26.3 * cm, 19.5 * cm, 26.3 * cm)

        # Pie de página inferior
        self.setStrokeColor(colors.HexColor("#dee2e6"))
        self.setLineWidth(0.5)
        self.line(2 * cm, 2 * cm, 19.5 * cm, 2 * cm)

        self.drawString(
            2 * cm, 1.5 * cm,
            "Evaluación Sumativa #4 — DRF, JWT, Swagger UI, Serializadores Diferenciados y AWS"
        )
        page_str = f"Página {self._pageNumber} de {total_pages}"
        self.drawRightString(19.5 * cm, 1.5 * cm, page_str)
        self.restoreState()


def build_pdf(filename=None):
    if filename is None:
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "INFORME_TECNICO_SGR_EVALUACION_4.pdf")
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    c_primary = colors.HexColor("#AD0000")   # Rojo INACAP
    c_dark = colors.HexColor("#1A252F")      # Texto oscuro principal
    c_gray = colors.HexColor("#495057")

    title_cover = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=c_primary,
        alignment=1,
        spaceAfter=12
    )

    subtitle_cover = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_dark,
        alignment=1,
        spaceAfter=25
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_dark,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=6,
        alignment=4  # Justificado
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4
    )

    story = []

    # =========================================================================
    # PORTADA
    # =========================================================================
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("INACAP — SEDE LA SERENA", ParagraphStyle('Inst', fontName='Helvetica-Bold', fontSize=12, leading=15, alignment=1, textColor=colors.HexColor("#6c757d"))))
    story.append(Paragraph("Área Tecnologías de la Información y Ciberseguridad", ParagraphStyle('Area', fontName='Helvetica', fontSize=10, leading=13, alignment=1, textColor=colors.HexColor("#6c757d"))))
    story.append(Spacer(1, 2.5 * cm))

    story.append(Paragraph("INFORME TÉCNICO FORMAL", ParagraphStyle('SubPre', fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, textColor=c_dark)))
    story.append(Paragraph("Desarrollo de API RESTful con Autenticación JWT y Documentación Swagger UI", title_cover))
    story.append(Paragraph("Sistema de Gestión de Resultados (SGR) — Ilustre Municipalidad de La Serena", subtitle_cover))

    story.append(HRFlowable(width="80%", thickness=2, color=c_primary, spaceBefore=10, spaceAfter=25))

    meta_data = [
        [Paragraph("<b>Asignatura:</b>", body_style), Paragraph("Programación Back End (TI3V41)", body_style)],
        [Paragraph("<b>Docente:</b>", body_style), Paragraph("Alex Díaz Araos", body_style)],
        [Paragraph("<b>Evaluación:</b>", body_style), Paragraph("Evaluación Sumativa #4 (30% Ponderación Final)", body_style)],
        [Paragraph("<b>Infraestructura Cloud:</b>", body_style), Paragraph("Amazon Web Services (AWS EC2) — IP: 3.213.246.194", body_style)],
        [Paragraph("<b>Entorno Tecnológico:</b>", body_style), Paragraph("Django 6, DRF 3.18, SimpleJWT 5.5, OpenAPI 3, MySQL 8.4", body_style)],
        [Paragraph("<b>Fecha:</b>", body_style), Paragraph("Noviembre 2026 — La Serena, Chile", body_style)],
    ]
    t_meta = Table(meta_data, colWidths=[5 * cm, 10 * cm])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_meta)
    story.append(PageBreak())

    # =========================================================================
    # SECCIÓN 1: RESUMEN EJECUTIVO Y OBJETIVOS
    # =========================================================================
    story.append(Paragraph("1. Resumen Ejecutivo y Objetivos Técnicos", h1_style))
    story.append(Paragraph(
        "El presente informe documenta el desarrollo de la API RESTful oficial para el Sistema de Gestión de Resultados "
        "(SGR) de la Municipalidad de La Serena, correspondiente a la Evaluación Sumativa #4 de la asignatura Programación "
        "Back End (TI3V41). La solución provee una interfaz de programación desacoplada que permite el consumo seguro de "
        "recursos municipales por parte de aplicaciones móviles de terreno y servicios interinstitucionales.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Objetivos Cumplidos al 100%:</b><br/>"
        "• Implementación de 2 Mantenedores RESTful completos (Delegaciones Municipales y Vecinos/Padrón Comunal) mediante Django REST Framework.<br/>"
        "• Implementación de la Transacción Central del Negocio (Gestiones Territoriales) con trazabilidad de Tubo de Trabajo y evidencias.<br/>"
        "• Esquema de autenticación sin estado (Stateless) mediante JSON Web Tokens (JWT) con rotación y refresco seguro.<br/>"
        "• Protección de datos personales (Ley N° 19.628) mediante Serializadores Diferenciados entre Administradores y Operadores.<br/>"
        "• Documentación viva e interactiva OpenAPI 3.0 / Swagger UI con botón de autorización Bearer integrado.<br/>"
        "• Despliegue en producción sobre instancia Ubuntu 26.04 en AWS EC2 con IP elástica 3.213.246.194.",
        body_style
    ))

    # =========================================================================
    # SECCIÓN 2: ARQUITECTURA Y DISEÑO DE ENDPOINTS
    # =========================================================================
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("2. Especificación de Endpoints y Operaciones CRUD", h1_style))
    story.append(Paragraph(
        "Se adoptó el patrón ModelViewSet de DRF con enrutador automático (DefaultRouter) bajo el prefijo /api/v1/. "
        "Todos los endpoints implementan semántica HTTP estricta y códigos de estado estandarizados.",
        body_style
    ))

    endpoints_data = [
        [Paragraph("<b>Recurso</b>", body_style), Paragraph("<b>Método</b>", body_style), Paragraph("<b>Endpoint URL</b>", body_style), Paragraph("<b>Descripción</b>", body_style), Paragraph("<b>Código Exitoso</b>", body_style)],
        [Paragraph("Auth", body_style), Paragraph("POST", code_style), Paragraph("/api/token/", code_style), Paragraph("Emisión de par de tokens (Access y Refresh)", body_style), Paragraph("200 OK", body_style)],
        [Paragraph("Auth", body_style), Paragraph("POST", code_style), Paragraph("/api/token/refresh/", code_style), Paragraph("Renovación de token de acceso", body_style), Paragraph("200 OK", body_style)],
        [Paragraph("Delegaciones", body_style), Paragraph("GET", code_style), Paragraph("/api/v1/delegaciones/", code_style), Paragraph("Listar todas las delegaciones", body_style), Paragraph("200 OK", body_style)],
        [Paragraph("Delegaciones", body_style), Paragraph("POST", code_style), Paragraph("/api/v1/delegaciones/", code_style), Paragraph("Crear delegación (Solo Administrador)", body_style), Paragraph("201 Created", body_style)],
        [Paragraph("Delegaciones", body_style), Paragraph("PUT/PATCH", code_style), Paragraph("/api/v1/delegaciones/{id}/", code_style), Paragraph("Actualizar delegación municipal", body_style), Paragraph("200 OK", body_style)],
        [Paragraph("Delegaciones", body_style), Paragraph("DELETE", code_style), Paragraph("/api/v1/delegaciones/{id}/", code_style), Paragraph("Eliminar delegación (Solo Administrador)", body_style), Paragraph("204 No Content", body_style)],
        [Paragraph("Vecinos", body_style), Paragraph("GET", code_style), Paragraph("/api/v1/vecinos/", code_style), Paragraph("Listar padrón (Diferenciado por rol)", body_style), Paragraph("200 OK", body_style)],
        [Paragraph("Vecinos", body_style), Paragraph("POST", code_style), Paragraph("/api/v1/vecinos/", code_style), Paragraph("Registrar nuevo vecino comunal", body_style), Paragraph("201 Created", body_style)],
        [Paragraph("Vecinos", body_style), Paragraph("DELETE", code_style), Paragraph("/api/v1/vecinos/{id}/", code_style), Paragraph("Eliminar vecino (Solo Administrador)", body_style), Paragraph("204 No Content", body_style)],
        [Paragraph("Gestiones", body_style), Paragraph("GET", code_style), Paragraph("/api/v1/gestiones/", code_style), Paragraph("Listar actividades (Diferenciado por rol)", body_style), Paragraph("200 OK", body_style)],
        [Paragraph("Gestiones", body_style), Paragraph("POST", code_style), Paragraph("/api/v1/gestiones/", code_style), Paragraph("Registrar requerimiento territorial", body_style), Paragraph("201 Created", body_style)],
        [Paragraph("Gestiones", body_style), Paragraph("PUT/PATCH", code_style), Paragraph("/api/v1/gestiones/{id}/", code_style), Paragraph("Actualizar estado o derivación a Tubo", body_style), Paragraph("200 OK", body_style)],
        [Paragraph("Swagger UI", body_style), Paragraph("GET", code_style), Paragraph("/api/docs/", code_style), Paragraph("Interfaz interactiva Swagger UI", body_style), Paragraph("200 OK", body_style)],
        [Paragraph("OpenAPI", body_style), Paragraph("GET", code_style), Paragraph("/api/schema/", code_style), Paragraph("Esquema formal OpenAPI 3.0 (YAML)", body_style), Paragraph("200 OK", body_style)],
    ]
    t_end = Table(endpoints_data, colWidths=[2.2 * cm, 1.6 * cm, 4.2 * cm, 5.5 * cm, 2.2 * cm])
    t_end.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#AD0000")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_end)

    # =========================================================================
    # SECCIÓN 3: AUTENTICACIÓN JWT Y SERIALIZADORES DIFERENCIADOS
    # =========================================================================
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("3. Seguridad, Autenticación JWT y Protección de Datos Sensibles", h1_style))
    story.append(Paragraph(
        "<b>Flujo de Autenticación Stateless (SimpleJWT):</b><br/>"
        "La autenticación se realiza mediante intercambio de credenciales contra /api/token/. "
        "El cliente recibe un Access Token firmado con vigencia de 60 minutos y un Refresh Token de 24 horas. "
        "Cada petición protegida debe incluir la cabecera <code>Authorization: Bearer &lt;token&gt;</code>.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Arquitectura de Serializadores Diferenciados (Cumplimiento Ley 19.628):</b><br/>"
        "Para conciliar la necesidad operativa de los funcionarios en terreno con el respeto estricto a la privacidad de los vecinos de La Serena, "
        "se diseñaron serializadores polimórficos resueltos en tiempo de ejecución por el método <code>get_serializer_class()</code>:",
        body_style
    ))

    sec_data = [
        [Paragraph("<b>Entidad</b>", body_style), Paragraph("<b>Perfil Administrador</b>", body_style), Paragraph("<b>Perfil Operador / Estándar</b>", body_style)],
        [
            Paragraph("<b>Vecinos / Padrón</b>", body_style),
            Paragraph("Acceso total a datos reales:<br/>• RUT: <code>15.987.654-3</code><br/>• Teléfono: <code>+56912345678</code><br/>• Correo: <code>carlos.vecino@gmail.com</code>", body_style),
            Paragraph("Datos sensibles enmascarados dinámicamente:<br/>• RUT: <code>15.***.***-3</code><br/>• Teléfono: <code>+56 9 ****-****</code><br/>• Correo: <code>c****@gmail.com</code>", body_style)
        ],
        [
            Paragraph("<b>Gestiones Centrales</b>", body_style),
            Paragraph("Exposición completa de auditoría:<br/>• Datos de contacto directos del solicitante.<br/>• Observaciones privadas de revisión de evidencia.<br/>• Identificación de usuario creador y revisor interno.", body_style),
            Paragraph("Protección de privacidad y auditoría interna:<br/>• Contacto y RUT del vecino enmascarados.<br/>• Campo <code>observacion_revision</code> excluido.<br/>• Datos de auditoría interna restringidos.", body_style)
        ],
    ]
    t_sec = Table(sec_data, colWidths=[3.5 * cm, 6 * cm, 6.5 * cm])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A252F")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_sec)

    # =========================================================================
    # SECCIÓN 4: RECOMENDACIONES IA (OWASP API TOP 10)
    # =========================================================================
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("4. Recomendaciones de Seguridad Asistidas por Inteligencia Artificial", h1_style))
    story.append(Paragraph(
        "A través de una auditoría estática asistida por modelos de Inteligencia Artificial para seguridad back-end, "
        "se evaluaron los riesgos del estándar <b>OWASP API Security Top 10</b> y se implementaron salvaguardas directas en el código:",
        body_style
    ))
    story.append(Paragraph(
        "<b>1. API1:2023 Broken Object Level Authorization (BOLA / IDOR):</b> Mitigado filtrando el QuerySet en base al atributo "
        "<code>delegacion_activa</code> del perfil de usuario, impidiendo que funcionarios accedan a gestiones de otras dependencias.<br/>"
        "<b>2. API2:2023 Broken Authentication:</b> Mitigado mediante SimpleJWT con expiración acotada (60 min) y rechazo estricto (401) de solicitudes sin token.<br/>"
        "<b>3. API3:2023 Broken Object Property Level Authorization:</b> Mitigado definiendo <code>read_only_fields</code> en serializadores para evitar inyección de campos privilegiados.<br/>"
        "<b>4. API5:2023 Broken Function Level Authorization:</b> Mitigado asignando <code>IsAdminUserRole</code> a los métodos destructivos (DELETE).",
        body_style
    ))

    # =========================================================================
    # SECCIÓN 5: PRUEBAS AUTOMATIZADAS Y RESULTADOS
    # =========================================================================
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("5. Validación Automatizada y Resultados de la Suite de Pruebas", h1_style))
    story.append(Paragraph(
        "Se ejecutó la suite de pruebas unitarias y de integración <code>test_api.py</code>, logrando un 100% de éxito en todos los escenarios evaluados:",
        body_style
    ))

    test_data = [
        [Paragraph("<b>Identificador de Prueba</b>", body_style), Paragraph("<b>Objetivo y Aseveración Verificada</b>", body_style), Paragraph("<b>Resultado</b>", body_style)],
        [Paragraph("test_01_autenticacion_jwt", code_style), Paragraph("Emisión y refresco de tokens JWT en /api/token/ y /api/token/refresh/", body_style), Paragraph("APROBADO (OK)", body_style)],
        [Paragraph("test_02_seguridad_sin_token", code_style), Paragraph("Bloqueo de acceso no autorizado con código HTTP 401 Unauthorized", body_style), Paragraph("APROBADO (OK)", body_style)],
        [Paragraph("test_03_crud_delegaciones", code_style), Paragraph("CRUD completo; bloqueo de creación a Operador (403) y autorización a Admin (201, 204)", body_style), Paragraph("APROBADO (OK)", body_style)],
        [Paragraph("test_04_serializadores_vecinos", code_style), Paragraph("Validación de datos censurados para Operador y datos reales para Administrador", body_style), Paragraph("APROBADO (OK)", body_style)],
        [Paragraph("test_05_transaccion_gestiones", code_style), Paragraph("Creación de gestión con Tubo y ocultamiento de observaciones de auditoría a Operador", body_style), Paragraph("APROBADO (OK)", body_style)],
        [Paragraph("test_06_documentacion_swagger", code_style), Paragraph("Disponibilidad HTTP 200 de los endpoints OpenAPI 3 (/api/schema/) y Swagger UI (/api/docs/)", body_style), Paragraph("APROBADO (OK)", body_style)],
    ]
    t_test = Table(test_data, colWidths=[5 * cm, 8.5 * cm, 2.5 * cm])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_test)

    # =========================================================================
    # SECCIÓN 6: CONCLUSIONES
    # =========================================================================
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("6. Conclusiones y Estado del Proyecto", h1_style))
    story.append(Paragraph(
        "La implementación de la API RESTful para el Sistema de Gestión de Resultados cumple íntegramente con cada requisito de la Evaluación Sumativa #4: "
        "arquitectura modular DRF, seguridad JWT robusta, protección de datos ciudadanos mediante serializadores diferenciados y documentación interactiva Swagger UI. "
        "El código base se encuentra versionado en GitHub y preparado para servir a la comunidad de La Serena con altos estándares de calidad y seguridad.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Informe compilado exitosamente: {filename}")


if __name__ == '__main__':
    build_pdf()
