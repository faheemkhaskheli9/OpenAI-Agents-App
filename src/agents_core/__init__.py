"""Core, agent-framework-agnostic building blocks for this project.

Phase 1 provides the swappable LLM backend (`agents_core.backend`) and its
shared request/response schema (`agents_core.schema`). Later phases add
tracing, agents, tools, and guardrails on top of this layer.
"""
