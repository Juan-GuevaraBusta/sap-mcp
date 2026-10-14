# Auditoría del repositorio previo — Aprendiz (`frontier-hackathon`)

Este documento audita el código ya construido en `hackathons/` (repositorio `JuanMCanchala/frontier-hackathon`, rama "equipo") para decidir qué se reutiliza, qué se reescribe y qué errores no se repiten en `sap-mcp`.

## 1. Qué se auditó

Los cinco directorios de `hackathons/` apuntan al **mismo repositorio remoto** en commits distintos:

| Directorio local | Commit head | Rol en la auditoría |
| --- | --- | --- |
| `frontier-hackathon-equipo` | `56afa80` | **Versión canónica y más completa** (README y DECISIONES actualizados al 12-10). Base de la auditoría. |
| `frontier-gate-v2` | `bec9eac` | Rama con mejoras del gate. Idéntica estructura; no aporta componentes nuevos. |
| `frontier-e3-efficient` | `863993a` | Rama de optimización de verificación tabular. |
| `frontier-mini-app` | `9f56ed3` | Aporta la mini app CRUD local (`apps/mini_crud/`) para medir generalización. |
| `frontier-parafrasis` | `74f4e51` | Aporta `eval/parafrasis/` (redacciones alternativas). |

**Conclusión de alcance:** auditar `frontier-hackathon-equipo` es suficiente; el resto son forks del mismo árbol en puntos distintos de la historia.

## 2. Arquitectura de Aprendiz (resumen)

Servicio HTTP siempre encendido que ejecuta tareas en lenguaje natural sobre un escritorio VNC 1280×800 con apps que nunca ha visto:

- **Entrada:** `FastAPI` con `GET /health`, `POST /tasks` (responde `task_id` < 2 s), `GET /tasks/{id}`.
- **Supervisor** (`tasks.py` + `store.py` + `lease.py`): lock por escritorio, watchdog con deadline monotónico, revocación de lease, estado de tareas en SQLite.
- **Runner** (`agent/runner.py`): conecta, congela el plan, resuelve parámetros, ejecuta, verifica, resume.
- **Ciclo del agente** (`agent/episode.py`): un único punto de despacho (`_dispatch`) para todo evento; clasifica → autoriza → ejecuta → detecta.
- **Controles de seguridad:** clasificador de escrituras, compuerta de escritura, detector de efectos, verificador, regla de texto, redactor determinista.
- **Driver RFB propio** (`vnc/`): RFB 3.8 sobre websocket, framebuffer en memoria, clic con duración, espera de estabilidad.

## 3. Inventario de reutilización

| Componente | Ubicación | ¿Reutilizable en sap-mcp? | Observaciones |
| --- | --- | --- | --- |
| Driver RFB/VNC | `src/aprendiz/vnc/` | **Sí, como adaptador RFB** | RFB 3.8, websocket, lease, release_all. Solo encoding raw; sin compresión. El límite de resolución 1280×800 lo impone `runner.py`, no el driver. |
| Llm client + presupuesto | `agent/llm.py`, `agent/budget.py` | **Sí** | Protocolo `Llm`, timeout, reintentos acotados, reserva de costo antes de cada llamada. Acoplado a OpenRouter (hay que abstraer proveedor). |
| Schemas cerrados | `agent/schemas.py`, `agent/structured.py` | **Sí (patrón)** | Pydantic `extra="forbid"`, validación de salida de modelos con reintento. |
| Plan congelado | `agent/planner.py`, `agent/schemas.py` | **Sí (concepto)** | El plan sale solo del texto, antes de la primera captura. Extensible a "operación empresarial". |
| Compuerta de escritura | `agent/gate.py` | **Sí (núcleo de seguridad)** | Reglas en código + auditor de otra familia de modelos; negar por defecto. |
| Clasificador de escrituras | `agent/classifier.py` | **Sí** | Recorte 240×120 sin historial; lo ambiguo = compromiso. |
| Detector de efectos | `agent/detector.py` | **Sí** | Segunda línea; pixel-diff + modelo ante señal de persistencia. |
| Verificador | `agent/verifier.py` | **Sí** | No declara éxito sin confirmación visible; relectura en modo lectura. |
| Resumen determinista + redacción | `agent/summary.py`, `redact.py` | **Sí** | El resumen lo arma código, no un modelo; filtro de secretos. |
| Regla de texto | `agent/textrule.py` | **Sí** | Solo se teclea texto de la tarea, del plan o calculado por código. |
| Cálculo de fechas en código | `agent/hoy.py` | **Sí** | Gramática cerrada `hoy_app±N`; no confía el calendario al modelo. |
| Lectura de tablas en código | `agent/table_reader.py` | **Parcial** | Conteo/suma agregados en código; útil para verificación de listas SAP. |
| Supervisor (lock + watchdog + lease) | `tasks.py`, `store.py`, `vnc/lease.py` | **Sí (base del orquestador)** | Patrón de tareas de larga duración, cancelación y cierre ordenado. |
| Trazas | `agent/trace.py` | **Sí** | Traza local redactada por tarea (`resumen.json`, `pasos.jsonl`). |
| Harness de evaluación | `eval/harness.py`, `eval/scoring.py`, `eval/schema.py` | **Sí (patrón)** | Evaluación reproducible, esquema estricto, reglas puras. |
| Monitor de incidentes | `eval/incidente.py`, `eval/vigilancia.py` | **Sí (concepto)** | Detección de cambio de app por diff de píxeles. |
| Suite de tests offline | `tests/` | **Sí (patrón)** | RFB falso, runners falsos, sin red. |
| Mini app CRUD local | `apps/mini_crud/` | **Sí (banco de pruebas)** | Segundo layout para medir generalización sin SAP real. |

