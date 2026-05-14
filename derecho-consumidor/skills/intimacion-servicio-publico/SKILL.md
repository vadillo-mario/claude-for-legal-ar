---
name: intimacion-servicio-publico
description: Redacta carta documento o nota administrativa de intimación a empresa de servicio público (energía eléctrica EDEMSA/EPRE, gas Ecogas/ENARGAS, agua AYSAM/DGI Irrigación, telecomunicaciones ENACOM, telefonía) por facturación irregular, cortes injustificados, reemplazo de medidor, cargos no autorizados, deuda inexistente, o mora en respuesta a reclamos previos. Usar cuando hay un consumidor concreto, un proveedor identificable, y una causa de reclamo definida.
argument-hint: <empresa> <tipo-reclamo> [--via=carta-documento|nota-administrativa|email-fehaciente]
---

# Intimación a Empresa de Servicio Público

## Objetivo

Producir una intimación que el abogado pueda firmar y enviar el mismo día, con:
- Encabezado completo y formal.
- Hechos descriptos en presente, ordenados cronológicamente.
- Derecho aplicado con cita normativa precisa.
- Plazo de cumplimiento conforme al marco regulatorio.
- Petitorio específico (no genérico).
- Reserva de acciones administrativas, judiciales, y de daño punitivo.

## Información que necesita la skill

Antes de redactar, asegurar tener (preguntar lo que falte, una pregunta por turno):

1. **Datos del consumidor:** nombre, DNI, domicilio (donde recibe el servicio y donde acepta notificaciones).
2. **Datos del proveedor:** denominación social, CUIT si está disponible, domicilio comercial donde corresponda enviar la intimación.
3. **Identificador del servicio:** número de cuenta, NIS, NIC, contrato, póliza, etc.
4. **Causa del reclamo:** qué pasó, desde cuándo, qué documentación tiene el consumidor.
5. **Antecedentes:** ¿hizo reclamo previo? ¿cuándo? ¿qué número de reclamo le dieron? ¿qué respondieron?
6. **Vía deseada:** carta documento (default si no se aclara), nota administrativa (al ente regulador), o correo electrónico fehaciente.

Si el consumidor pidió la intimación con urgencia (corte inminente, factura próxima a vencer, salud comprometida), priorizar carta documento y mencionar la urgencia en el cuerpo.

## Marco normativo por sector

### Energía eléctrica (Mendoza: EDEMSA / EPRE)

- Marco regulatorio: Ley 6.498 (Mza.) y reglamentación EPRE.
- Reclamos por facturación: plazo del ente para resolver, generalmente 30 días hábiles.
- Cortes: requieren preaviso e intimación previa.
- Citas frecuentes: LDC arts. 25, 30, 31. CCyCN arts. 1097-1099.

### Gas (Ecogas / ENARGAS)

- Marco regulatorio: Ley 24.076 y reglamentación ENARGAS.
- Reglamento de Servicio (Resolución ENARGAS aplicable).
- Reclamos por medidor: derecho a contrastación; quien adelanta el costo y a quién se le devuelve si la contrastación falla.

### Agua (Mendoza: AYSAM / DGI Irrigación)

- AYSAM: agua potable, marco regulatorio EPAS (cuando estuvo) / regulación actual.
- DGI Irrigación: canon de riego, Ley General de Aguas Mza., Constitución Mza. arts. 1, 2, 16, 187.
- **Atención: canon por propiedad sin infraestructura de riego — encuadre en SCJM "López c/DGI" (2017) y "Valle de Uco c/DGI" (2021).**

### Telecomunicaciones (ENACOM)

- Ley 27.078 (Argentina Digital) y normativa complementaria.
- Reglamento General de Clientes de los Servicios de Comunicaciones Móviles.
- Reclamos: plazo de respuesta del proveedor, 24-48hs según servicio.

## Procedimiento

### 1. Reunir información

Recoger los 6 puntos del bloque anterior. No avanzar sin: datos del consumidor, datos del proveedor, identificador del servicio, y causa del reclamo.

### 2. Verificar el marco regulatorio aplicable

- Identificar la empresa y el sector.
- Cargar las referencias normativas (sectorial + LDC + CCyCN).
- Si `ar-legal-sources` está conectado, verificar el texto vigente de la resolución regulatoria aplicable.
- Si hay reclamo previo, verificar plazos del ente para que la empresa responda.

### 3. Estructurar el escrito

Formato carta documento estándar (Correo Argentino o equivalente):

