## Evaluación Sumativa #3 (30%): Aplicación web con CRUD.

Ingeniería en informática

Programación Back End (TI3041)

La Serena

## Situación de Evaluación: Evolución del Proyecto Desarrollado en la Evaluación Sumativa N°2

## Contexto

En la Evaluación Sumativa N° 2 se construyó una aplicación web basada en Django Framework, utilizando una base de datos relacional, Django ORM, despliegue en AWS EC2, control de versiones mediante GitHub y administración de datos utilizando Django Admin.

La organización ahora requiere evolucionar la solución hacia un entorno más cercano a una aplicación real de producción, eliminando completamente la dependencia de Django Admin para la gestión de información y trasladando todas las funcionalidades hacia interfaces desarrolladas mediante Django Templates.

Además, la aplicación deberá incorporar un sistema completo de autenticación y autorización basado en múltiples perfiles de usuario, paneles de administración diferenciados según permisos y mecanismos de recuperación de contraseña mediante correo electrónico utilizando herramientas de Inteligencia Artificial como apoyo al desarrollo.

## Instrucciones

De forma individual o grupal, continúe el desarrollo del proyecto realizado en las evaluaciones anteriores.

La aplicación deberá encontrarse completamente funcional al momento de la revisión presencial.

No se permitirá utilizar Django Admin para realizar las operaciones del sistema.

Toda interacción deberá realizarse mediante páginas desarrolladas utilizando:

- Django Templates.

- Bootstrap.

- Django ORM.

- Formularios Django.

- Sistema de autenticación de Django.

- Sistema de permisos y grupos.

- Herramientas de Inteligencia Artificial como apoyo al desarrollo.

## Requerimientos de Autenticación

La aplicación deberá incorporar un sistema completo de inicio de sesión.

## Funcionalidades mínimas

## Inicio de Sesión

La aplicación deberá permitir:

- Ingreso mediante usuario y contraseña.

- Cierre de sesión.

- Protección de vistas mediante autenticación.

- Restricción de acceso según perfil.

## Perfiles de Usuario

Se deberán implementar como mínimo tres perfiles diferentes:

| Perfil         | Nivel de acceso         |
| -------------- | ----------------------- |
| Administrador  | Acceso total al sistema |
| Supervisor     | Permisos intermedios    |
| Administrativo | Permisos mínimos        |

Cada perfil deberá poseer permisos diferenciados.

Durante la revisión el estudiante deberá demostrar:

- Creación de usuarios.

- Asignación de grupos.

- Restricciones funcionales.

- Acceso diferenciado según perfil.

## Recuperación de Contraseña mediante Correo Electrónico

Utilizando herramientas de Inteligencia Artificial como apoyo al desarrollo, se deberá implementar un sistema funcional de recuperación de contraseña.

## Requerimientos mínimos

La solución deberá permitir:

- 1. Solicitar recuperación mediante correo electrónico.

- 2. Generar token seguro de recuperación.

- 3. Enviar enlace de recuperación al correo del usuario.

- 4. Validar token.

- 5. Permitir establecer una nueva contraseña.

- 6. Confirmar cambio exitoso.

Durante la revisión presencial el estudiante deberá demostrar el flujo completo.

## Evidencias requeridas

- Usuario solicita recuperación.

- Recepción del correo electrónico.

- Apertura del enlace recibido.

- Cambio de contraseña.

- Acceso exitoso utilizando la nueva contraseña.

## Eliminación del Uso de Django Admin

A partir de esta evaluación:

No se permitirá utilizar Django Admin como mecanismo principal de administración del sistema.

Se evaluará exclusivamente la funcionalidad implementada mediante Django Templates.

Las operaciones deberán ejecutarse desde interfaces propias desarrolladas por el estudiante.

## Dashboard por Perfil

La aplicación deberá incorporar paneles de navegación diferenciados.

## Dashboard Administrador

Debe permitir:

- Acceso a todos los mantenedores.

- Acceso a todas las transacciones.

- Gestión de usuarios.

- Visualización global del sistema.

## Dashboard Supervisor

Debe permitir:

