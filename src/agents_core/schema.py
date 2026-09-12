"""Common request/response shapes for LLM backends.

Every backend (fake, OpenAI, ...) speaks this shape so agents and tools
never touch a provider SDK directly — see `agents_core.backend`.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Message:
    """One turn in a conversation."""

    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass(frozen=True)
class BackendResponse:
    """The result of a single `BaseBackend.complete()` call."""

    text: str
    backend: str
    raw: dict = field(default_factory=dict)
