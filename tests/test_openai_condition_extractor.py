"""Offline tests for the opt-in LLM condition adapter."""
import json
import sys
from types import SimpleNamespace

import pytest

from nova.__main__ import build_service
from nova.openai_condition_extractor import OpenAIConditionExtractor
from nova.product_condition import ProductCondition


def fake_openai(monkeypatch, payload):
    calls = []
    class Client:
        def __init__(self):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(choices=[
                SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))
            ])
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=Client))
    return calls


@pytest.mark.parametrize(("condition", "expected"), [
    ("SEALED", ProductCondition.SEALED),
    ("OPENED", ProductCondition.OPENED),
    ("DAMAGED", ProductCondition.DAMAGED),
    ("UNKNOWN", ProductCondition.UNKNOWN),
])
def test_valid_structured_response(monkeypatch, condition, expected):
    calls = fake_openai(monkeypatch, {"condition": condition, "needs_clarification": False})
    result = OpenAIConditionExtractor().extract("El producto está abierto")
    assert result.condition == expected
    assert not result.needs_clarification
    assert len(calls) == 1
    assert calls[0]["response_format"]["type"] == "json_schema"


def test_hedging_does_not_call_llm(monkeypatch):
    calls = fake_openai(monkeypatch, {"condition": "SEALED", "needs_clarification": False})
    result = OpenAIConditionExtractor().extract("Parece que está sellado")
    assert result.needs_clarification
    assert result.condition is None
    assert calls == []


@pytest.mark.parametrize("payload", [
    {"condition": "SEALED", "needs_clarification": "false"},
    {"condition": "INVALID", "needs_clarification": False},
    {"condition": None, "needs_clarification": False},
    {"condition": "SEALED", "needs_clarification": True},
])
def test_invalid_or_uncertain_response_never_advances(monkeypatch, payload):
    fake_openai(monkeypatch, payload)
    result = OpenAIConditionExtractor().extract("Está en su empaque original")
    assert result.needs_clarification
    assert result.condition is None


def test_cli_opt_in(tmp_path):
    default = build_service(demo=True, db_path=str(tmp_path / "a.db"))
    llm = build_service(demo=True, llm_condition=True, db_path=str(tmp_path / "b.db"))
    assert type(default.condition_extractor).__name__ == "RuleBasedConditionExtractor"
    assert isinstance(llm.condition_extractor, OpenAIConditionExtractor)


def test_llm_requires_demo(tmp_path):
    with pytest.raises(ValueError):
        build_service(llm_condition=True, db_path=str(tmp_path / "a.db"))
