# Sesión 8 — Recuperación de políticas (incremento 1)

## Objetivo
Iniciar la capacidad de preguntas sobre políticas de NovaRetail sin permitir que el contenido recuperado modifique la evaluación determinista de devoluciones.

## Alcance actual
- Dos pasajes **ficticios**, versionables en código, con identificadores de fuente: `POL-RET-001#plazo` y `POL-RET-001#estado`.
- `PolicyRetriever.answer(question)` utiliza coincidencias léxicas conservadoras, cita el pasaje elegido y se abstiene ante preguntas sin evidencia.
- Ante coincidencias empatadas, solicita precisar la consulta.
- Pruebas unitarias para fuente, abstención, ambigüedad y separación respecto a decisiones de elegibilidad.

**Esto todavía no es RAG:** no hay embeddings, base vectorial, generación por LLM ni integración en el flujo conversacional. No presentar este prototipo como búsqueda semántica ni como cobertura completa de políticas.

## Próximos incrementos
1. Integrar consultas de políticas al `WorkflowService` con inyección de dependencias y protección del estado de devoluciones suspendidas.
2. Crear corpus de políticas versionado, fragmentación y metadatos de procedencia.
3. Sustituir recuperación léxica por recuperación semántica, medir precisión y abstenciones.
4. Añadir generación fundamentada en pasajes, validación de citas y evaluación de respuestas.

## Prueba local
```bash
python -m pytest -q tests/test_policy_retrieval.py
python -m pytest -q
```

## Integración al workflow — validación funcional

- `WorkflowService` acepta `policy_retriever` inyectable; el modo demo lo habilita sin API key.
- Una consulta explícita sobre políticas devuelve texto y referencia; cuando no hay evidencia, se abstiene sin inventar una cita.
- Si hay devolución activa, la consulta suspende el proceso y conserva orden provisional y paso pendiente.
- `retomar` responde según el paso guardado, en lugar de pedir nuevamente un número de orden ya registrado.
- **Evidencia en Codespaces:** 167 pruebas aprobadas y 1 warning conocido antes del ajuste final del mensaje de reanudación. La usuaria confirmó visualmente en el chat Docker la consulta citada y la reanudación con pregunta por el producto. La suite completa posterior al ajuste debe verificarse antes del merge.

## Criterio de cierre de este incremento
Recuperación léxica e integración de políticas con referencias, sin alterar el motor determinista de elegibilidad. La **sesión 8 RAG completa sigue pendiente** de recuperación semántica, generación fundamentada y evaluación.
