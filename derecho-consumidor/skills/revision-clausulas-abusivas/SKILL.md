---
name: revision-clausulas-abusivas
description: Revisa un contrato de adhesión o de consumo (plan de ahorro automotor, crédito prendario, tarjeta de crédito, seguro, contrato de prestación, condiciones generales de servicio) y detecta cláusulas abusivas bajo LDC art. 37 y CCyCN arts. 988 y 1117 ss. Produce dictamen con marcado de cláusulas, encuadre normativo y propuesta de impugnación. Usar cuando el abogado tiene un contrato físico/PDF/imagen y quiere análisis fundado para una intimación o un escrito.
argument-hint: <ruta-al-contrato> [--tipo plan-ahorro|prendario|tarjeta|seguro|prestacion|otros]
---

# Revisión de Cláusulas Abusivas

## Objetivo

Producir un dictamen que el abogado pueda usar como insumo directo para:
- Intimación extrajudicial a la empresa pidiendo eliminación o readecuación de la cláusula.
- Denuncia ante autoridad administrativa de defensa del consumidor (provincial o nacional).
- Escrito judicial de nulidad parcial del contrato (CCyCN art. 989) o reclamo de devolución.
- Columna periodística denunciando la práctica abusiva (si el caso lo amerita y el abogado lo decide).

## Marco normativo aplicado

Cargar antes de empezar las referencias:

- `references/ldc-24240.md` — art. 37 y concordantes.
- `references/ccycn-consumo.md` — arts. 988, 1092-1122, 1117 ss., 771.
- `references/normativa-mendoza.md` si la jurisdicción es Mendoza.
- Si está conectado SAIJ, consultar tesauro por: "cláusula abusiva", "contrato por adhesión", "consumidor".

## Procedimiento

### 1. Lectura del contrato

- Leer el contrato completo. Si es PDF, extraer texto. Si es imagen, OCR.
- Identificar: partes, objeto, plazo, precio, moneda, mecanismos de actualización, modos de extinción, jurisdicción y competencia, cargos administrativos, seguros, garantías.
- Detectar si es **contrato por adhesión** (CCyCN art. 984) o **contrato de consumo** (CCyCN art. 1092). Casi siempre es ambos; declararlo explícitamente.

### 2. Identificación de cláusulas problemáticas

Para cada cláusula, evaluar contra los siguientes test cumulativos:

**Test LDC art. 37 (cualquiera basta para abusividad):**

- (a) Desnaturaliza obligaciones del proveedor o limita su responsabilidad por daños.
- (b) Importa renuncia o restricción de los derechos del consumidor, o amplía los del proveedor.
- (c) Invierte la carga de la prueba en perjuicio del consumidor.

**Test CCyCN art. 988 (contratos por adhesión, cualquiera basta):**

- (a) Cláusulas que desnaturalizan obligaciones del predisponente.
- (b) Cláusulas que importan renuncia o restricción de derechos del adherente, o amplían derechos del predisponente que resulten de normas supletorias.
- (c) Cláusulas sorpresivas — aquellas que por su contenido, redacción o presentación, no son razonablemente previsibles.

**Sub-tests específicos por tipo de contrato:**

- **Planes de ahorro automotor:** cláusula de actualización por valor móvil del modelo, cargo de "gastos administrativos" desproporcionado, imposibilidad de rescisión sin penalidad, transferencia de riesgos de fabricación al suscriptor. Resolución IGJ aplicable.
- **Crédito prendario / personal:** tasa nominal vs. costo financiero total, capitalización de intereses, comisiones no informadas, cláusula de aceleración, seguros forzosos. Comparar TNA contra promedio BCRA del segmento. Doctrina de la usura (CCyCN art. 771).
- **Tarjeta de crédito:** Ley 25.065 — comisiones no autorizadas, intereses punitorios excesivos, modificaciones unilaterales del contrato.
- **Seguro:** Ley 17.418 — cláusula de caducidad, exclusiones de cobertura sorpresivas, alteración del riesgo.
- **Prepaga / salud:** Ley 26.682 — autorizaciones, copagos, exclusiones, aumentos de cuota.
- **Servicios públicos:** Marco regulatorio sectorial (ENRE, ENARGAS, ENACOM, SSS). Cargos no autorizados por el ente regulador, facturación sin lectura, corte sin previo aviso.

