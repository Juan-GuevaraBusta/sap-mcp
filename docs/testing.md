# Estrategia de pruebas — sap-mcp

Cómo se prueba el sistema con **AI-TDD**, qué niveles de test existen, qué infraestructura offline se usa y cómo se evalúa el MVP sin autoengañarse.

## 1. Filosofía

1. **Evidencia antes que afirmación**: ninguna capacidad se declara terminada sin un test reproducible que la demuestre.
2. **Tests desde la spec**: cada PR del roadmap define criterios de aceptación medibles; los tests nacen de esos criterios (SDD + AI-TDD).
3. **Offline por defecto**: los tests unitarios y de integración no tocan red, SAP, LLM ni MCP reales; usan fakes que implementan el mismo contrato.
4. **Evaluación espejo**: el harness replica al evaluador real y es al menos tan estricto (lección del `eval/schema.py` de Aprendiz).

## 2. Pirámide de pruebas

| Nivel | Qué prueba | Infraestructura | PR asociado |
| --- | --- | --- | --- |
| **Unit** | Schemas, estados, reglas, redacción, presupuesto, fechas, tablas. | Sin red; puro. | PR-001..009, PR-018 |
| **Contract** | Cada adaptador/engine implementa su Protocol; un fake que "prueba el mock" no cuenta. | Protocol + fakes tipados. | PR-002..006 |
| **Integration (offline)** | Flujo de un loop completo con adaptador falso y LLM falso. | RFB falso (de Aprendiz), LLM falso, KS en `:memory:`, RAG falso. | PR-007..020 |
| **MCP** | Tools tipadas, validación, authz, tareas largas. | Cliente MCP falso (unit) y real (interop). | PR-021..023 |
| **E2E / Harness** | Workflow SAP representativo completo, fallos e interrupciones. | Entorno SAP sandbox + harness. | PR-024..025 |

## 3. AI-TDD en la práctica

Cada PR sigue el bucle (detallado en `standards.md` §6):

1. Escribir el test que expresa el criterio de aceptación → **falla**.
2. **Revisión humana del test** (punto de carga obligatorio): confirmar que prueba el requisito y no la implementación auto-generada.
3. Implementar lo mínimo → **verde**.
4. Refactor con tests en verde.
5. Congelar el test como regresión.

**Anti-patrón detectado en el repo previo:** un componente (`memory`) que se documentó como existente sin test ni código fuente. Regla: **sin test = no existe**.

## 4. Infraestructura offline reutilizable

Tomada de Aprendiz y extendida:

| Fake | Propósito |
| --- | --- |
| Servidor RFB falso (`tests/fake_server.py` en Aprendiz) | Probar el adaptador RFB sin un escritorio real: handshake, framebuffer, eventos. |
| LLM falso (implementa `Llm`) | Respuestas deterministas por prompt; simula timeout/error/JSON inválido. |
| Adaptador SAP falso (implementa `InteractionAdapter`) | Probar Discovery/Execution sin SAP: devuelve `Observation` y `Effect` controlados. |
| RAG falso | Recupera fragmentos fijos con citas para probar el Research Loop. |
| Knowledge Store en `:memory:` | Persistencia determinista por test, sin archivos. |
| Cliente MCP falso | Invoca tools y valida schemas/errores sin transporte real. |
| Reloj y budget inyectados | Deadlines y coste deterministas. |

Regla: **un fake implementa el Protocol real**; nunca un doble ad-hoc que pase de casualidad.

## 5. Pruebas por dominio

### 5.1 Conocimiento (Fase B-C)
- CRUD y versionado (`KnowledgeRevision` inmutable).
- Transiciones de estado: `validated` exige `Evidence`; contradicción → `conflicted`; cambio → `stale`.
- Aislamiento por `Installation`: un elemento de la instalación A nunca se devuelve para B.

### 5.2 Descubrimiento (Fase C)
- Inventario desde `Observation` fija: elementos persistidos con contexto y método de detección.
- Detección de cambios: tema distinto → `stale`; navegación fallida → no invalida; texto seleccionado (falso positivo conocido) → no invalida.
- Identidad de control estable sin coordenadas fijas.

### 5.3 RAG (Fase D)
- Procedencia obligatoria (sin URL/versión no se indexa).
- Fuente interna ≠ oficial.
- Recuperación contextual por producto/versión.
- Relevancia medida sobre un set dorado pequeño.

### 5.4 Memoria (Fase E)
- Recuperar experiencia de la misma instalación.
- No contaminar otras instalaciones.
- Expiración/invalidación.

### 5.5 Loops (Fase F)
- Selección de loop correcto (discover/research/experiment/execute).
- Límites: presupuesto, pasos, timeout, ciclos.
- Recuperación sin reintentos ciegos de escrituras.
- Execution: éxito solo con verificación; estados finales explícitos (§3.5).

### 5.6 Seguridad (Fase G) — casos de `product_context.md` §12.4
| Caso | Test |
| --- | --- |
| Botón con efecto desconocido | Clasificado como compromiso; negado por defecto. |
| Acción irreversible | Requiere aprobación; sin permiso no se ejecuta. |
| Entidades duplicadas/ambiguas | Gate deniega y nombra el dato distintivo. |
| Mensaje malicioso en pantalla | No modifica política ni plan. |
| Documentación contradictoria | `conflicted`, conserva incertidumbre. |
| Cambio de versión | `stale` con evidencia. |
| Cambio de resolución/diseño | Adaptador acepta resolución dinámica; sin coordenadas fijas. |
| Timeout tras escritura | Reconciliación: comprobar estado antes de reintentar. |
| Permisos insuficientes | Bloqueado con estado explícito. |
| Fallo multi-paso | Estado persistente y recuperación. |
| Reintento de operación completada | Idempotencia por execution id. |

### 5.7 MCP (Fase H)
- Schemas de tools cerrados; argumento inválido → error accionable.
- Dos starts idénticos no duplican.
- Disponibilidad de tool ≠ autorización.
- Interoperabilidad con cliente MCP real (PR-023).

## 6. Harness de evaluación (Fase I)

Portar y endurecer el patrón de Aprendiz:

1. **Esquema estricto antes de enviar** (no enviar pruebas mal escritas).
2. **Reglas de scoring puras** (funciones sin estado).
3. **Presupuesto de la key** consultado antes de cada tarea.
4. **Secretos solo por entorno**; resultados redactados y fuera de git.
5. **Métricas por corrida**: éxito, falsos éxitos, acciones destructivas, duplicados, p50/p95 de tiempo, coste, latencia, seguridad (§12 del product_context).
6. **Línea base**: un runner que siempre responde `fallida` como piso de comparación.

## 7. Cobertura mínima exigida

- 100 % de los criterios de aceptación de cada PR con al menos un test.
- Los 15 criterios del MVP (§16) trazados en `docs/validation.md`.
- Los 11 casos de seguridad (§12.4) con test reproducible.
- CI en cada PR: `pytest -q` + `ruff check` (+ `ruff format --check`).

## 8. Cómo verificar sin autoengañarse

1. Ejecutar el comando real y **mostrar la salida exacta** (sin maquillar).
2. El harness replica al evaluador; un verde en fakes no basta para el E2E.
3. Falsos éxitos y acciones destructivas se miden explícitamente, no se asumen en cero.
4. Limitaciones documentadas en `docs/limitations.md` antes de ampliar alcance.
5. Skill `verification-before-completion` antes de declarar cualquier PR "terminado".
