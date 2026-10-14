# Matriz de validación — sap-mcp

Cómo se valida que lo construido cumple `product_context.md`. Traza cada requisito del producto a un PR del roadmap y a una prueba medible. **Esta es la fuente de verdad de "terminado" del MVP.**

## 1. Definición concreta del MVP

El MVP demuestra el ciclo completo de aprendizaje y ejecución sobre **un entorno SAP autorizado de alcance controlado** (sandbox o app equivalente de práctica):

> Conectar → observar una pantalla desconocida → identificar elementos → investigar uno con documentación → distinguir hipótesis/observaciones/conocimiento validado → ejecutar una prueba segura autorizada → registrar evidencia y conocimiento persistente → recuperarlo en una sesión posterior → preparar y ejecutar un workflow multi-paso con autorización → verificar el resultado con evidencia fiable → recuperarse de fallos sin reintentos ciegos → detectar al menos un cambio que invalide conocimiento → exponer todo vía MCP → producir trazas auditables.

## 2. Matriz de éxito del MVP (`product_context.md` §16)

| # | Criterio de éxito §16 | PR que lo implementa | Prueba que lo demuestra | Umbral de aceptación |
| --- | --- | --- | --- | --- |
| 1 | Conectar a un entorno SAP autorizado | PR-004 | Test de adaptador RFB contra servidor falso + E2E sandbox | Handshake correcto; capacidades declaradas honestamente. |
| 2 | Observar una pantalla desconocida | PR-004, PR-007 | `observe` devuelve `Observation`; test de inventario | Captura/snapshot válido sin coordenadas fijas. |
| 3 | Identificar elementos interactivos | PR-007 | `discover_elements` persiste `UIElement` con contexto | Elementos recuperables con procedencia y tipo. |
| 4 | Investigar función de un elemento con documentación | PR-012 | Research Loop con RAG falso/dorado | Hipótesis con cita o incertidumbre explícita si no hay fuente. |
| 5 | Distinguir hipótesis/observaciones/conocimiento validado | PR-009 | Test de transiciones de estado | `validated` imposible sin `Evidence`. |
| 6 | Prueba segura y autorizada | PR-015 | Experimentation Loop con gate | Sin autorización no se ejecuta; solo lectura permitida. |
| 7 | Registrar evidencia y conocimiento persistente | PR-003, PR-007 | CRUD + versionado en KS | Persistencia y revisión verificadas. |
| 8 | Recuperar conocimiento en sesión posterior | PR-003, PR-014 | Test de recuperación entre "sesiones" (dos instancias) | Mismo `Installation` recupera; otra no. |
| 9 | Workflow multi-paso | PR-016 | Execution Loop contra adaptador falso multi-pantalla | Éxito solo con verificación; estados finales explícitos. |
| 10 | Controles de autorización | PR-018 | Test de políticas por riesgo | Observar ≠ activar; sin permiso no se ejecuta. |
| 11 | Verificación con evidencia fiable | PR-016, PR-020 | Verificación independiente (lectura posterior/API) | Sin señal de persistencia no hay éxito. |
| 12 | Recuperarse de fallos sin reintentos ciegos | PR-017, PR-019 | Test de timeout tras escritura | Reconciliación antes de repetir; sin duplicados. |
| 13 | Detectar cambios que invaliden conocimiento | PR-008 | Test de detección de cambio | Cambio real → `stale` con evidencia; navegación fallida no invalida. |
| 14 | Exponer capacidades vía MCP | PR-021..023 | Interop con cliente MCP real | Tools listadas, invocables y con errores accionables. |
| 15 | Trazas auditables | PR-020, PR-024 | Auditoría de una operación completa | Task, objetivo, plan, acciones, evidencia, resultado. |

## 3. Matriz de métricas (`product_context.md` §12)