- Acceso a mantenedores autorizados.

- Acceso a transacciones autorizadas.

- Visualización de información operacional.

## Dashboard Administrativo

Debe permitir:

- Acceso únicamente a las funcionalidades asignadas.

- Restricción de operaciones críticas.

El comportamiento deberá variar según el perfil autenticado.

## Requerimientos de Mantenedores

La aplicación deberá incorporar como mínimo:

## Dos mantenedores completamente funcionales

Cada mantenedor deberá permitir:

- Crear registros.

- Buscar registros.

- Listar registros.

- Modificar registros.

- Eliminar registros.

Operaciones CRUD completamente funcionales.

## Ejemplos

- Clientes.

- Productos.

- Servicios.

- Técnicos.

- Equipos.

- Categorías.

- Reservas.

O cualquier entidad asociada a la problemática desarrollada.

## Requerimientos de Transacciones

La aplicación deberá incorporar al menos:

## Una transacción operacional

La transacción deberá involucrar:

- Dos o más entidades relacionadas.

- Formularios funcionales.

- Persistencia en base de datos.

- Validaciones.

## Ejemplos

- Registro de atención técnica.

- Generación de reserva.

- Venta de productos.

- Registro de servicio.

- Asignación de tickets.

- Gestión de órdenes de trabajo.

## Requerimientos Técnicos

Se deberá mantener lo desarrollado en la evaluación anterior:

- AWS EC2 operativa.

- Aplicación desplegada.

- Repositorio GitHub.

- Base de datos relacional.

- Django ORM.

- Migraciones.

- Variables de entorno.

- Control de versiones.

## Revisión Presencial Obligatoria

Durante la revisión el estudiante deberá demostrar:

## Seguridad y Acceso

- Inicio de sesión funcional.

- Cierre de sesión.

- Usuarios registrados.

- Perfiles diferenciados.

- Restricción de accesos.

## Recuperación de Contraseña

- Solicitud de recuperación.

- Correo enviado.

- Token generado.

- Restablecimiento de contraseña.

## Dashboard

- Dashboard Administrador.

- Dashboard Supervisor.

- Dashboard Administrativo.

## Mantenedores

- Operaciones CRUD completas.

- Validaciones.

- Formularios.

- Búsquedas.

## Transacciones

- Flujo completo de la operación.

- Registro en base de datos.

- Relaciones entre entidades.

## Base de Datos

- Modelos implementados.

- Relaciones.

- Migraciones.

- Consistencia de datos.

## GitHub

- Repositorio actualizado.

- Historial de commits.

- Evidencia del desarrollo incremental.

## AWS

- Aplicación ejecutándose desde EC2.

- Acceso funcional vía navegador.

## Entregables

- 1. Aplicación Web Operativa

La aplicación deberá incluir:

- Inicio de sesión.

- Recuperación de contraseña.

- Gestión de perfiles.

- Dashboards por rol.

- CRUD completo desde Django Templates.

- Transacciones funcionales.

- 2. Repositorio GitHub

Debe contener:

- Código fuente completo.

- README actualizado.

- Historial de commits.

- Archivo .gitignore.

## 3. Documento Técnico (PDF o Word)

Debe incluir:

## Descripción del proyecto

- Objetivo.

- Problemática abordada.

- Funcionalidades desarrolladas.

## Seguridad

- Estructura de roles.

- Permisos implementados.

- Flujo de autenticación.

## Base de datos

- Modelo entidad-relación.

- Capturas de tablas.

- Relaciones implementadas.

## Evidencia de Interfaces

Capturas de:

- Login.

- Recuperación de contraseña.

- Dashboard Administrador.

- Dashboard Supervisor.

- Dashboard Administrativo.

- Mantenedores.

- Transacciones.

## Evidencia de AWS

Capturas de:

- Instancia EC2.

- Ejecución del proyecto.

## Evidencia de GitHub

Capturas de:

- Repositorio.

- Historial de commits.

## Evidencia de IA

- Prompts utilizados.

- Respuestas obtenidas.

- Aplicación práctica de las respuestas en el desarrollo.

