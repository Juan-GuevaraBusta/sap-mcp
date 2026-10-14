# sap-mcp

Servidor MCP (Model Context Protocol) que permite a agentes de IA descubrir, comprender, documentar y ejecutar operaciones en instalaciones SAP desconocidas, con percepción visual, RAG, memoria, experimentación controlada y verificación de resultados.

## Estado

Proyecto en etapa inicial: **auditoría del repositorio previo completada y roadmap definido. Sin código implementado todavía.**

La fuente de verdad del producto es [`product_context.md`](product_context.md). Todo lo demás deriva de ahí.

## Índice de documentación

| Documento | Contenido |
| --- | --- |
| [product_context.md](product_context.md) | Visión, alcance funcional, arquitectura conceptual, seguridad, métricas y definición de éxito del MVP. **No se modifica; es el contrato del producto.** |
| [docs/audit-aprendiz.md](docs/audit-aprendiz.md) | Auditoría del repositorio `frontier-hackathon` (Aprendiz): qué se reutiliza, qué se hizo bien, qué se hizo mal y qué no repetir. |
| [docs/architecture.md](docs/architecture.md) | Arquitectura objetivo, brechas respecto a la visión, decisiones técnicas pendientes y mapeo de reutilización. |
| [docs/standards.md](docs/standards.md) | Estándares de trabajo: convenciones de código, git, SDD, AI-TDD, skills y rules a usar en cada fase. |
| [docs/roadmap.md](docs/roadmap.md) | Roadmap técnico incremental: fases, PR ordenados, dependencias, criterios de aceptación y riesgos. |
| [docs/testing.md](docs/testing.md) | Estrategia de pruebas: AI-TDD, infraestructura offline, harness de evaluación y pruebas de seguridad. |
| [docs/validation.md](docs/validation.md) | Matriz de validación que traza cada requisito del `product_context.md` a PR y prueba medible. |
| [docs/decisions.md](docs/decisions.md) | Registro de decisiones (ADR) y decisiones abiertas pendientes de evidencia. |

## Reglas de oro

1. **No se implementa código hasta que un PR del roadmap lo pida explícitamente.**
2. **No se hace push ni commit sin pedido explícito.**
3. Toda decisión relevante se registra en `docs/decisions.md`.
4. Toda afirmación de éxito se respalda con una prueba reproducible (`docs/validation.md`).
