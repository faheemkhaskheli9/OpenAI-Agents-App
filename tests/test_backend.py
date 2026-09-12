"""Tests for issue #1: swappable LLM backend interface with a fake default.

No network access and no API key are used anywhere in this file — the
`openai` backend is exercised only up to construction/selection, never a
real `complete()` call.
"""
from __future__ import annotations

import pytest

from agents_core.backend import FakeBackend, OpenAIBackend, get_backend
from agents_core.schema import Message


def test_fake_backend_is_deterministic():
    backend = FakeBackend()
    messages = [Message(role="user", content="hello there")]
    first = backend.complete(messages)
    second = backend.complete(messages)
    assert first.text == second.text
    assert first.backend == "fake"


def test_fake_backend_differs_for_different_input():
    backend = FakeBackend()
    a = backend.complete([Message(role="user", content="alpha")])
    b = backend.complete([Message(role="user", content="beta")])
    assert a.text != b.text


def test_fake_backend_requires_at_least_one_message():
    backend = FakeBackend()
    with pytest.raises(ValueError):
        backend.complete([])


def test_fake_backend_uses_last_user_message_not_trailing_system_message():
    backend = FakeBackend()
    messages = [
        Message(role="user", content="what is the weather"),
        Message(role="system", content="internal note, ignore"),
    ]
    response = backend.complete(messages)
    assert "what is the weather" in response.text


def test_get_backend_defaults_to_fake(monkeypatch):
    monkeypatch.delenv("AGENT_BACKEND", raising=False)
    backend = get_backend()
    assert isinstance(backend, FakeBackend)


def test_get_backend_respects_env_var(monkeypatch):
    monkeypatch.setenv("AGENT_BACKEND", "FAKE")  # case-insensitive
    backend = get_backend()
    assert isinstance(backend, FakeBackend)


def test_get_backend_explicit_name_overrides_env_var(monkeypatch):
    monkeypatch.setenv("AGENT_BACKEND", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    backend = get_backend("fake")
    assert isinstance(backend, FakeBackend)


def test_get_backend_unknown_name_raises():
    with pytest.raises(ValueError):
        get_backend("not-a-real-backend")


def test_openai_backend_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        OpenAIBackend(api_key=None)


def test_swap_to_openai_backend_is_config_only(monkeypatch):
    # Swapping backends is purely an AGENT_BACKEND / OPENAI_API_KEY change,
    # never a code change in a caller — this proves the factory selects the
    # right class from config alone, with no network call made.
    monkeypatch.setenv("AGENT_BACKEND", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    backend = get_backend()
    assert isinstance(backend, OpenAIBackend)