```
[Lugar y fecha]

A: [Razón social del proveedor]
[CUIT si se tiene]
[Domicilio comercial]

De mi consideración:

Quien suscribe, [nombre del abogado], en mi carácter de letrado patrocinante
de [nombre del consumidor], DNI [N°], con domicilio en [domicilio del
consumidor] (en adelante "el consumidor"), me dirijo a Ustedes en relación
con el servicio de [tipo de servicio] prestado bajo el N° de [identificador]
en el domicilio de servicio sito en [domicilio del servicio], a efectos de:

INTIMAR formalmente, bajo apercibimiento de iniciar las acciones
administrativas y judiciales que correspondieran, incluyendo el reclamo
de la sanción de daño punitivo prevista en el art. 52 bis de la Ley 24.240,
para que en el plazo de [N] días corridos contados desde la recepción de
la presente, proceda a:

[PETITORIO — numerado, específico]
1. [Acción concreta que se exige]
2. [Acción concreta que se exige]
3. ...

Fundo lo anterior en los siguientes:

HECHOS

[Relato cronológico en presente, párrafos cortos, hechos verificables.
Incluir: fecha de inicio del problema, gestiones previas con número de
reclamo, respuesta o falta de respuesta del proveedor, documentación
respaldatoria]

DERECHO

[Cita normativa precisa. Estructura sugerida:]

a) Marco general — Ley 24.240, art. 4 (deber de información), art. 8 bis
   (trato digno), arts. 25 a 31 (servicios públicos domiciliarios cuando
   aplique). CCyCN arts. 1092 ss. (relación de consumo), 1097-1099 (trato
   digno, equitativo y no discriminatorio).

b) Marco regulatorio sectorial — [norma específica del sector]

c) [Otros argumentos pertinentes al caso]

La falta de cumplimiento del presente requerimiento dentro del plazo
indicado importará el inicio de las acciones que correspondan, sin
necesidad de nueva intimación, dejando expresamente reservado el derecho
del consumidor a reclamar:
- La readecuación o cesación de la conducta lesiva.
- La devolución de las sumas indebidamente percibidas, con más sus
  intereses.
- Los daños y perjuicios derivados (daño emergente, lucro cesante, daño
  moral, privación de uso).
- La sanción de daño punitivo (LDC art. 52 bis).

Quedo a la espera de su respuesta dentro del plazo legal.

Saludo a Ustedes atentamente.

Mario Vadillo
Abogado — [matrícula]
[Domicilio profesional]
[Email — opcional]
```

### 4. Validación previa al despacho

Antes de presentar el borrador al abogado, verificar:

- [ ] ¿Los nombres y datos identificatorios coinciden con lo que dio el consumidor?
- [ ] ¿La causa del reclamo está descripta con hechos verificables, sin adjetivos?
- [ ] ¿El petitorio es específico (no "que cese la conducta abusiva" sino "que descuente $X de la factura N° Y")?
- [ ] ¿El plazo es razonable y conforme al marco regulatorio? (Generalmente 5-10 días para acciones urgentes, 15-30 para readecuaciones contractuales.)
- [ ] ¿La reserva de daño punitivo está incluida?
- [ ] ¿Hay cita normativa precisa con art. e inciso, no genérica?

## Reglas duras de salida

- **Castellano formal pero no arcaico.** Sin "Vuestra Excelencia" ni "tengo el honor de". Sí "me dirijo a Ustedes", "quedo a la espera", "saludo atentamente".
- **Sin negrita en el cuerpo.** Solo en encabezados de sección si la carta documento los admite.
- **Sin íconos, emojis, ni adornos.**
- **El petitorio se numera.** Cada punto del petitorio es una acción concreta.
- **La reserva de daño punitivo va al final, antes del saludo.** No olvidarla.
- **No prometer plazos del proveedor que no surjan de norma o regulación verificada.**

## Trampas conocidas

- **Cortes en curso o inminentes:** la intimación debe enfatizar la urgencia y, si corresponde, mencionar la posibilidad de acción de amparo (art. 43 CN). En esos casos, sumar a la intimación una nota al ente regulador en paralelo.
- **Resoluciones ANAC en transporte aéreo:** si la intimación es a una aerolínea, **no citar Decreto 809/2024 junto con Resolución 1532/98** — verificar cuál rige al hecho.
- **Canon Irrigación sin infraestructura:** encuadre obligado en "López c/DGI" (2017) y "Valle de Uco" (2021). No omitir.
- **ATM Mendoza — tasas de interés y embargos:** estrategia comunicacional primero, intimación después. Consultar con Mario antes de despachar si el caso involucra ATM.
- **Empresas con domicilio comercial fuera de Mendoza:** verificar el domicilio para asegurar que la carta documento llegue. Pedirlo si hay duda.
