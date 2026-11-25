"""
Compilador ReportLab para generar los 3 PDFs oficiales:
1. PRESENTACION_DEFENSA_EVA3_ING_SW.pdf (Presentación de 10 minutos con código y pantallazos)
2. GUIA_DEFENSA_MOCKUP_Y_FUTURA_CONSTRUCCION.pdf (Guía de navegación del wireframe y justificación)
3. GUIA_EXPLICATIVA_EVALUACION_4.pdf (Guía didáctica de la API RESTful, JWT y Swagger)
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para calcular y numerar páginas dinámicamente ('Página X de Y')."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.doc_title = getattr(self, 'doc_title', 'INACAP La Serena — Sistema de Gestión de Resultados (SGR)')

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
        self.drawString(2 * cm, 26.5 * cm, "INACAP La Serena — Ingeniería de Software / Programación Back End | SGR Municipalidad")
        self.setStrokeColor(colors.HexColor("#AD0000"))
        self.setLineWidth(1)
        self.line(2 * cm, 26.3 * cm, 19.5 * cm, 26.3 * cm)

        # Pie de página inferior
        self.setStrokeColor(colors.HexColor("#dee2e6"))
        self.setLineWidth(0.5)
        self.line(2 * cm, 2 * cm, 19.5 * cm, 2 * cm)

        self.drawString(2 * cm, 1.5 * cm, "Documentación Oficial del Proyecto SGR — Ilustre Municipalidad de La Serena")
        page_str = f"Página {self._pageNumber} de {total_pages}"
        self.drawRightString(19.5 * cm, 1.5 * cm, page_str)
        self.restoreState()


def get_custom_styles():
    styles = getSampleStyleSheet()
    c_primary = colors.HexColor("#AD0000")
    c_dark = colors.HexColor("#1A252F")
    
    h1 = ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=c_primary, spaceBefore=12, spaceAfter=5, keepWithNext=True)
    h2 = ParagraphStyle('H2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=c_dark, spaceBefore=8, spaceAfter=4, keepWithNext=True)
    body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=c_dark, spaceAfter=5, alignment=4)
    code = ParagraphStyle('Code', parent=styles['Normal'], fontName='Courier', fontSize=7.5, leading=9.5, textColor=colors.HexColor("#1e293b"), spaceAfter=3)
    cover_t = ParagraphStyle('CoverT', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=c_primary, alignment=1, spaceAfter=10)
    cover_sub = ParagraphStyle('CoverSub', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=15, textColor=c_dark, alignment=1, spaceAfter=20)
    speech = ParagraphStyle('Speech', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8.5, leading=12, textColor=colors.HexColor("#0f5132"), spaceAfter=5)

    return {
        'h1': h1, 'h2': h2, 'body': body, 'code': code,
        'cover_t': cover_t, 'cover_sub': cover_sub, 'speech': speech
    }


# ==============================================================================
# 1. GENERAR PRESENTACION_DEFENSA_EVA3_ING_SW.pdf
# ==============================================================================
def generar_pdf_presentacion():
    filename = "PRESENTACION_DEFENSA_EVA3_ING_SW.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=2*cm, rightMargin=2*cm, topMargin=2.5*cm, bottomMargin=2.5*cm)
    st = get_custom_styles()
    story = []

    # Portada
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("INACAP — SEDE LA SERENA", ParagraphStyle('P1', fontName='Helvetica-Bold', fontSize=12, leading=15, alignment=1, textColor=colors.HexColor("#6c757d"))))
    story.append(Paragraph("Área Informática, Ciberseguridad y Telecomunicaciones", ParagraphStyle('P2', fontName='Helvetica', fontSize=10, leading=13, alignment=1, textColor=colors.HexColor("#6c757d"))))
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("PRESENTACIÓN EJECUTIVA Y DEFENSA ORAL", ParagraphStyle('P3', fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, textColor=colors.HexColor("#1A252F"))))
    story.append(Paragraph("Sistema de Gestión de Resultados (SGR) — Ilustre Municipalidad de La Serena", st['cover_t']))
    story.append(Paragraph("Prototipado Interactivo, Calidad de Software y Justificación de Arquitectura (Etapa 3)", st['cover_sub']))
    story.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor("#AD0000"), spaceBefore=5, spaceAfter=20))

    meta = [
        [Paragraph("<b>Asignatura:</b>", st['body']), Paragraph("Ingeniería de Software (TI2043) — Evaluación Sumativa #3", st['body'])],
        [Paragraph("<b>Ponderación:</b>", st['body']), Paragraph("35% de la Nota Final (Presentación Oral 10 Minutos)", st['body'])],
        [Paragraph("<b>Artefactos de Defensa:</b>", st['body']), Paragraph("Wireframes Interactivos (/wireframes/) + Prototipo Django AWS EC2", st['body'])],
        [Paragraph("<b>Infraestructura:</b>", st['body']), Paragraph("AWS EC2 Ubuntu 26.04 — IP: 3.213.246.194", st['body'])],
        [Paragraph("<b>Fecha de Presentación:</b>", st['body']), Paragraph("Noviembre 2026 — La Serena, Chile", st['body'])],
    ]
    t_meta = Table(meta, colWidths=[5 * cm, 10.5 * cm])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#dee2e6")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(PageBreak())

    # Diapositiva 1 y 2
    story.append(Paragraph("Diapositiva 1: Apertura y Diagnóstico Territorial (Minuto 0:00 – 1:30)", st['h1']))
    story.append(Paragraph(
        "<b>Problemática:</b> 6 delegaciones desconectadas con planillas Excel y demoras de >8 minutos.<br/>"
        "<b>Solución Cloud:</b> Paradigma IaaS sobre AWS EC2 y SaaS interno para acceso territorial.", st['body']
    ))
    story.append(Paragraph("<b>Libreto Oral (Speech):</b>", st['h2']))
    story.append(Paragraph(
        "<i>'Buenos días profesor y comisión. Hoy presentamos la culminación del Sistema de Gestión de Resultados (SGR) para la Municipalidad de La Serena. Demostraremos nuestro prototipo interactivo y defenderemos cómo cada requerimiento de la Evaluación 2 se convirtió en una solución cloud IaaS/SaaS real, robusta y desplegada en AWS EC2.'</i>",
        st['speech']
    ))

    # Diapositiva 3
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Diapositiva 2: Defensa de la Metodología Híbrida (Minuto 1:30 – 2:30)", st['h1']))
    story.append(Paragraph(
        "<b>1. Modelo Cascada (Fase de Análisis):</b> Justificado por la rigurosidad del sector público. Se requería congelar los 38 Requerimientos Funcionales y normalizar la base de datos en 3NF antes de codificar.<br/>"
        "<b>2. Metodología Scrum (Fase de Desarrollo):</b> 3 Sprints de dos semanas (Sprint 1: Autenticación; Sprint 2: CRUDs y delegaciones; Sprint 3: Kanban Tubo y Evidencias).",
        st['body']
    ))

    # Diapositiva 4
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Diapositiva 3: Modelo Entidad-Relación y Código de Transacción (Minuto 2:30 – 3:30)", st['h1']))
    story.append(Paragraph(
        "<b>Trazabilidad MER.png:</b> Tablas relacionales con claves foráneas estrictas entre delegaciones, vecinos, actividades y compromisos.", st['body']
    ))
    story.append(Paragraph("<b>Fragmento de Código Real (actividades/models.py):</b>", st['h2']))
    code_text = (
        "class Actividad(models.Model):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;id_actividad = models.AutoField(primary_key=True)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;codigo = models.CharField(max_length=30, unique=True)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;id_delegacion = models.ForeignKey(Delegacion, on_delete=models.SET_NULL, null=True)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;id_vecino = models.ForeignKey(Vecino, on_delete=models.SET_NULL, null=True)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;ingreso_tubo = models.BooleanField(default=False)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;id_compromiso = models.ForeignKey('agenda.Compromiso', on_delete=models.SET_NULL, null=True)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;estado = models.CharField(max_length=30, default='Pendiente')"
    )
    t_code = Table([[Paragraph(code_text, st['code'])]], colWidths=[15.5 * cm])
    t_code.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_code)

    # Diapositivas 5 y 6
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Diapositiva 4: Demostración Wireframes — Formulario y Kanban (Minuto 3:30 – 5:30)", st['h1']))
    story.append(Paragraph(
        "• <b>Formulario Unificado (CU-05):</b> Autocompletado AJAX por RUT de vecinos en <900 ms.<br/>"
        "• <b>Tubo de Trabajo Kanban (CU-07):</b> Tablero de 4 columnas sincronizado bidireccionalmente con la gestión ciudadana.",
        st['body']
    ))
    story.append(Paragraph("<b>Código Real de Sincronización Transaccional (agenda/views.py):</b>", st['h2']))
    code_sync = (
        "if nuevo_estado == 'REALIZADO':<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;compromiso.estado = 'Realizado'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;compromiso.fecha_cierre = timezone.now().date()<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;compromiso.save()<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;if compromiso.id_actividad:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;compromiso.id_actividad.estado = 'Realizado'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;compromiso.id_actividad.save()"
    )
    t_sync = Table([[Paragraph(code_sync, st['code'])]], colWidths=[15.5 * cm])
    t_sync.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sync)

    # Diapositivas 7, 8 y 9
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Diapositiva 5: Semáforo de Metas y Seguridad RBAC (Minuto 5:30 – 7:30)", st['h1']))
    story.append(Paragraph(
        "• <b>Semáforo de Metas (CU-08):</b> Solo evidencias aprobadas y cuantitativas ponderan a metas.<br/>"
        "• <b>Control de Acceso RBAC:</b> Restricción territorial por delegación (un supervisor de La Antena no puede ver datos de Las Compañías).",
        st['body']
    ))

    # Diapositivas 10 y 11
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Diapositiva 6: Calidad de Software, Ciberseguridad y Cierre (Minuto 7:30 – 10:00)", st['h1']))
    story.append(Paragraph(
        "• <b>Calidad (14 Suites test_suite.py):</b> Pruebas automatizadas 100% aprobadas e idempotentes.<br/>"
        "• <b>Ciberseguridad:</b> Mitigación OWASP Top 10 (SQLi, CSRF), Ley 21.459 (auditoría inmutable de evidencias) y Ley 19.628 (protección de datos de vecinos).",
        st['body']
    ))
    story.append(Paragraph("<b>Speech de Cierre:</b>", st['h2']))
    story.append(Paragraph(
        "<i>'Profesor y comisión: hemos demostrado que nuestro wireframe es el plano de ingeniería de un sistema real, seguro y validado en producción. Cumplimos el 100% de los criterios exigidos. Muchas gracias.'</i>",
        st['speech']
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Compilado: {filename}")


# ==============================================================================
# 2. GENERAR GUIA_DEFENSA_MOCKUP_Y_FUTURA_CONSTRUCCION.pdf
# ==============================================================================
def generar_pdf_guia_defensa():
    filename = "GUIA_DEFENSA_MOCKUP_Y_FUTURA_CONSTRUCCION.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=2*cm, rightMargin=2*cm, topMargin=2.5*cm, bottomMargin=2.5*cm)
    st = get_custom_styles()
    story = []

    # Portada
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("INACAP — ÁREA INFORMÁTICA Y CIBERSEGURIDAD", ParagraphStyle('G1', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1, textColor=colors.HexColor("#6c757d"))))
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("GUÍA MAESTRA DE DEFENSA", ParagraphStyle('G2', fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, textColor=colors.HexColor("#1A252F"))))
    story.append(Paragraph("Cómo Presentar el Mockup Interactivo y Defender su Construcción Futura", st['cover_t']))
    story.append(Paragraph("Evaluación Sumativa N° 3 — Ingeniería de Software (TI2043)", st['cover_sub']))
    story.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor("#AD0000"), spaceBefore=5, spaceAfter=20))

    story.append(Paragraph("1. ¿Qué Significa Defender su Construcción Futura?", st['h1']))
    story.append(Paragraph(
        "Defender la construcción futura significa justificar técnicamente por qué el mockup no es un simple dibujo, "
        "sino un plano de software viable que se conecta con la base de datos MySQL, la lógica de Django, las normas "
        "de ciberseguridad OWASP y la infraestructura en la nube de AWS EC2.",
        st['body']
    ))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("2. Recorrido Paso a Paso en /wireframes/ (5 Pantallas Clave)", st['h1']))
    
    pasos = [
        [Paragraph("<b>Paso</b>", st['body']), Paragraph("<b>Pantalla en Wireframe</b>", st['body']), Paragraph("<b>Cómo Defender la Construcción Futura</b>", st['body'])],
        [Paragraph("1", st['body']), Paragraph("Acceso y Recuperación", st['body']), Paragraph("Hashing PBKDF2 en Django y token seguro de 1 solo uso con expiración de 15 min.", st['body'])],
        [Paragraph("2", st['body']), Paragraph("Dashboard Multirrol", st['body']), Paragraph("Control RBAC: Si es Supervisor, el ORM filtra estrictamente por su delegación.", st['body'])],
        [Paragraph("3", st['body']), Paragraph("Formulario de Atención", st['body']), Paragraph("Llamada AJAX asíncrona al ingresar RUT, autocompletando datos en <900 ms.", st['body'])],
        [Paragraph("4", st['body']), Paragraph("Tablero Kanban Tubo", st['body']), Paragraph("Máquina de estados en modelo Compromiso con sincronización a la Actividad.", st['body'])],
        [Paragraph("5", st['body']), Paragraph("Semáforo de Metas", st['body']), Paragraph("Fórmula matemática que pondera solo evidencias aprobadas (máximo 100%).", st['body'])],
    ]
    t_pasos = Table(pasos, colWidths=[1.5 * cm, 4.5 * cm, 9.5 * cm])
    t_pasos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#AD0000")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dee2e6")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_pasos)

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("3. El Golpe Maestro de la Defensa", st['h1']))
    story.append(Paragraph(
        "Al minuto 6 de tu exposición, abres la pestaña de la aplicación real en Django (http://localhost:8000/) y dices: "
        "<i>'Profesor, nosotros fuimos más allá de la teoría: construimos, probamos y desplegamos el sistema real para validar empíricamente que cada mockup es 100% funcional.'</i>",
        st['body']
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Compilado: {filename}")


# ==============================================================================
# 3. GENERAR GUIA_EXPLICATIVA_EVALUACION_4.pdf
# ==============================================================================
def generar_pdf_guia_eva4():
    filename = "GUIA_EXPLICATIVA_EVALUACION_4.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=2*cm, rightMargin=2*cm, topMargin=2.5*cm, bottomMargin=2.5*cm)
    st = get_custom_styles()
    story = []

    # Portada
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("INACAP — PROGRAMACIÓN BACK END (TI3V41)", ParagraphStyle('E1', fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1, textColor=colors.HexColor("#6c757d"))))
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("GUÍA EXPLICATIVA DEFINITIVA", ParagraphStyle('E2', fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, textColor=colors.HexColor("#1A252F"))))
    story.append(Paragraph("Entendiendo la API RESTful, JWT, Swagger y el SGR desde Cero", st['cover_t']))
    story.append(Paragraph("Evaluación Sumativa N° 4 — Docente Alex Díaz Araos", st['cover_sub']))
    story.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor("#AD0000"), spaceBefore=5, spaceAfter=20))

    story.append(Paragraph("1. ¿Qué es lo que Había que Hacer?", st['h1']))
    story.append(Paragraph(
        "Convertir el sistema web de Django en un <b>proveedor de datos puros (formato JSON)</b> mediante una API RESTful, "
        "para que aplicaciones móviles (celulares de los funcionarios en terreno) o sistemas externos puedan consultar y guardar datos.",
        st['body']
    ))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("2. Los 3 Conceptos Clave en Palabras Simples", st['h1']))
    story.append(Paragraph(
        "• <b>API RESTful (El Mozo del Restaurante):</b> El cliente hace pedidos al mozo (GET para leer, POST para crear, PUT para editar, DELETE para borrar) y el mozo responde con datos JSON.<br/>"
        "• <b>Token JWT (La Pulsera VIP del Festival):</b> Muestras tus credenciales en /api/token/ una sola vez y recibes un token cifrado. A partir de ese momento solo presentas tu token en cada petición.<br/>"
        "• <b>Swagger UI (El Catálogo de Pruebas):</b> Página web en /api/swagger/ que te permite probar todos los botones de la API directamente desde el navegador.",
        st['body']
    ))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("3. Serializadores Diferenciados (Ley 19.628 de Protección de Datos)", st['h1']))
    story.append(Paragraph(
        "El profesor exigió que los datos sensibles se protejan según el perfil del usuario:<br/>"
        "• <b>Administrador:</b> Ve los datos reales (RUT 15.987.654-3, teléfono +56912345678, correo y notas de auditoría).<br/>"
        "• <b>Operador / Funcionario Normal:</b> El sistema automáticamente enmascara los datos sensibles (RUT 15.***.***-3, teléfono +56 9 ****-****, correo c****@gmail.com).",
        st['body']
    ))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("4. Cómo Probar la API en 3 Pasos", st['h1']))
    story.append(Paragraph(
        "1. Ve a <code>http://localhost:8000/api/token/</code> con usuario <code>admin</code> y clave <code>admin</code> para obtener tu token.<br/>"
        "2. Ve a <code>http://localhost:8000/api/swagger/</code> y haz clic en el botón verde <b>Authorize</b> para pegar el token.<br/>"
        "3. Haz clic en <code>GET /api/v1/delegaciones/</code> y pulsa <b>Execute</b> para ver la respuesta 200 OK con los datos de MySQL.",
        st['body']
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Compilado: {filename}")


if __name__ == '__main__':
    generar_pdf_presentacion()
    generar_pdf_guia_defensa()
    generar_pdf_guia_eva4()
