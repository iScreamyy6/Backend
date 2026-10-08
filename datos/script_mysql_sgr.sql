-- ==============================================================================
-- PROYECTO: Sistema de Gestión de Resultados (SGR) — Ilustre Municipalidad de La Serena
-- ARTEFACTO: Script DDL/DML para MySQL (Ingeniería Inversa en MySQL Workbench)
-- EVALUACIÓN: Segunda Evaluación (Eva 2) — Modelo Relacional y MER
-- MOTOR: InnoDB | CHARSET: utf8mb4 | COLLATION: utf8mb4_unicode_ci
-- ==============================================================================

-- 1. CREACIÓN Y SELECCIÓN DE BASE DE DATOS
DROP DATABASE IF EXISTS sgr_municipalidad;
CREATE DATABASE sgr_municipalidad 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE sgr_municipalidad;

-- Desactivar temporalmente revisión de claves foráneas para creación limpia
SET FOREIGN_KEY_CHECKS = 0;

-- ==============================================================================
-- 2. TABLAS DEL MÓDULO ORGANIZACIÓN (EP-08)
-- ==============================================================================

-- Tabla: Delegaciones Municipales
DROP TABLE IF EXISTS delegaciones;
CREATE TABLE delegaciones (
    id_delegacion INT AUTO_INCREMENT COMMENT 'Identificador único de la delegación',
    nombre VARCHAR(200) NOT NULL UNIQUE COMMENT 'Nombre formal (ej: Delegación Las Compañías)',
    ambito VARCHAR(150) NOT NULL COMMENT 'Sector territorial geográfico',
    responsable VARCHAR(200) NOT NULL COMMENT 'Delegado o jefatura a cargo',
    foco_estrategico TEXT NULL COMMENT 'Misión prioritaria del sector',
    estado ENUM('Activa', 'Inactiva') NOT NULL DEFAULT 'Activa' COMMENT 'Estado operativo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de alta en el sistema',
    PRIMARY KEY (id_delegacion)
) ENGINE=InnoDB COMMENT='Unidades territoriales descentralizadas del municipio';

