# Estándares de trabajo — sap-mcp

Reglas operativas para que el roadmap (`roadmap.md`) se ejecute con **SDD (Spec-Driven Development)** y **AI-TDD (AI-assisted Test-Driven Development)**, de forma reproducible y auditable.

## 1. Convenciones generales

- **Código, identificadores y comentarios en inglés.** Documentación del repo (README, specs, decisiones, roadmap) en español.
- **Una tarea por vez.** Si algo no está claro, se pregunta antes de asumir. No se inventan APIs, campos ni capacidades: se verifican contra el código, el `product_context.md` o una respuesta real.
- **Nada de secretos en código ni logs.** Claves por variables de entorno; redacción en trazas y resultados.
- **Sin hardcodeo de casos de evaluación** ni de respuestas esperadas. El set de evaluación es representativo y extensible, no un listado fijo que el agente memorice.
- **Configuración en un único archivo** (`config.py`), no repartida.
- **Toda llamada externa** (LLM, SAP, RAG, memoria, MCP client) pasa por un módulo cliente con timeout, reintentos acotados y log estructurado.

## 2. Estándar de código

- Funciones pequeñas, una responsabilidad, nombres que explican la intención, sin código muerto ni TODOs sueltos.
- **Tipos explícitos en fronteras** y validación con schema cerrado (`extra="forbid"`).
- **Errores nunca en silencio**: fallar con mensaje claro o devolver el fallback definido, dejándolo en el log.
- Comentarios solo donde aportan el **por qué** (decisión, restricción, comportamiento no obvio del sistema externo).
- **Código propio**: no copiar literal de otros repos; si una librería resuelve el problema, se agrega como dependencia gestionada.

## 3. Git y ramas