## 4. Qué se hizo bien (patrones a conservar)

1. **Un único punto de despacho de eventos** (`_dispatch` en `episode.py`): ningún evento llega al driver sin pasar por clasificación y autorización. Esto evita caminos laterales inseguros.
2. **Plan congelado antes de la primera captura**: la intención y las escrituras permitidas se fijan solo con el texto de la tarea. La pantalla (dato no confiable) nunca amplía el plan. Defensa directa contra inyección de instrucciones.
3. **Negar por defecto en escrituras**: todo clic/tecla que pueda comprometer es candidato a escritura; lo ambiguo se trata como compromiso; un auditor de otra familia de modelos decide contra el plan.
4. **Verificación independiente del actor**: el actor propone, el verificador manda; sin confirmación visible no hay éxito declarado; el resumen lo arma código determinista (nunca un modelo).
5. **Presupuesto y deadlines duros**: reserva de costo antes de cada llamada, deadline monotónico, watchdog, revocación de lease y cierre ordenado antes de publicar estado. Idempotencia parcial: nunca repetir una escritura sin efecto visible.
6. **Schemas cerrados y tipado en fronteras**: `extra="forbid"`, validación de salida de modelos con reintento, errores explícitos.
7. **Evaluación que replica al evaluador real**: harness con esquema estricto, reglas de scoring puras, presupuesto de la key, resultados redactados y fuera de git.
8. **Cálculo en código donde el modelo se equivoca**: fechas (`hoy.py`), conteos/sumas (`table_reader.py`), formato de respuesta (`summary.py`).
9. **Generalización medida, no supuesta**: mini app con otro layout y etiquetas para detectar sobreajuste.
10. **Observabilidad sin acoplar la ruta crítica**: traza local redactada; exportador a Langfuse opcional y que nunca tumba la tarea.
11. **Disciplina de proceso**: `AGENTS.md` claro, `DECISIONES.md` como ADR, commits convencionales, PR obligatorio, sin force push.

## 5. Qué se hizo mal o quedó incompleto (errores a no repetir)

1. **Sin capa de abstracción de interacción**: el loop está acoplado al driver VNC. El `product_context.md` exige adaptadores intercambiables (RFB, Playwright, UI Automation, APIs SAP) tras un contrato común.
2. **Resolución hardcodeada 1280×800**: `runner.py` rechaza cualquier otra resolución y `schemas.py` valida coordenadas contra `SCREEN_WIDTH/HEIGHT` fijos. SAP GUI puede variar de resolución/DPI.
3. **Memoria anunciada pero no implementada**: `DECISIONES.md` habla de "memoria por app" y existe un `__pycache__/memory.cpython-313.pyc`, pero **no hay `memory.py`** y `store.py` solo guarda estado de tareas (`tasks`), no conocimiento por app. La "memoria" real fue un supuesto, no un componente. Lección: no documentar capacidades que no existen.
4. **Sin registro estructurado de conocimiento**: no hay entidades (`Installation`, `Screen`, `UIElement`, `Procedure`, `Evidence`, `Hypothesis`) ni estados de conocimiento (`discovered`, `validated`, `stale`…). Aprendiz "aprende" dentro de una tarea, no entre sesiones de forma versionada.
5. **Sin RAG ni investigación documental**: no consulta documentación oficial; todo el conocimiento viene de la pantalla o del modelo.
6. **Sin loop de descubrimiento sistemático**: la decisión fue "exploración bajo demanda" por presión de tiempo del hackathon. Para SAP se requiere inventario progresivo y mapa de navegación.
7. **Sin experimentación controlada formal**: hay pruebas implícitas (rellenar, verificar), pero no un `Experiment` con hipótesis, precondiciones, resultado esperado y registro de evidencia.
8. **Sin MCP**: expone una API HTTP propia (`/tasks`), no herramientas MCP tipadas.
9. **Proveedor LLM acoplado**: precios de OpenRouter hardcodeados a mano; un cambio de modelo exige mantener la tabla. Falta una abstracción de proveedor con precios dinámicos o contrato declarado.
10. **`episode.py` monolítico (~1.000 líneas)**: difícil de extender hacia los cuatro loops especializados (discovery, research, experimentation, execution).
11. **Sin aprobación humana**: la compuerta autoriza o niega, pero no hay flujo de pausa + aprobación para operaciones de alto riesgo (crear/contabilizar/enviar/eliminar en SAP).
12. **Detección de cambio frágil**: el monitor por diff de píxeles tuvo falsos positivos por estado de pantalla (texto seleccionado, clic de menú perdido). Necesita distinguir "la app cambió" de "la navegación falló" y no confundir cambio visual con cambio semántico.
13. **Encoding RFB sin compresión**: solo `raw` + `DesktopSize`; más ancho de banda y sin `Cursor`, `ZRLE`/`Tight`. Aceptable para MVP local, insuficiente para sesiones SAP largas.
14. **Lock solo dentro del servicio**: un operador externo sin lock interfirió en el escritorio compartido. Para SAP el lock debe ser una invariante del orquestador, no solo del harness.

