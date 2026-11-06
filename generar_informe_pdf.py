"""
Script para compilar el Informe Técnico Formal del SGR a formato PDF profesional
utilizando ReportLab (instalado en el entorno virtual).
Incluye el Diagrama Oficial del Modelo Entidad-Relación (MER.png) embebido en alta calidad.
Genera: INFORME_TECNICO_SGR_EVALUACION_3.pdf y README.pdf
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
            # En la portada no se dibujan encabezados ni números de página
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6c757d"))

        # Encabezado superior
        self.drawString(
            2 * cm, 26.5 * cm,
            "INACAP La Serena — TI3041 Programación Back End | Sistema de Gestión de Resultados (SGR)"
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
            "Ilustre Municipalidad de La Serena · Evaluación Sumativa N°3 · Noviembre 2026"
        )
        page_text = f"Página {self._pageNumber} de {total_pages}"
        self.drawRightString(19.5 * cm, 1.5 * cm, page_text)
        self.restoreState()


def generar_informe_pdf(output_filename="INFORME_TECNICO_SGR_EVALUACION_3.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    # Estilos tipográficos institucionales
    c_rojo = colors.HexColor("#AD0000")
    c_gris_oscuro = colors.HexColor("#212529")
    c_fondo_tabla = colors.HexColor("#f8f9fa")

    style_portada_inst = ParagraphStyle(
        'PortadaInst',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_rojo,
        alignment=1,
    )
    style_portada_sub = ParagraphStyle(
        'PortadaSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#495057"),
        alignment=1,
    )
    style_portada_titulo = ParagraphStyle(
        'PortadaTitulo',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=28,
        textColor=c_rojo,
        alignment=1,
    )
    style_portada_desc = ParagraphStyle(
        'PortadaDesc',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        textColor=c_gris_oscuro,
        alignment=1,
    )

    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_rojo,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True,
    )
    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#495057"),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True,
    )
    style_body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_gris_oscuro,
        spaceBefore=2.5,
        spaceAfter=2.5,
    )
    style_caption = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#6c757d"),
        alignment=1,
        spaceBefore=4,
        spaceAfter=8,
    )
    style_callout = ParagraphStyle(
        'Callout',
        parent=style_body,
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#084298"),
        backColor=colors.HexColor("#cfe2ff"),
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=5,
    )
    style_th = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1,
    )
    style_td = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=c_gris_oscuro,
    )
    style_td_code = ParagraphStyle(
        'TDCode',
        parent=style_td,
        fontName='Courier-Bold',
        textColor=c_rojo,
    )

    story = []

    # =========================================================================
    # PÁGINA 1: PORTADA FORMAL INACAP
    # =========================================================================
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("UNIVERSIDAD TECNOLÓGICA DE CHILE INACAP", style_portada_inst))
    story.append(Paragraph("SEDE LA SERENA · ÁREA INFORMÁTICA, CIBERSEGURIDAD Y TELECOMUNICACIONES", style_portada_sub))
    story.append(Paragraph("CARRERA: INGENIERÍA EN INFORMÁTICA / ANALISTA PROGRAMADOR", style_portada_sub))
    story.append(Spacer(1, 1.2 * cm))

    story.append(HRFlowable(width="100%", thickness=3, color=c_rojo, spaceAfter=20, spaceBefore=0))
    story.append(Paragraph("INFORME TÉCNICO DE PROYECTO Y DESPLIEGUE EN LA NUBE", style_portada_desc))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("SISTEMA DE GESTIÓN DE RESULTADOS (SGR)", style_portada_titulo))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("ILUSTRE MUNICIPALIDAD DE LA SERENA", style_portada_desc))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#ced4da"), spaceAfter=20, spaceBefore=15))

    story.append(Paragraph("<b>Evaluación Sumativa N°3 (30%) — Aplicación Web con CRUD y Perfiles de Acceso</b>", style_portada_desc))
    story.append(Paragraph("Asignatura: Programación Back End (TI3041) · Docentes: Mariavictoria Freites Ayala / Alex Díaz Araos", style_portada_sub))
    story.append(Spacer(1, 1.8 * cm))

    # Tabla de Integrantes en Portada
    datos_portada = [
        [Paragraph("<b>INTEGRANTES DEL EQUIPO</b>", style_th), Paragraph("<b>ROL EN EL PROYECTO</b>", style_th)],
        [Paragraph("<b>Emanuel Román Serón</b>", style_td), Paragraph("Seguridad RBAC, SMTP Gmail, Despliegue AWS EC2 y QA", style_td)],
        [Paragraph("<b>Benjamín Antipa</b>", style_td), Paragraph("Vistas, Dashboards Dinámicos, APIs y Formularios", style_td)],
        [Paragraph("<b>Álvaro Obregón</b>", style_td), Paragraph("Modelado ORM, Persistencia MySQL y Exportación Excel", style_td)],
    ]
    t_portada = Table(datos_portada, colWidths=[8 * cm, 9.5 * cm])
    t_portada.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_rojo),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_fondo_tabla]),
    ]))
    story.append(t_portada)

    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("<b>Entorno de Producción:</b> http://3.229.11.31:8000/ · <b>Repositorio GitHub:</b> https://github.com/iScreamyy6/Backend", style_portada_sub))
    story.append(Paragraph("La Serena, Chile — Noviembre de 2026", style_portada_sub))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: RESUMEN EJECUTIVO Y FICHA TÉCNICA
    # =========================================================================
    story.append(Paragraph("RESUMEN EJECUTIVO (ABSTRACT)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_rojo, spaceAfter=8, spaceBefore=2))
    story.append(Paragraph(
        "El <b>Sistema de Gestión de Resultados (SGR)</b> es una plataforma web desarrollada en el framework <b>Django</b> "
        "con base de datos relacional <b>MySQL 8.x</b> y desplegada en la nube de <b>Amazon Web Services (AWS EC2)</b>. "
        "Fue concebida para la Ilustre Municipalidad de La Serena con el objetivo de modernizar, digitalizar y centralizar "
        "los procesos de atención ciudadana, operativos en terreno, seguimiento de compromisos en un tablero Kanban y medición "
        "del cumplimiento de metas en las delegaciones territoriales de Las Compañías, La Antena, Centro y Rural.",
        style_body
    ))
    story.append(Paragraph(
        "Este informe técnico consolida los requerimientos y resultados de la <b>Evaluación Sumativa N°3</b>, destacando la "
        "implementación de una arquitectura de seguridad por roles (RBAC) con 3 niveles mediante <b>Grupos y Permisos nativos de Django</b> "
        "(<code>Administrador</code>, <code>Supervisor</code>, <code>Administrativo</code>), recuperación de claves por correo real vía "
        "<b>Gmail SMTP con código PIN de 6 dígitos y token criptográfico HMAC-SHA256</b>, dashboards dinámicos adaptados al perfil, "
        "unificación de atenciones en el Módulo de Gestiones con correlativos automáticos (<code>GES-XXXXX</code>, <code>SOC-XXXXX</code>, "
        "<code>TUB-XXXXX</code>), asignación de cuentas institucionales <code>@correo.cl</code>, filtro estricto de privacidad para operadores, "
        "el <b>Modelo Entidad-Relación (MER)</b> oficial y un arnés de pruebas automatizadas idempotente verificado al 100% de efectividad.",
        style_body
    ))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("FICHA TÉCNICA DEL SISTEMA", style_h2))

    ficha_datos = [
        [Paragraph("<b>Componente</b>", style_th), Paragraph("<b>Especificación Técnica</b>", style_th), Paragraph("<b>Estado</b>", style_th)],
        [Paragraph("Framework Web", style_td), Paragraph("Django 5.1+ / 6.0 (Python 3.10+ / 3.14 / 3.12 Ubuntu)", style_td), Paragraph("Operativo", style_td_code)],
        [Paragraph("Base de Datos", style_td), Paragraph("MySQL Server 8.0 (Producción) / SQLite (Desarrollo)", style_td), Paragraph("Operativo", style_td_code)],
        [Paragraph("Infraestructura Cloud", style_td), Paragraph("Amazon EC2 t2.micro — Ubuntu 24.04 LTS (3.229.11.31:8000)", style_td), Paragraph("En Producción", style_td_code)],
        [Paragraph("Seguridad & RBAC", style_td), Paragraph("3 Grupos Django (auth_group) + 9 Roles Institucionales", style_td), Paragraph("Operativo", style_td_code)],
        [Paragraph("Servicio de Correo", style_td), Paragraph("Gmail SMTP TLS Puerto 587 (emanuelromanseron@gmail.com)", style_td), Paragraph("Operativo", style_td_code)],
        [Paragraph("Recuperación Claves", style_td), Paragraph("PIN numérico de 6 dígitos + Token HMAC-SHA256 de un solo uso", style_td), Paragraph("Operativo", style_td_code)],
        [Paragraph("Suite de Pruebas", style_td), Paragraph("test_suite.py (14 secciones) + test_personal_filter.py (100% pass)", style_td), Paragraph("Aprobado 100%", style_td_code)],
        [Paragraph("Archivos Estáticos", style_td), Paragraph("WhiteNoise Middleware con compresión Gzip en AWS EC2", style_td), Paragraph("Operativo", style_td_code)],
    ]
    t_ficha = Table(ficha_datos, colWidths=[4 * cm, 10.5 * cm, 3 * cm])
    t_ficha.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#343a40")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#ced4da")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_fondo_tabla]),
    ]))
    story.append(t_ficha)

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("1. ARQUITECTURA DE SEGURIDAD Y CONTROL DE ACCESO (RBAC)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_rojo, spaceAfter=8, spaceBefore=2))
    story.append(Paragraph(
        "Se implementó una <b>arquitectura de seguridad de doble capa</b> que separa las autorizaciones técnicas de los cargos institucionales:<br/>"
        "• <b>Capa Técnica (Grupos de Django <code>auth.Group</code>):</b> <code>Administrador</code> (80 permisos), "
        "<code>Supervisor</code> (41 permisos) y <code>Administrativo</code> (14 permisos). Determina las acciones CRUD sobre la base de datos.<br/>"
        "• <b>Capa Institucional (Roles Municipales <code>organizacion.Rol</code>):</b> Asigna el cargo funcional del empleado "
        "(<code>Delegado Municipal</code>, <code>Gestor Social</code>, <code>Territorial OO.CC.</code>, <code>DISERCO</code>) "
        "para condicionar las clasificaciones temáticas que puede registrar y la presentación de su panel operativo.",
        style_body
    ))

    # Tabla de Matriz de Perfiles
    datos_perfiles = [
        [Paragraph("<b>Grupo Django</b>", style_th), Paragraph("<b>Permisos</b>", style_th), Paragraph("<b>Alcance Territorial</b>", style_th), Paragraph("<b>Capacidades Funcionales</b>", style_th)],
        [Paragraph("<b>Administrador</b>", style_td), Paragraph("80 permisos", style_td), Paragraph("Comunal Global", style_td), Paragraph("Acceso irrestricto a los 6 CRUDs, creación/edición de usuarios, asignación de grupos Django, auditoría y reportes alcaldicios.", style_td)],
        [Paragraph("<b>Supervisor</b>", style_td), Paragraph("41 permisos", style_td), Paragraph("Comunal o Delegación", style_td), Paragraph("Supervisión de metas SGR, semáforo de cumplimiento, monitoreo del Kanban comunal. Bloqueado de administrar usuarios.", style_td)],
        [Paragraph("<b>Administrativo</b>", style_td), Paragraph("14 permisos", style_td), Paragraph("Delegación Asignada", style_td), Paragraph("Registro de gestiones de ventanilla y terreno, carga de evidencias fotográficas, filtro de gestiones propias.", style_td)],
    ]
    t_perfiles = Table(datos_perfiles, colWidths=[3.2 * cm, 2.2 * cm, 3.6 * cm, 8.5 * cm])
    t_perfiles.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_rojo),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#ced4da")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_fondo_tabla]),
    ]))
    story.append(t_perfiles)

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: MODELO ENTIDAD-RELACIÓN (MER) OFICIAL
    # =========================================================================
    story.append(Paragraph("2. MODELO ENTIDAD-RELACIÓN (MER) OFICIAL DEL PROYECTO", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_rojo, spaceAfter=8, spaceBefore=2))
    story.append(Paragraph(
        "El modelo relacional del SGR fue diseñado y normalizado en tercera forma normal (3NF) mediante <b>MySQL Workbench</b> "
        "(archivo fuente editable <code>Contexto de la problematica/02_Modelamiento_y_Diseno/Diagramas/modelo-sgr-MER.mwb</code>) "
        "y trasladado fielmente a la persistencia en MySQL 8.x mediante el ORM de Django.",
        style_body
    ))
    story.append(Paragraph(
        "A continuación se presenta el <b>Diagrama MER Oficial en Alta Resolución</b> que describe la totalidad de tablas maestras, "
        "entidades transaccionales, llaves foráneas y cardinalidades del sistema municipal:",
        style_body
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Incrustación de la imagen oficial del MER
    mer_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "img", "MER.png")
    if os.path.exists(mer_img_path):
        # 13.5 cm de ancho por 17.6 cm de alto preserva el aspect ratio 869x1134
        mer_flowable = Image(mer_img_path, width=13.5 * cm, height=17.6 * cm)
        mer_flowable.hAlign = 'CENTER'
        story.append(mer_flowable)
        story.append(Paragraph(
            "<i>Figura 2.1: Diagrama Oficial del Modelo Entidad-Relación (MER) — Sistema SGR Ilustre Municipalidad de La Serena.</i>",
            style_caption
        ))
    else:
        story.append(Paragraph("<b>[Aviso: Archivo MER.png no encontrado en static/img/]</b>", style_callout))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 4: RECUPERACIÓN DE CONTRASEÑA Y MÓDULOS DE NEGOCIO
    # =========================================================================
    story.append(Paragraph("3. RECUPERACIÓN SEGURA DE CONTRASEÑAS POR CORREO (SMTP)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_rojo, spaceAfter=8, spaceBefore=2))
    story.append(Paragraph(
        "El módulo de autenticación implementa un flujo bancario de alta seguridad para el restablecimiento de contraseñas olvidadas, "
        "integrando el servidor SMTP real de Google (<code>smtp.gmail.com</code> puerto TLS 587):",
        style_body
    ))
    story.append(Paragraph(
        "1. <b>Solicitud sin Pistas (<code>/recuperar/</code>):</b> El usuario ingresa su correo. El servidor genera un <b>PIN numérico de 6 dígitos</b> "
        "y un <b>token criptográfico HMAC-SHA256</b> (<code>default_token_generator</code>), despachando el mensaje por correo real.<br/>"
        "2. <b>Pantalla de 6 Casilleros (<code>/recuperar/validar/</code>):</b> Interfaz con auto-avance numérico y validación de vigencia (15 minutos) "
        "con protección contra ataques de fuerza bruta (bloqueo automático tras 3 intentos erróneos).<br/>"
        "3. <b>Restablecimiento e Invalidación Inmediata (<code>/recuperar/nueva-clave/</code>):</b> Al guardar la nueva contraseña, "
        "el token y el PIN se invalidan de forma permanente, impidiendo su reutilización.",
        style_body
    ))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("4. MÓDULOS OPERACIONALES: GESTIONES, TUBO KANBAN Y PRIVACIDAD", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_rojo, spaceAfter=8, spaceBefore=2))
    story.append(Paragraph(
        "• <b>Módulo Unificado de Gestiones (<code>/actividades/</code>):</b> Reúne en un único modelo relacional (<code>Actividad</code>) "
        "todas las solicitudes de ventanilla, operativos comunitarios y casos sociales con folios correlativos únicos (<code>GES-XXXXX</code>, <code>SOC-XXXXX</code>). "
        "Incorpora autocompletado de vecinos por RUT vía AJAX.<br/>"
        "• <b>Tubo de Trabajo y Tablero Kanban (<code>/agenda/resumen/</code>):</b> Monitorea compromisos derivados en 4 columnas de flujo "
        "(<code>INGRESADO</code>, <code>PENDIENTE</code>, <code>EN PROCESO</code>, <code>REALIZADO</code>) con detección automática de compromisos atrasados.<br/>"
        "• <b>Filtro de Privacidad y Gestiones Personales:</b> Los usuarios con perfil <code>Administrativo</code> visualizan exclusivamente "
        "sus 3 gestiones asignadas por funcionario o creador, preservando la confidencialidad de los casos sociales.<br/>"
        "• <b>Selector Comunal ('Todas las Delegaciones'):</b> Permite a supervisores y administradores alternar entre una delegación específica o la vista comunal consolidada.",
        style_body
    ))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("5. MATRIZ DE CUENTAS OFICIALES Y CREDENCIALES DE DEMOSTRACIÓN", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_rojo, spaceAfter=8, spaceBefore=2))
    story.append(Paragraph(
        "Todas las cuentas de usuario fueron sincronizadas con los nombres de sus funcionarios "
        "y su dominio oficial <code>@correo.cl</code> (todas con clave inicial <code>admin</code>):",
        style_body
    ))

    datos_cuentas = [
        [Paragraph("<b>Funcionario</b>", style_th), Paragraph("<b>Cargo / Rol</b>", style_th), Paragraph("<b>Perfil Django</b>", style_th), Paragraph("<b>Usuario</b>", style_th), Paragraph("<b>Correo Institucional</b>", style_th), Paragraph("<b>Delegación</b>", style_th)],
        [Paragraph("<b>Acuaman</b>", style_td), Paragraph("Territorial OO.CC. 1", style_td), Paragraph("Administrativo", style_td), Paragraph("acuaman", style_td_code), Paragraph("acuaman@correo.cl", style_td), Paragraph("[D02] La Antena", style_td)],
        [Paragraph("<b>Flash</b>", style_td), Paragraph("Gestor Social 1", style_td), Paragraph("Administrativo", style_td), Paragraph("flash", style_td_code), Paragraph("flash@correo.cl", style_td), Paragraph("[D01] Las Compañías", style_td)],
        [Paragraph("<b>He-Man</b>", style_td), Paragraph("Delegado Municipal", style_td), Paragraph("Supervisor", style_td), Paragraph("heman", style_td_code), Paragraph("heman@correo.cl", style_td), Paragraph("[D01] Las Compañías", style_td)],
        [Paragraph("<b>Capitana Marvel</b>", style_td), Paragraph("Coordinador DISERCO", style_td), Paragraph("Administrativo", style_td), Paragraph("capitanamarvel", style_td_code), Paragraph("capitanamarvel@correo.cl", style_td), Paragraph("[D04] Rural", style_td)],
        [Paragraph("<b>Spider-Man</b>", style_td), Paragraph("Territorial OO.CC. 2", style_td), Paragraph("Administrativo", style_td), Paragraph("spiderman", style_td_code), Paragraph("spiderman@correo.cl", style_td), Paragraph("[D01] Las Compañías", style_td)],
        [Paragraph("<b>Capitán América</b>", style_td), Paragraph("Gestor Social 2", style_td), Paragraph("Administrativo", style_td), Paragraph("capitanamerica", style_td_code), Paragraph("capitanamerica@correo.cl", style_td), Paragraph("[D02] La Antena", style_td)],
        [Paragraph("<b>Pantera Negra</b>", style_td), Paragraph("Prof. Planificación", style_td), Paragraph("Administrativo", style_td), Paragraph("panteranegra", style_td_code), Paragraph("panteranegra@correo.cl", style_td), Paragraph("[D03] Centro", style_td)],
        [Paragraph("<b>Hulk</b>", style_td), Paragraph("Gestor Social 3", style_td), Paragraph("Administrativo", style_td), Paragraph("hulk", style_td_code), Paragraph("hulk@correo.cl", style_td), Paragraph("[D03] Centro", style_td)],
        [Paragraph("<b>Coordinador</b>", style_td), Paragraph("Coordinador Comunal", style_td), Paragraph("Supervisor", style_td), Paragraph("coordinador", style_td_code), Paragraph("coordinador@correo.cl", style_td), Paragraph("[COMUNAL] Todas", style_td)],
        [Paragraph("<b>Administrador</b>", style_td), Paragraph("Administrador General", style_td), Paragraph("Administrador", style_td), Paragraph("admin", style_td_code), Paragraph("emanuelseron2003@gmail.com", style_td), Paragraph("[COMUNAL] Todas", style_td)],
    ]
    t_cuentas = Table(datos_cuentas, colWidths=[2.8 * cm, 3.2 * cm, 2.5 * cm, 2.4 * cm, 4 * cm, 2.6 * cm])
    t_cuentas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_rojo),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#ced4da")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_fondo_tabla]),
    ]))
    story.append(t_cuentas)

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 5: DESPLIEGUE AWS, QA Y CONCLUSIONES
    # =========================================================================
    story.append(Paragraph("6. DESPLIEGUE EN LA NUBE (AWS EC2) Y PRUEBAS AUTOMATIZADAS", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_rojo, spaceAfter=8, spaceBefore=2))
    story.append(Paragraph(
        "• <b>Infraestructura Cloud:</b> Instancia Amazon EC2 <code>t2.micro</code> (Ubuntu Server 24.04 LTS) en IP pública <code>3.229.11.31:8000</code>. "
        "Base de datos MySQL Server 8.0, servicio administrado bajo <code>systemd</code> (<code>sgr-django.service</code>) y WhiteNoise para estáticos.<br/>"
        "• <b>Suite Oficial de Pruebas (<code>test_suite.py</code>):</b> Arnés automatizado de 14 secciones que valida autenticación, los 6 mantenedores CRUD, "
        "exportación a Excel, flujo de recuperación por correo real, dashboards diferenciados y restricciones por URL. "
        "<b>Ejecuta con 100% de éxito de manera idempotente</b>, conservando exactamente la base de datos limpia con sus 24 gestiones baseline (3 por funcionario).",
        style_body
    ))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("7. CASOS DE USO DE INTELIGENCIA ARTIFICIAL EN EL DESARROLLO", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_rojo, spaceAfter=8, spaceBefore=2))

    datos_ia = [
        [Paragraph("<b>Caso Técnico</b>", style_th), Paragraph("<b>Problema / Requerimiento</b>", style_th), Paragraph("<b>Aporte de la IA y Solución Implementada</b>", style_th)],
        [Paragraph("Seguridad RBAC desacoplada", style_td), Paragraph("Rúbrica docente exigía Grupos Django nativos mientras el negocio requería 9 cargos municipales.", style_td), Paragraph("Diseñó la arquitectura de doble capa vinculando Grupos de Django (auth_group) con Roles (organizacion.Rol).", style_td)],
        [Paragraph("Recuperación SMTP híbrida", style_td), Paragraph("Integración de pantalla de 6 casilleros interactiva con seguridad anti fuerza bruta.", style_td), Paragraph("Estructuró sesión temporal de 15 minutos, límite de 3 intentos y token criptográfico HMAC-SHA256 de consumo único.", style_td)],
        [Paragraph("Idempotencia de pruebas", style_td), Paragraph("Ejecución reiterada de test_suite acumulaba registros transaccionales repetidos.", style_td), Paragraph("Diseñó bloques de limpieza previa y posterior garantizando cero residuos y 24 gestiones baseline exactas.", style_td)],
    ]
    t_ia = Table(datos_ia, colWidths=[4 * cm, 6 * cm, 7.5 * cm])
    t_ia.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#495057")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#ced4da")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_fondo_tabla]),
    ]))
    story.append(t_ia)

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("8. CONCLUSIONES", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_rojo, spaceAfter=8, spaceBefore=2))
    story.append(Paragraph(
        "El desarrollo del <b>Sistema de Gestión de Resultados (SGR)</b> cumplió satisfactoriamente con la totalidad de los criterios "
        "establecidos en la pauta de la Evaluación Sumativa N°3 de Programación Back End. La solución implementada no solo satisface los "
        "requerimientos académicos, sino que constituye una herramienta de software lista para producción institucional, "
        "con segregación de privilegios efectiva, recuperación de contraseñas robusta, persistencia relacional íntegra y despliegue cloud en AWS.",
        style_body
    ))

    story.append(Spacer(1, 0.3 * cm))
    callout_enlaces = (
        "<b>Puntos de Acceso en Producción (AWS EC2 Cloud):</b><br/>"
        "• <b>Portal SGR en Vivo:</b> http://3.229.11.31:8000/<br/>"
        "• <b>Inicio de Sesión:</b> http://3.229.11.31:8000/login/<br/>"
        "• <b>Recuperación de Contraseña:</b> http://3.229.11.31:8000/recuperar/<br/>"
        "• <b>Repositorio Oficial de Código:</b> https://github.com/iScreamyy6/Backend"
    )
    story.append(Paragraph(callout_enlaces, style_callout))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Documento PDF generado exitosamente: {output_filename}")


if __name__ == "__main__":
    generar_informe_pdf("INFORME_TECNICO_SGR_EVALUACION_3.pdf")
    generar_informe_pdf("README.pdf")
