---
pr: PR-XXX
title: <título corto>
status: spec_draft # spec_draft | spec_approved | red | tests_approved | green | verified | reviewed | ready | blocked
depends_on: [] # p. ej. [PR-001a]
blocked_by_decisions: [] # números de docs/decisions.md, p. ej. [2]
branch: pr-xxx-<slug>
write_paths: # rutas exclusivas de este PR; deben ser disjuntas de los PR paralelos
  - src/sap_mcp/<módulo>/
  - tests/<módulo>/
---

# PR-XXX · <título>

## Objetivo
<Una o dos frases. Qué capacidad existe al terminar.>

## Contexto
<Referencias: docs/roadmap.md PR-XXX, product_context.md §…, docs/audit-aprendiz.md §…>

## Fuera de alcance
- <Lo que explícitamente no se hace aquí y en qué PR se hace.>

## Contrato
<Tipos, firmas, schemas y Protocols. Solo lo necesario para los AC.>

```python
# Firma propuesta, sin implementación
```

## Invariantes
- <Reglas que siempre deben cumplirse.>

## Errores
- <Qué entradas o estados producen qué error.>

## Acuerdos con PR paralelos
- <Contratos compartidos fijados antes de despachar. "Ninguno" si no aplica.>

## Criterios de aceptación

| AC | Criterio medible | Test |
| --- | --- | --- |
| AC-1 | <…> | `tests/<módulo>/test_<archivo>.py::test_<nombre>` |

## Dependencias nuevas
<Ninguna, o la lista con su ADR en docs/decisions.md.>

## Evidencia
<La rellena el Verifier con la salida literal de los comandos de AGENTS.md §6.>

## Revisión
<La rellena el Reviewer: hallazgos bloqueantes y no bloqueantes.>