## 6. Brechas frente a la visión del producto

| Capacidad exigida por `product_context.md` | Estado en Aprendiz |
| --- | --- |
| Descubrimiento progresivo de pantallas/elementos | ❌ No existe (solo exploración bajo demanda) |
| Investigación documental (RAG) | ❌ No existe |
| Experimentación controlada formal | ⚠️ Implícita |
| Memoria de experiencias (Engram/GentleAI) | ⚠️ Anunciada, no implementada |
| Conocimiento estructurado y versionado | ❌ No existe |
| Ejecución de workflows multi-etapa | ⚠️ Parcial (tareas de una app) |
| Verificación independiente | ✅ Sólida |
| Política/riesgo/aprobación humana | ⚠️ Solo gate binario, sin aprobación |
| Exposición MCP | ❌ HTTP propio |
| Adaptadores intercambiables | ❌ Solo VNC |
| Auditoría y redacción | ✅ Sólida |
| Evaluación reproducible | ✅ Sólida |

## 7. Qué se reutiliza tal cual vs. qué se reescribe

**Reutilizar tal cual (importar como base):**
- Driver VNC (`vnc/`), lease y release_all.
- Llm client + presupuesto (`llm.py`, `budget.py`).
- Schemas cerrados y parseo de salidas (`schemas.py`, `structured.py`).
- Redacción de secretos (`redact.py`).
- Resumen determinista y cálculo de fechas/tablas (`summary.py`, `hoy.py`, `table_reader.py`).
- Patrón de supervisor: lock, watchdog, deadline, cierre ordenado (`tasks.py`, `store.py`, `lease.py`).
- Patrón de trazas y de harness de evaluación (`trace.py`, `eval/`).

**Adaptar (reescribir la interfaz, conservar la lógica):**
- `gate.py`, `classifier.py`, `detector.py`, `verifier.py`: extenderlos de "escritura sí/no" a **clases de riesgo** (observación, navegación, consulta, preparación, creación, compromiso, aprobación, destructiva).
- `planner.py`: pasar de "plan de tarea" a "plan de operación empresarial" con precondiciones y verificación.
- `episode.py`: partirlo en los cuatro loops especializados del producto.

**Construir desde cero:**
- Capa de abstracción de interacción (contrato común + adaptadores).
- Discovery Engine y registro estructurado de conocimiento.
- Research Engine y pipeline RAG.
- Experimentation Engine.
- Integración de memoria (Engram/GentleAI, tras verificación).
- Capa de política/riesgo/aprobación/auditoría.
- Servidor MCP.

## 8. Lecciones que condicionan el roadmap

1. **No documentar capacidades que no existen** (el caso `memory.py`): cada PR del roadmap debe terminar con una prueba que demuestre la capacidad, no con una promesa.
2. **Interfaces antes que motores**: el contrato de interacción y el modelo de conocimiento van primero; los motores se enchufan después.
3. **El conocimiento es dato versionado, no variable de sesión**: exige entidades, estados y procedencia desde el primer día.
4. **Seguridad del lado del servidor y por capas**: el prompt no autoriza; el contenido de SAP es dato no confiable.
5. **Evaluar contra un evaluador espejo**: el harness de Aprendiz fue decisivo para no autoengañarse; sap-mcp necesita el mismo rigor desde la Fase I.
