"""Swappable LLM backend interface.

`BaseBackend` is the one call signature every agent in this project uses to
talk to an LLM. `FakeBackend` is the default so the whole project runs and
is testable with no API key. Swapping to a real provider is a matter of
setting `AGENT_BACKEND=openai` (and `OPENAI_API_KEY`) in `.env` — callers
never change, they just go through `get_backend()`.
"""
from __future__ import annotations

import hashlib
import os
from abc import ABC, abstractmethod

from .schema import BackendResponse, Message


class BaseBackend(ABC):
    """Common interface every LLM backend must implement."""

    #: Short, stable key this backend is registered under (e.g. "fake").
    name: str

    @abstractmethod
    def complete(self, messages: list[Message]) -> BackendResponse:
        """Send `messages` to the backend and return a `BackendResponse`.

        Implementations must raise on transport/SDK errors rather than
        returning a malformed response — callers (bounded run loop, Phase 3)
        rely on exceptions to detect a failed attempt.
        """
        raise NotImplementedError


class FakeBackend(BaseBackend):
    """Deterministic, offline backend — the default.

    The response is derived from a hash of the last user message, so the
    same input always produces the same output (useful for reproducible
    tests and demos) while different inputs produce visibly different
    output. No network access, no API key.
    """

    name = "fake"

    def complete(self, messages: list[Message]) -> BackendResponse:
        if not messages:
            raise ValueError("complete() requires at least one message")
        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user"),
            messages[-1].content,
        )
        digest = hashlib.sha256(last_user.encode("utf-8")).hexdigest()[:8]
        text = f"[fake-backend:{digest}] ack: {last_user[:200]}"
        return BackendResponse(
            text=text,
            backend=self.name,
            raw={"messages": [vars(m) for m in messages]},
        )


class OpenAIBackend(BaseBackend):
    """Real OpenAI-backed implementation.

    The `openai` package is imported lazily inside `complete()` so it is
    only a hard dependency when this backend is actually used — the fake
    backend (and the whole default test run) never needs it installed or an
    API key set.
    """

    name = "openai"

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAIBackend requires OPENAI_API_KEY (env var or api_key=...)"
            )
        self._api_key = api_key
        self._model = model

    def complete(self, messages: list[Message]) -> BackendResponse:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - only hit when selected
            raise ImportError(
                "OpenAIBackend requires the 'openai' package: pip install openai"
            ) from exc

        client = OpenAI(api_key=self._api_key)
        response = client.chat.completions.create(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        text = response.choices[0].message.content or ""
        return BackendResponse(text=text, backend=self.name, raw=response.model_dump())


#: Registry of backend name -> implementation class. Extend by adding an
#: entry here (this stays a mapping, not one field per known backend)
#: rather than branching in `get_backend`.
_REGISTRY: dict[str, type[BaseBackend]] = {
    FakeBackend.name: FakeBackend,
    OpenAIBackend.name: OpenAIBackend,
}


def get_backend(name: str | None = None) -> BaseBackend:
    """Return the configured backend instance.

    `name` overrides the `AGENT_BACKEND` env var (default: "fake"). This is
    the single place backend selection happens — swapping backends is
    config only (`AGENT_BACKEND`, `OPENAI_API_KEY`), never a code change in
    any caller.
    """
    key = (name or os.environ.get("AGENT_BACKEND") or "fake").strip().lower()
    try:
        backend_cls = _REGISTRY[key]
    except KeyError as exc:
        known = ", ".join(sorted(_REGISTRY))
        raise ValueError(f"Unknown AGENT_BACKEND '{key}' (known: {known})") from exc
    return backend_cls()
