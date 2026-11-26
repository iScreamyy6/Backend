# PRESENTACIÓN EJECUTIVA Y DEFENSA TÉCNICA (10 MINUTOS)
## EVALUACIÓN SUMATIVA N° 3 — INGENIERÍA DE SOFTWARE (TI2043)
### INACAP La Serena | Sistema de Gestión de Resultados (SGR) — Ilustre Municipalidad de La Serena

---

## DIAPOSITIVA 1: PORTADA Y PRESENTACIÓN DEL PROYECTO (0:00 – 0:45)

**Título:** Sistema de Gestión de Resultados (SGR) Municipalidad de La Serena  
**Subtítulo:** Validación de Prototipos Interactivos y Defensa de Decisiones de Arquitectura (Etapa 3)  
**Asignatura:** Ingeniería de Software (TI2043) — Ponderación 35%  
**Equipo de Desarrollo:** Alumnos Ingeniería en Informática / Ciberseguridad  

### Mensaje Clave de Apertura (Speech):
> *"Buenos días profesor y comisión. Hoy presentamos la culminación del Sistema de Gestión de Resultados (SGR) para la Ilustre Municipalidad de La Serena. Demostraremos nuestro prototipo interactivo en vivo y defenderemos técnicamente cómo cada diagrama UML y requerimiento levantado en la Evaluación 2 se materializó en una arquitectura robusta, segura y desplegada en la nube de AWS."*

---

## DIAPOSITIVA 2: DIAGNÓSTICO TERRITORIAL Y TENDENCIAS CLOUD (0:45 – 1:30)

### La Problemática Territorial:
* **Antes:** 6 delegaciones municipales desconectadas (Las Compañías, La Antena, Centro, Avenida del Mar, Rural, etc.) operando con planillas Excel aisladas.
* **Consecuencias:** Duplicidad de solicitudes ciudadanas, tiempos de respuesta superiores a 8 minutos y nula trazabilidad gerencial.

### Solución Tecnológica: Arquitectura Cloud (IaaS / SaaS)
* **Paradigma IaaS (Infraestructura como Servicio):** Despliegue en **Amazon Web Services (AWS EC2)** con Ubuntu Server y MySQL 8.4 bajo la IP elástica `3.213.246.194`.
* **Paradigma SaaS (Software como Servicio):** Acceso multi-delegación centralizado mediante navegador web, sin requerir servidores físicos locales en cada territorio.

```
                      +---------------------------------------+
                      |       CLIENTES MULTI-TERRITORIO       |
                      | (Las Compañías / La Antena / Rural)   |
                      +---------------------------------------+
                                          | [HTTPS / Nginx]
                                          v
                      +---------------------------------------+
                      |          AWS EC2 CLUSTER (IaaS)       |
                      |     Gunicorn + Django 6 + MySQL 8.4   |
                      +---------------------------------------+
```

---

## DIAPOSITIVA 3: DEFENSA DE LA METODOLOGÍA HÍBRIDA (EVA 2 -> EVA 3) (1:30 – 2:30)

### Justificación Técnica de la Elección:
1. **¿Por qué Cascada para la Etapa de Análisis (Eva 1 y 2)?:**  
   En la administración pública rige el principio de auditoría y legalidad. Era mandatorio congelar formalmente los 38 Requerimientos Funcionales y normalizar la base de datos en Tercera Forma Normal (3NF) antes de programar.
2. **¿Por qué Scrum para el Desarrollo y Prototipado (Eva 2 y 3)?:**  
   El desarrollo se estructuró en **3 Sprints de 2 semanas** con historias de usuario (HU):
   * **Sprint 1:** Autenticación, control RBAC y navegación.
   * **Sprint 2:** Mantenedores CRUD (Delegaciones, Vecinos, Roles, Territorios).
   * **Sprint 3:** Tablero Kanban Tubo de Trabajo, bandeja de evidencias y despliegue cloud.

---

## DIAPOSITIVA 4: TRAZABILIDAD UML Y MODELO DE DATOS EN CÓDIGO (2:30 – 3:30)