-- Tabla: Funcionarios Municipales
DROP TABLE IF EXISTS funcionarios;
CREATE TABLE funcionarios (
    id_funcionario INT AUTO_INCREMENT COMMENT 'Identificador único del funcionario',
    id_delegacion INT NOT NULL COMMENT 'Delegación a la que está adscrito',
    nombre VARCHAR(200) NOT NULL COMMENT 'Nombre completo del funcionario',
    cargo VARCHAR(150) NOT NULL COMMENT 'Cargo funcional (ej: Gestor Social, Territorial)',
    activo TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1 = Activo, 0 = Inactivo/Licencia',
    fecha_ingreso DATE NULL COMMENT 'Fecha de incorporación al municipio',
    PRIMARY KEY (id_funcionario),
    INDEX idx_funcionario_delegacion (id_delegacion),
    CONSTRAINT fk_funcionarios_delegaciones
        FOREIGN KEY (id_delegacion)
        REFERENCES delegaciones (id_delegacion)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Nómina de personal sujeto a evaluación por metas';

-- ==============================================================================
-- 3. TABLAS DEL MÓDULO ACTIVIDADES Y EVIDENCIAS (EP-01, EP-03)
-- ==============================================================================

-- Tabla: Registro de Actividades / Gestiones en Terreno
DROP TABLE IF EXISTS actividades;
CREATE TABLE actividades (
    id_actividad INT AUTO_INCREMENT COMMENT 'Identificador único de la gestión',
    id_funcionario INT NOT NULL COMMENT 'Funcionario que ejecutó la gestión',
    fecha DATE NOT NULL COMMENT 'Fecha en que se llevó a cabo la acción',
    solicitud TEXT NOT NULL COMMENT 'Problema o requerimiento vecinal planteado',
    accion VARCHAR(300) NOT NULL COMMENT 'Acción resolutiva o gestión realizada',
    responsable VARCHAR(200) NOT NULL COMMENT 'Nombre del responsable en terreno',
    item_evaluacion VARCHAR(200) NOT NULL COMMENT 'Ítem de ponderación de la meta del cargo',
    estado ENUM('Pendiente', 'En Proceso', 'Realizado') NOT NULL DEFAULT 'Pendiente',
    contacto VARCHAR(200) NULL COMMENT 'Nombre del vecino o dirigente requirente',
    telefono VARCHAR(30) NULL COMMENT 'Teléfono de contacto para trazabilidad',
    ingreso_tubo TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 = Requiere seguimiento en Tubo de Trabajo',
    codigo_evidencia VARCHAR(50) UNIQUE NULL COMMENT 'Código único correlativo de evidencia',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_actividad),
    INDEX idx_actividades_funcionario (id_funcionario),
    INDEX idx_actividades_fecha (fecha),
    CONSTRAINT fk_actividades_funcionarios
        FOREIGN KEY (id_funcionario)
        REFERENCES funcionarios (id_funcionario)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Libro de gestiones diarias y atención de requerimientos ciudadanos';

-- Tabla: Evidencias Fotográficas y Verificación Técnica
DROP TABLE IF EXISTS evidencias;
CREATE TABLE evidencias (
    id_evidencia INT AUTO_INCREMENT COMMENT 'Identificador de la evidencia',
    id_actividad INT NOT NULL COMMENT 'Actividad vinculada que respalda',
    codigo VARCHAR(50) NOT NULL UNIQUE COMMENT 'Código verificador oficial (EVI-2026-XXXX)',
    archivo_ruta VARCHAR(255) NOT NULL COMMENT 'Nombre o ruta del archivo/fotografía de respaldo',
    imagen_verificada TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Checklist: Foto auténtica y legible',
    verificador_valido TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Checklist: Código coincidente con planilla',
    resultado INT NOT NULL DEFAULT 0 COMMENT '1 = Aporta a meta, 0 = No computable',
    estado_validacion ENUM('Pendiente', 'Aprobada', 'Rechazada', 'Corregir') NOT NULL DEFAULT 'Pendiente',
    observacion TEXT NULL COMMENT 'Observaciones del verificador/auditor técnico',
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_evidencia),
    INDEX idx_evidencias_actividad (id_actividad),
    CONSTRAINT fk_evidencias_actividades
        FOREIGN KEY (id_actividad)
        REFERENCES actividades (id_actividad)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Auditoría fotográfica para validar cumplimiento de gestiones';

-- ==============================================================================
-- 4. TABLAS DEL MÓDULO AGENDA COLECTIVA (TUBO DE TRABAJO - EP-04)
-- ==============================================================================

-- Tabla: Compromisos del Tubo de Trabajo
DROP TABLE IF EXISTS compromisos_tubo;
CREATE TABLE compromisos_tubo (
    id_compromiso INT AUTO_INCREMENT COMMENT 'Identificador del compromiso',
    id_delegacion INT NOT NULL COMMENT 'Delegación asignada para el cumplimiento',
    id_responsable INT NULL COMMENT 'Funcionario asignado directamente (opcional)',
    fecha_solicitud DATE NOT NULL COMMENT 'Fecha de ingreso al tubo',
    actividad TEXT NOT NULL COMMENT 'Compromiso específico adquirido',
    tipo ENUM('INT', 'EXT') NOT NULL DEFAULT 'EXT' COMMENT 'INT: Interno municipal, EXT: Externo ciudadano',
    solicitante VARCHAR(200) NOT NULL COMMENT 'Organización vecinal o entidad requirente',
    territorio VARCHAR(200) NULL COMMENT 'Barrio, pasaje o sector territorial',
    responsable VARCHAR(200) NOT NULL COMMENT 'Nombre del funcionario o área a cargo',
    fecha_compromiso DATE NULL COMMENT 'Plazo fatal comprometido para cierre',
    area_apoyo VARCHAR(200) NULL COMMENT 'Área complementaria (Obras, Aseo, DISERCO)',
    observaciones TEXT NULL COMMENT 'Bitácora de avances y contingencias',
    estado ENUM('INGRESADO', 'PENDIENTE', 'EN PROCESO', 'REALIZADO') NOT NULL DEFAULT 'INGRESADO',
    unidad INT NOT NULL DEFAULT 1 COMMENT 'Identificador numérico de la unidad ejecutora',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_compromiso),
    INDEX idx_compromisos_delegacion (id_delegacion),
    INDEX idx_compromisos_responsable (id_responsable),
    INDEX idx_compromisos_estado (estado),
    CONSTRAINT fk_compromisos_delegaciones
        FOREIGN KEY (id_delegacion)
        REFERENCES delegaciones (id_delegacion)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_compromisos_funcionarios
        FOREIGN KEY (id_responsable)
        REFERENCES funcionarios (id_funcionario)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Agenda colectiva intersectorial para resolver requerimientos de mediano plazo';

-- ==============================================================================
-- 5. TABLAS DEL MÓDULO RESULTADOS Y SEMÁFORO SGR (EP-02, EP-05, EP-06)
-- ==============================================================================

-- Tabla: Ciclos / Períodos de Evaluación Trimestral
DROP TABLE IF EXISTS periodos_evaluacion;
CREATE TABLE periodos_evaluacion (
    id_periodo INT AUTO_INCREMENT COMMENT 'Identificador del período trimestral',
    nombre VARCHAR(100) NOT NULL COMMENT 'Glosa (ej: 3er Trimestre 2026)',
    fecha_inicio DATE NOT NULL,
    fecha_cierre DATE NOT NULL,
    dias_totales INT NOT NULL DEFAULT 90 COMMENT 'Días hábiles o corridos del ciclo',
    dias_transcurridos INT NOT NULL DEFAULT 89 COMMENT 'Días acumulados al momento de evaluación',
    activo TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1 = En curso, 0 = Histórico/Cerrado',
    PRIMARY KEY (id_periodo)
) ENGINE=InnoDB COMMENT='Períodos temporales para el cómputo de metas y avances';

-- Tabla: Metas Ponderadas por Funcionario (Ficha Oficial SGR)
DROP TABLE IF EXISTS metas_funcionario;
CREATE TABLE metas_funcionario (
    id_meta INT AUTO_INCREMENT COMMENT 'Identificador de la meta ponderada',
    id_funcionario INT NOT NULL COMMENT 'Funcionario evaluado',
    id_periodo INT NOT NULL COMMENT 'Período trimestral correspondiente',
    item VARCHAR(200) NOT NULL COMMENT 'Ítem evaluado (ej: Informes Sociales, Emergencia)',
    ponderador DECIMAL(5,2) NOT NULL COMMENT 'Porcentaje asignado al ítem (Suman 100% por cargo)',
    meta_periodo INT NOT NULL COMMENT 'Cantidad mínima comprometida para el período',
    avance_actual INT NOT NULL DEFAULT 0 COMMENT 'Gestiones válidas con evidencia aprobada',
    porcentaje_cumplimiento DECIMAL(6,2) NOT NULL DEFAULT 0.00 COMMENT '(avance/meta)*100 (Tope máx 150%)',
    cumplimiento_ponderado DECIMAL(6,2) NOT NULL DEFAULT 0.00 COMMENT 'ponderador * porcentaje_cumplimiento',
    felicitaciones INT NOT NULL DEFAULT 0 COMMENT 'Felicitaciones formales recibidas (+10% c/u, máx 3)',
    reclamos INT NOT NULL DEFAULT 0 COMMENT 'Reclamos formales ciudadanos recibidos (-20% a -30%)',
    PRIMARY KEY (id_meta),
    INDEX idx_metas_funcionario (id_funcionario),
    INDEX idx_metas_periodo (id_periodo),
    CONSTRAINT fk_metas_funcionarios
        FOREIGN KEY (id_funcionario)
        REFERENCES funcionarios (id_funcionario)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_metas_periodos
        FOREIGN KEY (id_periodo)
        REFERENCES periodos_evaluacion (id_periodo)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Ponderaciones, metas y cálculo matemático de cumplimiento por funcionario';

-- Tabla: Indicadores y Disponibilidad de Dotación por Delegación
DROP TABLE IF EXISTS indicadores_delegacion;
CREATE TABLE indicadores_delegacion (
    id_indicador INT AUTO_INCREMENT,
    id_delegacion INT NOT NULL,
    id_periodo INT NOT NULL,
    area VARCHAR(150) NOT NULL COMMENT 'Área o cargo evaluado en la delegación',
    responsable VARCHAR(200) NOT NULL COMMENT 'Titular del área',
    avance_porcentaje DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT 'Porcentaje acumulado',
    estado_semaforo ENUM('verde', 'amarillo', 'rojo') NOT NULL DEFAULT 'verde' COMMENT 'Verde: >=98.9%, Amarillo: >=60%, Rojo: <60%',
    licencias INT NOT NULL DEFAULT 0 COMMENT 'Días de ausentismo por licencias médicas',
    vacaciones INT NOT NULL DEFAULT 0 COMMENT 'Días por feriado legal',
    emergencias INT NOT NULL DEFAULT 0 COMMENT 'Eventos de emergencia asistidos',
    compensatorios INT NOT NULL DEFAULT 0 COMMENT 'Días compensatorios administrativos otorgados',
    PRIMARY KEY (id_indicador),
    INDEX idx_indicadores_delegacion (id_delegacion),
    INDEX idx_indicadores_periodo (id_periodo),
    CONSTRAINT fk_indicadores_delegaciones
        FOREIGN KEY (id_delegacion)
        REFERENCES delegaciones (id_delegacion)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_indicadores_periodos
        FOREIGN KEY (id_periodo)
        REFERENCES periodos_evaluacion (id_periodo)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Consolidado ejecutivo y semáforo de alerta para el Delegado y Alcaldía';

-- Reactivar chequeo de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;

-- ==============================================================================
-- 6. DATOS INICIALES (POBLADO PARA DEMOSTRACIÓN Y VALIDACIÓN)
-- ==============================================================================

-- 6.1 Delegaciones
INSERT INTO delegaciones (id_delegacion, nombre, ambito, responsable, foco_estrategico, estado) VALUES
(1, 'Delegación Municipal Las Compañías', 'Las Compañías Alta y Baja', 'He-Man', 'Atención integral comunitaria, operativos sociales y resolución territorial rápida', 'Activa'),
(2, 'Delegación Municipal La Antena', 'Sector La Antena y Florida', 'Thor', 'Seguridad vecinal, recuperación de espacios públicos y mediación comunitaria', 'Activa'),
(3, 'Delegación Municipal Centro y Casco Histórico', 'Centro Urbano y Casco Histórico', 'Batman', 'Fiscalización comercial, turismo patrimonial y aseo urbano', 'Activa'),
(4, 'Delegación Municipal Rural', 'Valles y Localidades Rurales', 'Superman', 'Conectividad hídrica, caminos rurales y apoyo a crianceros', 'Activa');

-- 6.2 Funcionarios
INSERT INTO funcionarios (id_funcionario, id_delegacion, nombre, cargo, activo, fecha_ingreso) VALUES
(1, 1, 'He-Man', 'Delegado Municipal', 1, '2024-01-01'),
(2, 1, 'Acuaman', 'Territorial OO.CC. 1', 1, '2024-03-15'),
(3, 1, 'Flash', 'Gestor Social 1', 1, '2024-02-01'),
(4, 1, 'Pantera Negra', 'Prof. Planificación y Control', 1, '2024-01-10'),
(5, 1, 'Capitana Marvel', 'Coordinador DISERCO', 1, '2024-04-01'),
(6, 1, 'Hulk', 'Gestor Social 3', 1, '2024-02-15'),
(7, 1, 'Capitán América', 'Gestor Social 2', 1, '2024-03-01'),
(8, 1, 'Spider-Man', 'Territorial OO.CC. 2', 1, '2024-05-10');

-- 6.3 Período de Evaluación Trimestral
INSERT INTO periodos_evaluacion (id_periodo, nombre, fecha_inicio, fecha_cierre, dias_totales, dias_transcurridos, activo) VALUES
(1, '3er Trimestre 2026', '2026-07-01', '2026-09-30', 90, 89, 1);

-- 6.4 Actividades
INSERT INTO actividades (id_actividad, id_funcionario, fecha, solicitud, accion, responsable, item_evaluacion, estado, contacto, telefono, ingreso_tubo, codigo_evidencia) VALUES
(1, 2, '2026-07-06', 'Solicitud de Reunión por vehículos mal estacionados', 'Gestionar Reunión con vecinos y directiva', 'Acuaman', 'ATENCION DE USUARIO TELEFONO Y PRESENCIAL', 'Realizado', 'María González', '+56 9 8765 4321', 0, 'EVI-2026-0901'),
(2, 2, '2026-07-06', 'Solicitud de Poda en Sector de Uruguay con Pasaje Totoral', 'Gestionar Poda e inspección de cuadrilla', 'Acuaman', 'ATENCION DE USUARIO TELEFONO Y PRESENCIAL', 'Realizado', 'Carlos Muñoz', '+56 9 5544 3322', 1, 'EVI-2026-0902'),
(3, 3, '2026-07-01', 'Entrega de documentación para aporte económico por incendio', 'Visita Terreno y Entrega de Informe Social', 'Flash', 'INFORMES SOCIALES', 'Realizado', 'Rosa Valenzuela', '+56 9 9988 7766', 0, 'EVI-2026-0903'),
(4, 4, '2026-07-08', 'Coordinación Gestión territorial actividad navidad', 'Reunión logística con juntas vecinales', 'Pantera Negra', 'EMERGENCIA', 'Realizado', 'Pedro Soto', '+56 9 3322 1100', 0, 'EVI-2026-0904');

-- 6.5 Evidencias
INSERT INTO evidencias (id_evidencia, id_actividad, codigo, archivo_ruta, imagen_verificada, verificador_valido, resultado, estado_validacion, observacion) VALUES
(1, 1, 'EVI-2026-0901', 'acta_reunion_vehiculos.jpg', 1, 1, 1, 'Aprobada', 'Acta firmada con timbre de delegación conforme'),
(2, 2, 'EVI-2026-0902', 'registro_fotografico_poda.jpg', 1, 1, 1, 'Aprobada', 'Fotografía de poda antes y después verificada'),
(3, 3, 'EVI-2026-0903', 'informe_social_fibe_082.pdf', 0, 1, 0, 'Pendiente', 'Pendiente visación de jefatura DIDECO'),
(4, 4, 'EVI-2026-0904', 'asistencia_comites_navidad.jpg', 0, 0, 0, 'Corregir', 'Fotografía borrosa requiere reemplazo');

-- 6.6 Compromisos del Tubo de Trabajo
INSERT INTO compromisos_tubo (id_compromiso, id_delegacion, id_responsable, fecha_solicitud, actividad, tipo, solicitante, territorio, responsable, fecha_compromiso, area_apoyo, observaciones, estado, unidad) VALUES
(1, 1, 8, '2026-07-06', 'Boulevard Las Compañías — Coordinación feriantes', 'EXT', 'Delegación', 'Plaza El Salitre', 'Spider-Man', '2026-08-15', 'Fomento Productivo', 'Operativo instalado y ejecutado', 'REALIZADO', 1),
(2, 1, 4, '2026-07-06', '1° Encuentro de centros de madre sector Las Violetas', 'EXT', 'Centro de Madres Las Violetas', 'Sector Las Violetas', 'Iron Man', '2026-08-20', 'DIDECO', 'Finalizado con asistencia de 60 dirigentas', 'REALIZADO', 1),
(3, 1, 7, '2026-07-06', 'Solicitud de Poda JJVV Terrazas del Brillador', 'EXT', 'JJVV Terrazas del Brillador', 'Terrazas del Brillador', 'Capitán América', '2026-09-15', 'Parques y Jardines', 'Cuadrilla programada para semana entrante', 'EN PROCESO', 1),
(4, 1, 6, '2026-07-06', 'Salida a terreno y catastro con dirigentes', 'EXT', 'Delegación', 'Sector La Campiña', 'Hulk', '2026-09-25', 'Obras Municipales', 'A la espera de confirmación de vehículo municipal', 'PENDIENTE', 1);

-- 6.7 Metas Ponderadas de Funcionario (Ejemplo Acuaman y Gestor Social)
INSERT INTO metas_funcionario (id_meta, id_funcionario, id_periodo, item, ponderador, meta_periodo, avance_actual, porcentaje_cumplimiento, cumplimiento_ponderado, felicitaciones, reclamos) VALUES
(1, 2, 1, 'ATENCIÓN DE USUARIO PRESENCIAL Y TELEFÓNICA', 25.00, 40, 11, 27.50, 6.88, 0, 0),
(2, 2, 1, 'INFORMES SOCIALES Y FICHAS FIBE', 30.00, 20, 6, 30.00, 9.00, 0, 0),
(3, 2, 1, 'GESTIÓN TERRITORIAL Y OPERATIVOS', 25.00, 15, 4, 26.67, 6.67, 0, 0),
(4, 2, 1, 'EMERGENCIAS COMUNALES Y REUNIONES', 20.00, 10, 3, 30.00, 6.00, 0, 0),
(5, 6, 1, 'ATENCIÓN SOCIAL A USUARIO PRESENCIAL', 35.00, 50, 75, 150.00, 52.50, 2, 0),
(6, 6, 1, 'VISITA A TERRENO Y PERITAJE', 25.00, 30, 45, 150.00, 37.50, 1, 0),
(7, 6, 1, 'ENTREGA DE INFORME Y BENEFICIO', 25.00, 25, 38, 150.00, 37.50, 0, 0),
(8, 6, 1, 'EMERGENCIA SOCIAL INMEDIATA', 15.00, 15, 22, 146.67, 22.00, 0, 0);

-- 6.8 Indicadores de Delegación (Semáforo de Cumplimiento)
INSERT INTO indicadores_delegacion (id_indicador, id_delegacion, id_periodo, area, responsable, avance_porcentaje, estado_semaforo, licencias, vacaciones, emergencias, compensatorios) VALUES
(1, 1, 1, 'GESTOR SOCIAL 3', 'Hulk', 150.00, 'verde', 0, 0, 4, 0),
(2, 1, 1, 'GESTOR SOCIAL 2', 'Capitán América', 92.70, 'verde', 2, 5, 2, 1),
(3, 1, 1, 'PLANIFICACIÓN Y GESTIÓN', 'Pantera Negra', 84.80, 'verde', 0, 0, 1, 2),
(4, 1, 1, 'TERRITORIAL OO.CC. 1', 'Acuaman', 28.30, 'rojo', 10, 10, 1, 1);

-- ==============================================================================
-- FIN DEL SCRIPT SGR MUNICIPALIDAD DE LA SERENA
-- ==============================================================================
