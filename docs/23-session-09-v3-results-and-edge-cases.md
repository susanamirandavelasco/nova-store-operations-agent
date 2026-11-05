# Session 9: V3 evidence validation

Observed user-run V3 evaluation on the 12 previously used development questions:
- Exact classifications: 10/12.
- TP=6, FP=1, FN=1, TN=4; precision=0.857, recall=0.857.
- Case 03: expected SUPPORTED_YES, obtained INSUFFICIENT. Policy explicitly starts the 30 natural days after purchase.
- Case 07: expected INSUFFICIENT, obtained SUPPORTED_NO. A calendar month is not always equivalent to 30 natural days; the question lacks specific dates.

This is not an independent benchmark. V3 remains experimental and disconnected from the workflow.

Eight additional pre-labeled edge questions are in nova/evaluate_evidence_v3_edge.py. Labels were set before any live run. The cases target start-of-period reasoning, unsupported exceptions, calendar-month ambiguity, and overly broad claims about opened items.

Run on branch feature/session-09-v3-evaluation:

    git pull origin feature/session-09-v3-evaluation
    python -m pytest -q
    python -m nova.evaluate_evidence_v3_edge
    python -m nova.evaluate_evidence_v3_edge --live

Only the last command calls OpenAI (8 paid calls). Review each incorrect verdict. Do not change labels after seeing predictions, modify V3 prompt, or integrate the verifier during this experiment.

Decision pending: assess results before choosing whether any integration is justified.
