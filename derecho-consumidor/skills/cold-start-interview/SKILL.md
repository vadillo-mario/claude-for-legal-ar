---
name: cold-start-interview
description: Setup inicial del plugin derecho-consumidor. Conversa con el abogado para aprender áreas de práctica, jurisdicción, estilo doctrinal, y carga documentos semilla. Escribe/actualiza CLAUDE.md del plugin. Correr este comando ANTES que cualquier otro del plugin. Usar opción --quick-start para una versión de 2 minutos.
argument-hint: [--quick-start | --full | --refresh]
---

# Cold Start Interview — derecho-consumidor

Este comando configura el plugin a la práctica concreta del abogado que lo usa. Toda otra skill del plugin lee el `CLAUDE.md` que este comando escribe; sin correrlo, las salidas son genéricas.

## Modos

- `--quick-start` (default si el archivo `CLAUDE.md` no existe) → 5 preguntas, 2 minutos. Útil para empezar a usar el plugin ya. Refinás después.
- `--full` → 15-20 minutos. Entrevista completa con carga de documentos semilla. Salida sensiblemente mejor en todas las skills.
- `--refresh` → relee el `CLAUDE.md` existente, propone ajustes basados en lo que viste en uso, y confirma cambios. Para usar cada 2-3 meses o cuando cambie algo material (nueva área, nueva jurisdicción, nueva normativa de cabecera).

## Procedimiento — modo `--quick-start`

Hacer estas 5 preguntas, una por turno, esperando respuesta antes de seguir:

1. **Identificación.** "Decime tu nombre, matrícula y jurisdicción principal." Guardar.
2. **Áreas dentro del consumidor.** "¿Cuáles son las 3 áreas en las que más trabajás dentro del derecho del consumidor? (ej: bancario, servicios públicos, transporte aéreo, salud, seguros, planes de ahorro)" Guardar como lista.
3. **Estilo.** "¿Cómo es tu tono de redacción? Elegí lo que más se acerque: (a) doctrinal y formal, (b) doctrinal pero accesible, (c) combativo y periodístico, (d) mixto según canal." Si elige (d), preguntar por canal.
4. **Reglas duras.** "¿Hay tres cosas que NUNCA querés que aparezcan en tus textos? (ej: emojis, fórmulas estándar, jurisprudencia salvo aprobación, mención a tu partido, conclusiones de cierre)" Guardar como prohibiciones.
5. **Fuentes que te interesan especialmente.** "¿Hay normas, fallos o autores doctrinarios que querés que tenga siempre a la vista cuando redactemos? Listalos." Guardar como núcleo doctrinal.

Después de las 5 respuestas:

- Escribir/actualizar `CLAUDE.md` con la información obtenida, preservando todo lo que ya esté ahí y no fue contradicho.
- Mostrarle al abogado un resumen de lo que se guardó.
- Decirle: "Listo, ya podés correr cualquier skill. Si querés afinar más, corré `--full` cuando tengas 15 minutos."

## Procedimiento — modo `--full`

Hacer las 5 preguntas del quick-start, más:

6. **Documentos semilla.** "Pasame 3 a 5 escritos tuyos que reflejen bien tu estilo (intimaciones, escritos judiciales, dictámenes, columnas de opinión). Dame las rutas o los links." Leer cada uno, extraer:
   - Frases recurrentes y giros propios.
   - Estructura típica de cada tipo de documento.
   - Forma de citar normativa y jurisprudencia.
   - Tono y registro.
7. **Jurisprudencia de cabecera.** "Listame fallos que considerás fundamentales en cada una de tus áreas — los que citás siempre o tenés en la cabeza." Guardar con fuente y holding.
8. **Encuadre normativo prioritario.** "¿Qué normas son las que más usás en cada área? Quiero registrarlas para que las tenga a mano." Guardar como tabla.
9. **Ciclo de revisión.** "Cuando recibís un borrador del plugin, ¿qué es lo primero que mirás? ¿Qué errores cometo más seguido?" Guardar como check-list de auto-revisión que cada skill debe hacer antes de emitir.
10. **Canales y reglas por canal.** "Repasame las reglas específicas por canal: redacción judicial, MDZ, redes, WhatsApp." Guardar tabla.
11. **Conectores activos.** Detectar qué MCPs están configurados (SAIJ, ar-legal-sources, WordPress) y registrar en CLAUDE.md cuáles puede usar el plugin y cuáles no.

Cada respuesta del abogado se procesa antes de la siguiente pregunta — no acumular 10 preguntas y pedir todas las respuestas juntas.

## Procedimiento — modo `--refresh`

1. Leer el `CLAUDE.md` actual.
2. Mostrar al abogado un resumen de lo que tiene cargado, agrupado por sección.
3. Para cada sección, preguntar: "¿Sigue vigente esto, o hay algo que cambió?"
4. Detectar inconsistencias en uso reciente (si el abogado corrigió varias veces el mismo punto, sugerir actualizar el perfil).
5. Confirmar cambios antes de escribir.

## Reglas durante la entrevista

- **Una pregunta por turno.** No acumular.
- **No interpretar de más.** Si la respuesta es ambigua, repreguntar.
- **Confirmar antes de escribir CLAUDE.md.** Mostrar el bloque que se va a agregar/modificar y esperar OK.
- **Preservar contenido existente.** Si CLAUDE.md ya tiene reglas duras, no sobreescribirlas sin confirmación explícita.
- **No inventar.** Si el abogado no menciona una norma o un fallo, no completarlo desde el conocimiento del modelo.

## Salida final

Al terminar (cualquier modo), emitir un resumen breve:

```
Perfil cargado. Áreas: [X, Y, Z]. Estilo: [...]. Prohibiciones: [...].
Conectores activos: [...]. Documentos semilla leídos: [N].

Próximos pasos sugeridos:
- /derecho-consumidor:revision-clausulas-abusivas para un contrato
- /derecho-consumidor:intimacion-servicio-publico para una intimación
- /derecho-consumidor:escrito-dano-punitivo para un escrito judicial

Si todavía no instalaste los MCPs de fuentes (SAIJ, ar-legal-sources), ver QUICKSTART paso 6.
```