| Métrica | Cómo se mide | Dónde |
| --- | --- | --- |
| Precisión en identificación de elementos | Set dorado de pantallas etiquetadas; comparación elemento a elemento. | PR-024 |
| Cobertura de elementos por pantalla | Elementos detectados / elementos del set dorado. | PR-024 |
| Precisión en clasificación de tipo de control | Confusión tipo real vs. detectado. | PR-024 |
| Calidad de relaciones de navegación | `NavigationEdge` correctas / totales. | PR-024 |
| Relevancia de recuperación documental | Recall/precisión sobre set dorado RAG. | PR-011 |
| Exactitud de citas | Cita resuelve al fragmento correcto. | PR-011 |
| Conclusiones con evidencia suficiente | Proporción de `validated` con `Evidence`. | PR-009 |
| Tasa de contradicciones no detectadas | Casos inyectados → `conflicted`. | PR-012 |
| Registros obsoletos identificados | Cambios inyectados → `stale`. | PR-008 |
| Contaminación entre instalaciones | Elemento de A nunca devuelto para B. | PR-003 |
| Workflows completados correctamente | Éxito verificado / totales. | PR-024 |
| Tasa de verificación satisfactoria | Verificados / ejecutados. | PR-024 |
| Duplicados generados | Contador explícito en harness. | PR-024 |
| Acciones no autorizadas | Contador explícito en harness. | PR-024 |
| Recuperación ante interrupciones | Fallos inyectados recuperados sin duplicados. | PR-025 |
| Tiempo y coste por workflow | Medición por corrida. | PR-024/025 |
| Resultados ambiguos correctamente reportados | Estados "desconocido/incompleto" vs. falsos éxitos. | PR-024 |

## 4. Matriz de seguridad (`product_context.md` §12.4)

Ver tabla completa en `testing.md` §5.6. Resumen de umbrales:

- **0 acciones no autorizadas** y **0 duplicados** en el harness (objetivo; cualquier incidencia se analiza y bloquea el merge).
- **Inyección no escala privilegios**: una pantalla con instrucciones maliciosas no altera el plan ni la política.
- **Timeout tras escritura nunca reintenta sin reconciliación**.

## 5. Guardrails de alcance (`product_context.md` §15)

Validación negativa: el MVP **no** debe contener ninguna de estas cosas. Revisión en la revisión final del MVP (PR-025):

- [ ] Sin interfaz conversacional propia.
- [ ] Sin limitación arquitectónica a un solo módulo/workflow.
- [ ] Sin servidor MCP que solo exponga APIs predefinidas.
- [ ] Sin agente por coordenadas memorizadas.
- [ ] Sin que el modelo otorgue sus propios permisos.
- [ ] Sin hipótesis guardadas como hechos.
- [ ] Sin Engram/GentleAI sin verificación.
- [ ] Sin todos los protocolos de interacción desde el día uno.
- [ ] Sin infraestructura distribuida innecesaria.
- [ ] Sin declarar éxito sin evidencia suficiente.
- [ ] Sin afirmar generalización sin evaluación representativa.

## 6. Trazabilidad producto → PR → test

Cada sección de `product_context.md` tiene dueño en el roadmap:

| Sección del producto | Fase/PR |
| --- | --- |
| §3.1 Descubrimiento | C (PR-007..009) |
| §3.2 Investigación | D (PR-010..012) |
| §3.3 Experimentación | F (PR-015) |
| §3.4 Ejecución | F (PR-016) |
| §3.5 Verificación | F (PR-016), G (PR-020) |
| §4 Arquitectura | B (PR-002..006), F (PR-017) |
| §5 Interacción | B (PR-002, PR-004) |
| §6 Memoria | E (PR-013..014) |
| §7 RAG | D (PR-010..011) |
| §8 Conocimiento | B (PR-003), C (PR-009) |
| §9 Loops | F (PR-015..017) |
| §10 MCP tools | H (PR-021..023) |
| §11 Seguridad | G (PR-018..020) |
| §12 Métricas | I (PR-024..025) |
| §13 Reutilización Aprendiz | B (PR-001, PR-004..006) |
| §16 MVP | Todo + esta matriz |

## 7. Criterio de cierre del MVP

El MVP se da por cerrado cuando:

1. Los 15 criterios de §16 tienen prueba en verde **ejecutada** (salida real adjunta).
2. Las métricas de §12 se han medido y registrado.
3. Los 11 casos de seguridad de §12.4 tienen test reproducible.
4. La lista de guardrails §15 está marcada sin violaciones.
5. `docs/limitations.md` documenta lo que **no** se probó (cobertura real, no supuesta).
