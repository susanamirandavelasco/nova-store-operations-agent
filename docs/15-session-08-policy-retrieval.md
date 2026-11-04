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