11

## Escala de Apreciación

|                                           | Puntaje |     |     | Puntaje                    |
| ----------------------------------------- | ------- | --- | --- | -------------------------- |
| Criterio de Evaluación                    | L       | ML  | PL  | NL                         |
|                                           | Máximo  |     |     | Obtenido -                 |
| Sistema de autenticación                  | 15 15   | 11  | 6   | 15 o                       |
| Gestión de perfiles y permisos            | 15 15   | 11  | 6   | o 15                       |
| Recuperación de contraseña mediante token | 15 15   | 11  | 6   | o 15                       |
| perfil Dashboard por                      | 10 10   | 7   | 4   | 1) 10                      |
| Dos mantenedores CRUD completos           | 20 20   | 14  | 8   | o 20                       |
| Transacción funcional                     | 10 10   | 7   | 4   | 10 o                       |
| Base de datos ORM y                       | 5 5     | 4   | 2   | o 5                        |
| AWS EC? operativa                         | 5 5     | 4   | 2   | 0 5                        |
| GitHub y control de versiones             | 3 3     | 2   | 12  | 0 3                        |
| Evidencia de uso de IA                    | 2 2     | 1   | 0,8 | 2 o                        |
| TOTAL                                     | 100     |     |     | 100 Total puntaje obtenido |
|                                           |         |     |     | Nota 7                     |

| Nivel                     | Descripción                                          | Factor |
| ------------------------- | ---------------------------------------------------- | ------ |
| Logrado (L)               | Cumple completamente el criterio solicitado.         | 100%   |
| Medianamente Logrado (ML) | Cumple parcialmente el criterio, presentando errores | 70%    |
| Por Lograr (PL)           | Cumple de forma insuficiente el criterio,            | 40%    |
| No Logrado (NL)           | No presenta la evidencia o esta no funciona.         | 0%     |

## Escala de Notas:

| Puntaje — Nota — |         |      |         |      |         |       |         |      |         |      |         |        |         |
| ---------------- | ------- | ---- | ------- | ---- | ------- | ----- | ------- | ---- | ------- | ---- | ------- | ------ | ------- |
|                  | Puntaje | Nota | Puntaje | Nota | Puntaje | “Nota | Puntaje | Nota | Puntaje | Nota | Puntaje | Nota   | Puntaje |
| o                | 1013    | 17   | 26      | 23   | 39      | 30    | 5       | 36   | 65      | 44   | 7       | sa     | 63      |
| 1                | 11      | 727  |         | 24   | 40      | 3053  |         | 37   | 66      | 45   | 79      | sa 2   | 64      |
| 2                | 1115    | 1828 |         | 24   | 4       | 31    | 5       | 37   | 67      | 45   | 80      | 5593   | 65      |
| 3                | 12 16   | 18   | 29      | 25   | 42      | 3155  |         | 38   | 6       | 46   | 81      | 56     | 66      |
| 4                | 12 17   | 1930 |         | 25   | 43      | 32    | 56      | 38   | 69      | 47   | 8       | 57 5   | 66      |
| 5                | 1318    | 1931 |         | 26   | 4       | 32    | 57      | 39   | 70      | 48   | 8       | 57%    | 67      |
| 5                | 13 19   | 20   | 32      | 26   | 45      | 33058 |         | 39   | 7       | 48   |         | 58 97  | 68      |
| 7                | 14 2    | 20   | 33      | 27   | 46      | 33    | 5       | 40   |         | 4985 |         | 59 8   | 69      |
| E                | 142     | 21   | a       | 27   | 47      | 34    | 60      | 40   | 73      |      | 5086    | 60     | 69      |
| 9                | 15 2    | 21   | 35      | 28   | 48      | 34    | 6       | 4174 |         |      | 5187    | 60 100 | 70      |
| 10               | 1523    | 22   | 36      | 28   | 49      | 35    | 6       | 42   | 75      |      | 5188    | 61     |         |
|                  | 16 24   | 22   | 37      | 29   | 50      | 35    | 6       | 42   | 76      | 52   | 8       | 62     |         |