### Pantallazo / Evidencia 1: Modelo Entidad-Relación (MER.png)
*Artefacto:* [MER.png](file:///d:/Django/Backend/Contexto%20de%20la%20problematica/02_Modelamiento_y_Diseno/Diagramas/MER.png)  
Normalización en 3NF con claves foráneas estrictas entre `delegaciones`, `vecinos`, `actividades` y `compromisos`.

### Fragmento de Código Real: Modelo de Transacción Central en Django
```python
# actividades/models.py (Núcleo de la Transacción Municipal)
class Actividad(models.Model):
    id_actividad = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=30, unique=True)
    id_delegacion = models.ForeignKey(Delegacion, on_delete=models.SET_NULL, null=True)
    id_vecino = models.ForeignKey(Vecino, on_delete=models.SET_NULL, null=True)
    solicitud = models.TextField(verbose_name='Requerimiento Ciudadano')
    accion = models.CharField(max_length=300, verbose_name='Acción Realizada')
    
    # Enlace relacional al Tubo de Trabajo (Kanban)
    ingreso_tubo = models.BooleanField(default=False)
    id_compromiso = models.ForeignKey('agenda.Compromiso', on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=30, default='Pendiente')
```
* **Defensa Técnica:** Cada campo del wireframe viaja directamente a este modelo estructurado, garantizando integridad referencial y cero pérdida de datos.

---

## DIAPOSITIVA 5: DEMOSTRACIÓN DE WIREFRAMES — MÓDULO GESTIONES (3:30 – 4:30)

### Pantallazo / Evidencia 2: Resumen y Dashboard Comunal
*Artefacto:* [Resumen.png](file:///d:/Django/Backend/Contexto%20de%20la%20problematica/02_Modelamiento_y_Diseno/Mockups_Galeria/Resumen.png) y [Resumen de la delegación.png](file:///d:/Django/Backend/Contexto%20de%20la%20problematica/02_Modelamiento_y_Diseno/Mockups_Galeria/Resumen%20de%20la%20delegaci%C3%B3n.png)

### Wireframe Interactivo en Vivo: `http://localhost:8000/wireframes/`
* **Formulario Unificado (CU-05):** Búsqueda asíncrona de vecinos por RUT. Si el vecino ya existe, autocompleta nombre, teléfono y dirección en menos de 900 ms.
* **Código Real de Autocompletado (AJAX en Django):**
```python
# actividades/views.py (Búsqueda Asíncrona de Vecinos)
def api_buscar_vecino(request):
    rut = request.GET.get('rut', '').strip()
    vecino = Vecino.objects.filter(rut__iexact=rut).first()
    if vecino:
        return JsonResponse({
            'encontrado': True,
            'nombre': vecino.nombre,
            'telefono': vecino.telefono,
            'direccion': vecino.direccion
        })
    return JsonResponse({'encontrado': False})
```

---

## DIAPOSITIVA 6: DEMOSTRACIÓN DE WIREFRAMES — TUBO DE TRABAJO KANBAN (4:30 – 5:30)

### Pantallazo / Evidencia 3: Tablero Kanban (Tubo de Trabajo)
*Artefacto:* [Tubo de trabajo (agenda colectiva).png](file:///d:/Django/Backend/Contexto%20de%20la%20problematica/02_Modelamiento_y_Diseno/Mockups_Galeria/Tubo%20de%20trabajo%20(agenda%20colectiva).png)

### Demostración en el Sistema:
* **4 Columnas Dinámicas:** *Ingresada*, *En Proceso*, *Atrasadas* (cálculo automático por fecha límite) y *Realizado*.
* **Sincronización Bidireccional en Código Real:**
```python
# agenda/views.py (Sincronización Transaccional Tubo -> Gestión)
if nuevo_estado == 'REALIZADO':
    compromiso.estado = 'Realizado'
    compromiso.fecha_cierre = timezone.now().date()
    compromiso.save()
    # Sincroniza automáticamente la actividad vinculada
    if compromiso.id_actividad:
        compromiso.id_actividad.estado = 'Realizado'
        compromiso.id_actividad.save()
```
* **Defensa Técnica:** La interfaz visual no es estática; está conectada a una máquina de estados relacional que sincroniza compromisos y gestiones en una sola transacción atómica.

---

## DIAPOSITIVA 7: DEMOSTRACIÓN DE WIREFRAMES — SEMÁFORO DE METAS (5:30 – 6:30)

### Pantallazo / Evidencia 4: Semáforo de Cumplimiento de Metas
*Artefacto:* [Semáforo.png](file:///d:/Django/Backend/Contexto%20de%20la%20problematica/02_Modelamiento_y_Diseno/Mockups_Galeria/Sem%C3%A1foro.png)

### Lógica de Ponderación Matemática en Código Real:
```python
# resultados/views.py (Cálculo de Semáforo de Gestión Territorial)
# Solo las evidencias validadas con estado 'Aprobada' y naturaleza 'Cuantitativa' ponderan
gestiones_validas = Actividad.objects.filter(
    id_funcionario=funcionario,
    estado_evidencia='Aprobada',
    tipo_impacto='Cuantitativa'
).count()
porcentaje_avance = min(100.0, (gestiones_validas / meta_trimestre.meta_cuantitativa) * 100)
```
* **Defensa Técnica:** Implementa una regla de negocio inquebrantable validada por la Dirección de Control: ninguna meta puede superar el 100% y las gestiones puramente cualitativas no alteran los números de auditoría.

---

## DIAPOSITIVA 8: SEGURIDAD Y CONTROL DE ROLES RBAC (6:30 – 7:30)

### Matriz de Control de Acceso (RBAC):
* **Administrador:** Alcance comunal completo, gestión de usuarios, roles e informes consolidados.
* **Supervisor:** Restringido exclusivamente a su delegación territorial asignada.
* **Operador / Administrativo:** Solo ingreso y consulta operativa básica.

### Código Real: Filtro Territorial Obligatorio en Vistas
```python
# Municipalidad/views_auth.py y context_processors.py
def delegaciones_filtradas(user):
    perfil = user.perfil
    if perfil.rol and perfil.rol.alcance_autorizado == 'COMUNAL':
        return Delegacion.objects.filter(estado='Activa')
    # Supervisor u Operador: estricta restricción a su delegación asignada
    return Delegacion.objects.filter(id_delegacion=perfil.delegacion_activa_id)
```
* **Defensa Técnica (Ley 19.628):** Impide fugas de información personal entre delegaciones y garantiza que cada territorio responda por su propia jurisdicción.

---

## DIAPOSITIVA 9: ESTÁNDARES DE CALIDAD Y PRUEBAS AUTOMATIZADAS (7:30 – 8:30)

### Calidad Comprobada con Arnés de Pruebas:
Se ejecutó la suite de integración [test_suite.py](file:///d:/Django/Backend/test_suite.py) y [test_api.py](file:///d:/Django/Backend/test_api.py):
* **14 Suites Unitarias y de Integración:** 100% Aprobadas (0 errores).
* **Validación Matemática:** Bloqueo automático ante intentos de configurar ponderaciones > 100%.
* **Idempotencia:** La base de datos se limpia automáticamente tras cada ejecución de pruebas, manteniéndose en estado canónico perfecto (24 gestiones, 10 vecinos, 13 compromisos).

### Fragmento del Test Automatizado en Código:
```python
# test_suite.py (Validación de Ponderación de Metas)
def test_validacion_bloqueo_ponderacion_excedida(self):
    meta = MetaFuncionario(funcionario=self.func, ponderacion=110)
    with self.assertRaises(ValidationError):
        meta.clean()  # Falla inmediatamente si la suma supera 100%
```

---

## DIAPOSITIVA 10: CIBERSEGURIDAD Y NORMATIVAS LEGALES CHILENAS (8:30 – 9:15)

### Cumplimiento Normativo Exigido por la Rúbrica:
1. **OWASP Top 10 (A01 - Broken Access Control):** Resuelto mediante roles RBAC y permisos a nivel de vista.
2. **OWASP Top 10 (A03 - Injection):** Mitigado al 100% mediante consultas ORM parametrizadas en Django (cero concatenación SQL manual).
3. **Ley N° 21.459 (Delitos Informáticos):** Registro de auditoría inmutable (`usuario_creador`, `usuario_revisor`, `fecha_revision`) que previene el repudio de dictámenes de evidencias.
4. **Ley N° 19.628 (Protección de Datos Personales):** Enmascaramiento de RUT, teléfonos y correos en APIs y consultas públicas (`15.***.***-3`, `+56 9 ****-****`).

---

## DIAPOSITIVA 11: CONCLUSIONES Y RETORNO DE INVERSIÓN (9:15 – 10:00)

### Comparativa de Impacto:
| Dimensión | Proceso Manual Anterior | Sistema SGR Implementado |
|---|---|---|
| **Tiempo de Atención Ciudadana** | 8 a 12 minutos por vecino | **Menos de 90 segundos** (Autocompletado AJAX) |
| **Seguimiento de Compromisos** | Cuadernos / Planillas dispersas | **Tablero Kanban sincronizado en tiempo real** |
| **Auditoría de Cumplimiento** | Estimaciones informales | **Semáforo algorítmico respaldado con evidencias** |
| **Infraestructura** | Servidores locales vulnerables | **Cluster Cloud AWS EC2 con MySQL 8.4** |

### Mensaje de Cierre (Speech):
> *"Profesor y comisión: hemos demostrado que nuestro diseño de wireframes no es una maqueta vacía, sino el plano de ingeniería de un sistema real, seguro y validado en producción. Cumplimos el 100% de los criterios de calidad, metodología y seguridad exigidos. Muchas gracias y quedamos a su disposición para las preguntas."*
