# Session 8 — Semantic policy retrieval (increment 2)

This increment adds an **optional in-memory semantic retriever** alongside the existing lexical baseline. It does not replace the current web-chat retriever.

## Components
- `Embedder` protocol for dependency injection.
- `SemanticPolicyRetriever`: embeds the two fictional policy passages, compares query embedding with cosine similarity, returns source-attributed text.
- Minimum similarity and near-tie margin are conservative demonstration heuristics, **not calibrated confidence probabilities**.
- `OpenAIEmbedder` uses `text-embedding-3-small` only when explicitly instantiated; requires `openai` and `OPENAI_API_KEY` and incurs API charges.
- Deterministic fake-embedding tests check routing, abstention, ties and invalid vectors without network calls.

## Run tests
```bash
python -m pytest -q tests/test_semantic_policy_retrieval.py
python -m pytest -q
```

## Limitations and next steps
Fake vectors only validate the algorithm; they do **not** demonstrate actual semantic model quality. Real-world similarity thresholds require an evaluation set with supported and unsupported queries, including Spanish paraphrases. No vector database, persistent index, grounded LLM generation, or production retrieval guarantees are included. Next: evaluate the real embedder against lexical retrieval and decide when to opt into the semantic retriever in the workflow.