- `main` protegido: todo entra por **pull request**.
- Cada PR es una rama desde `origin/main` actualizado; PR describe contexto, cambios, cómo probar y riesgos.
- **Nunca push forzado ni merge forzado ni reescritura de historia publicada.**
- **No se hace commit, push ni merge sin pedido explícito.**
- Commits pequeños y atómicos en español, imperativo, prefijo convencional: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`. El mensaje explica el porqué cuando no es obvio.
- Los documentos entregados no se modifican después de su entrega; lo nuevo va en un documento aparte enlazado desde el README.

## 4. Decisiones (ADR)

Cada decisión no obvia va en `docs/decisions.md`:

```text
## <fecha hora> — <decisión>
Contexto: <qué problema había>
Decisión: <qué se eligió>
Descartado: <alternativa> — <por qué no>
Consecuencias: <qué se vuelve más fácil / más difícil>
```

Regla de `product_context.md`: **no elegir base de datos, framework, protocolo ni servicio sin justificar la decisión.** Si falta información, la decisión queda abierta con su dueño y la evidencia requerida.

## 5. SDD — Spec-Driven Development

Flujo por PR (el `product_context.md` es la spec raíz; cada PR define su sub-spec):

1. **Spec**: escribir el contrato (interfaces, schemas, estados, errores) en un documento breve dentro del PR o en `docs/`. Definir criterios de aceptación **medibles**.
2. **Contratos**: materializar el contrato como tipos/schemas cerrados y protocoles. Este es el "contrato como código".
3. **Tests primero** (ver AI-TDD abajo): los tests nacen de la spec, no de la implementación.
4. **Implementación mínima** para pasar los tests.
5. **Refactor** con los tests en verde.
6. **Verificación** (ver §8) y registro de la evidencia en el PR.

**Regla de oro SDD:** una capacidad solo se da por hecha cuando existe un test que la demuestra. No se documentan capacidades inexistentes (lección del `memory.py` de Aprendiz).

## 6. AI-TDD — AI-assisted Test-Driven Development

Bucle rojo-verde-refactor asistido por agente, con **revisión humana en los puntos de carga**:

1. **Rojo**: el agente escribe el test que expresa el criterio de aceptación; falla (aún no hay implementación).
2. **Revisión humana del test**: el desarrollador confirma que el test realmente prueba el comportamiento pedido y que **no está sesgado hacia la implementación** (el mayor riesgo de AI-TDD es un test que valida código auto-generado pero no el requisito).
3. **Verde**: implementar lo mínimo para pasar.
4. **Refactor**: mejorar el diseño sin cambiar comportamiento.
5. **Congelar como regresión**: el test queda en la suite permanente.

**Reglas AI-TDD:**
- Los tests se escriben **antes** que la implementación, desde el criterio de aceptación del PR.
- Tests deterministas y reproducibles; sin red en unit tests (fakes para RFB, LLM, SAP, RAG, memoria, MCP client).
- Un test que "prueba el mock" no cuenta: se prueban contratos y comportamiento, no implementaciones internas.
- Los fakes implementan el mismo contrato que el real (Protocol), nunca un doble ad-hoc que pase de casualidad.

## 7. Skills a usar por fase

| Fase del roadmap | Skills relevantes | Uso concreto |
| --- | --- | --- |
| Fase A/B (fundamentos, reutilización) | `safe-refactor`, `surgical-patch` | Migrar Aprendiz a `sap-mcp` preservando comportamiento; extraer `vnc/`, `llm.py`, `budget.py`, supervisor sin romper tests. |
| Fase C (descubrimiento) | `python-testing-patterns`, `test-driven-development` | Inventario de pantallas con tests offline (RFB falso). |
| Fase D (RAG) | `langchain-rag` | Ingestión, split, embeddings, store y evaluación de recuperación. |
| Fase E (memoria) | `deep-agents-memory` (si aplica), `investigate-first` | Verificar Engram/GentleAI con evidencia antes de integrar; StateBackend vs StoreBackend. |
| Fase F (loops) | `langgraph-fundamentals` (solo si se adopta), `writing-plans`/`executing-plans` | Máquina de estados explícita por defecto; LangGraph solo con justificación. |
| Fase G (seguridad) | `surgical-patch`, `test-driven-development` | Políticas de riesgo, aprobaciones, idempotencia, auditoría. |
| Fase H (MCP) | `mcp-builder` (ya en `.cursor/skills/`) | Diseño de tools tipadas, transporte, errores accionables, evaluación MCP. |
| Fase I (evaluación) | `verification-before-completion`, `verify-and-stop` | Evidencia antes de declarar éxito; no expandir alcance. |
| Todo el proyecto | `writing-plans` (al definir specs), `executing-plans` (al ejecutar) | Cada PR con plan/spec y checkpoints de revisión. |
| Migraciones de esquema | `migration` | Cambios en Knowledge Store reversibles y con prueba de preservación. |

## 8. Definición de "hecho" (Definition of Done) por PR

Un PR solo se considera terminado cuando:

1. Los tests nuevos y los existentes pasan (`pytest`, `ruff`).
2. Cada criterio de aceptación del PR tiene al menos un test que lo demuestra.
3. La evidencia se registra (salida de test/command) sin maquillar.
4. `docs/decisions.md` registra cualquier decisión no obvia tomada en el PR.
5. No se añade complejidad no pedida (sin frameworks/servicios extra sin ADR).
6. El PR es pequeño: implementable, revisable y testeable de forma independiente.

## 9. Anti-patrones prohibidos

- ❌ Escribir implementación antes que el test que la especifica.
- ❌ "Probar el mock" en lugar del contrato.
- ❌ PR genéricos ("implementar todo el RAG", "crear el agente autónomo").
- ❌ Documentar una capacidad sin test que la respalde.
- ❌ Coordenadas fijas como identidad de un control.
- ❌ Tratar la memoria/documentación como autorización para ejecutar.
- ❌ Declarar éxito sin señal de verificación independiente.
- ❌ Reintentos ciegos de escrituras tras timeout.
- ❌ Que el contenido de SAP o de la documentación modifique políticas.
