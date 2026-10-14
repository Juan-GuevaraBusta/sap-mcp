# Registro de decisiones (ADR) — sap-mcp

Formato y decisiones abiertas. Cada decisión no obvia se registra aquí **antes** de implementar el PR que la asume.

## Formato

```text
## <fecha hora> — <decisión>
Contexto: <qué problema había>
Decisión: <qué se eligió>
Descartado: <alternativa> — <por qué no>
Consecuencias: <qué se vuelve más fácil / más difícil>
```

## Decisiones ya tomadas (desde la auditoría y el diseño)

### 2026-10-13 — Reutilizar Aprendiz como semilla, no reescribir desde cero
- **Contexto:** existe un repositorio previo con driver RFB, LLM, presupuesto, supervisor, gate, verificación y harness probados.
- **Decisión:** importar los componentes reutilizables (ver `audit-aprendiz.md` §7) y **adaptar** los que acoplan el núcleo a VNC o a un solo proveedor. No reescribir lo que funciona.
- **Descartado:** empezar desde cero — perdería meses de trabajo validado. Copiar sin cambios — arrastraría el acoplamiento a VNC, la resolución fija y el HTTP propio.
- **Consecuencias:** arranque rápido; riesgo de heredar deuda (mitigado con la capa de abstracción en PR-002 y la partición de `episode.py`).

### 2026-10-13 — Documentar solo capacidades con test
- **Contexto:** en el repo previo se documentó "memoria por app" sin que existiera `memory.py` ni test.
- **Decisión:** ninguna capacidad se documenta como existente sin un test que la demuestre (DoD en `standards.md` §8).
- **Descartado:** documentar intenciones como capacidades — genera falsa confianza.
- **Consecuencias:** el roadmap y la validación quedan anclados a evidencia.

### 2026-10-13 — Máquina de estados explícita como orquestador por defecto
- **Contexto:** `product_context.md` §4.2 permite grafo de estados o máquina de estados explícita, y §14.12 exige complejidad justificada.
- **Decisión:** máquina de estados explícita reutilizando el supervisor de Aprendiz (lock/watchdog/lease). No adoptar LangGraph salvo que surja una necesidad real de grafo.
- **Descartado:** LangGraph desde el inicio — añade un framework sin evidencia de necesidad en el MVP.
- **Consecuencias:** menos dependencias; si aparecen workflows complejos, se reevalúa con ADR.

## Decisiones abiertas (requieren evidencia antes del PR indicado)

| # | Decisión | PR que la necesita | Evidencia requerida | Dueño |
| --- | --- | --- | --- | --- |
| 1 | **Stack del MCP server**: Python (FastMCP/SDK oficial) vs. TypeScript como frontera delgada | PR-021 | Recomendación del skill `mcp-builder` (TS) vs. reutilización del núcleo Python; requisitos del cliente MCP objetivo. | Equipo |
| 2 | **Knowledge Store**: SQLite vs. Postgres | PR-003 | Volumen esperado, concurrencia, requisitos de despliegue. | Equipo |
| 3 | **RAG store**: SQLite FTS5 + embeddings vs. vector store dedicado | PR-011 | Volumen de documentos, latencia y coste de embeddings. | Equipo |
| 4 | **Engram y GentleAI**: qué memoria usa cada uno, si se integran | PR-013 | Repos, interfaces, persistencia, licencias, solapamientos (spike). | Equipo |
| 5 | **Proveedor LLM**: cuál(es) y cómo se abstrae el precio | PR-006 | Disponibilidad de proveedores, coste, soporte de salida estructurada. | Equipo |
| 6 | **Entorno SAP de pruebas**: sandbox oficial vs. app de práctica vs. cliente | PR-024 | Acceso, permisos, representatividad, coste. | Equipo |
| 7 | **Orden de adaptadores**: RFB → Playwright → UIA → APIs | PR-004 y siguientes | Qué interfaz usa el entorno SAP objetivo. | Equipo |
| 8 | **Política de lock**: desplazar vs. encolar tareas sobre la misma sesión | PR-005 | Comportamiento esperado del cliente MCP ante concurrencia. | Equipo |

**Regla:** ninguna decisión abierta se resuelve por suposición; se cierra con evidencia en su PR y se registra aquí con el formato ADR.