### 3. Verificación contra fuentes

Si SAIJ está conectado:
- Buscar jurisprudencia argentina reciente sobre el tipo de cláusula identificado.
- Citar fallo, tribunal, fecha y holding aplicable.
- Marcar como `[verificar]` cualquier cita que no haya sido recuperada de la fuente.

Si SAIJ no está conectado:
- Citar de memoria con marca `[verificar — sin fuente conectada]`.
- Avisar explícitamente al abogado que sin SAIJ las citas requieren revisión manual.

### 4. Cuantificación del perjuicio

Si el contrato permite calcular el perjuicio económico al consumidor, hacerlo:
- Diferencia entre lo facturado/percibido y lo legalmente exigible.
- Intereses moratorios (tasa pasiva o activa según corresponda).
- Reajuste por desvalorización monetaria si aplica.
- Costo de oportunidad si es relevante.

No inventar números: si falta información (cuotas pagadas, fecha de inicio, capital), pedirla.

### 5. Propuesta de acción

Sugerir al abogado **una o dos** vías concretas, según el caso:

- **Intimación extrajudicial** (LDC art. 4, deber de información; o pedido de readecuación o nulidad parcial). Ofrecer redactarla con la skill `intimacion-servicio-publico` o equivalente.
- **Denuncia administrativa** ante OMIC o Dirección Provincial de Defensa del Consumidor.
- **COPREC** si la empresa es grande y el reclamo es nacional.
- **Acción judicial individual** — nulidad parcial (CCyCN art. 989) + devolución + daños + daño punitivo (LDC art. 52 bis).
- **Acción colectiva** si la cláusula afecta a una clase identificable.

## Estructura de salida

El dictamen sigue esta estructura (no llamarla "informe" — llamarla "Dictamen sobre Cláusulas Abusivas"):

```
DICTAMEN SOBRE CLÁUSULAS ABUSIVAS
Contrato analizado: [tipo y partes]
Fecha: [fecha del dictamen]

1. CONTEXTO
[1-2 párrafos: qué es el contrato, quién lo predispone, qué adhiere el consumidor]

2. ENCUADRE NORMATIVO
[Bloque de normas aplicables: LDC, CCyCN, normativa sectorial, jurisdicción]

3. CLÁUSULAS OBSERVADAS
Para cada cláusula problemática:
  3.X — [Identificación: art./cláusula del contrato]
  Texto literal: "[transcripción]"
  Encuadre: [art. 37 LDC inciso X / art. 988 CCyCN inciso Y]
  Análisis: [por qué configura abusividad]
  Jurisprudencia: [fallos relevantes si están disponibles]

4. CUANTIFICACIÓN
[Si corresponde]

5. ACCIONES SUGERIDAS
[1-2 vías concretas, jerarquizadas por costo/beneficio]

Mario Vadillo
Abogado
```

## Reglas duras de salida

- **Sin "Conclusión".** El dictamen termina con "Acciones Sugeridas".
- **Negrita solo en encabezados** (1., 2., 3.X, etc.). En el cuerpo no.
- **Citar normativa con número de art. e inciso.** No "la LDC dispone que..." sino "la LDC, en su art. 37 inc. b, dispone que...".
- **No nombrar bancos o empresas específicas** si el dictamen va a ser usado en columna periodística sobre sobreendeudamiento.
- **Si el contrato es muy extenso (>30 carillas), pedir prioridades** al abogado en lugar de revisarlo entero a ciegas.
- **Verificación rigurosa:** no aceptar como ciertas las afirmaciones del usuario sobre cláusulas sin leerlas en el documento.

## Trampas conocidas

- **Plan de ahorro automotor — cargo administrativo:** la jurisprudencia varía. No afirmar "es abusivo" sin contrastar — el porcentaje y la transparencia previa importan.
- **Crédito prendario — tasa:** sin el dato de la TNA promedio BCRA del segmento al momento de contratar, la afirmación de usura queda débil. Pedir o consultar.
- **Servicios públicos:** algunos cargos están autorizados por el ente regulador. Antes de impugnar, verificar la resolución habilitante en el marco regulatorio.
- **Resoluciones ANAC:** **no citar Decreto 809/2024 junto con Resolución 1532/98** — son regímenes incompatibles. Verificar cuál rige a la fecha del hecho.
