# Architecture Notes: OpenAI Agents App

## Pipeline

```text
User request -> Triage agent (classifies intent)
    -> handoff -> Specialist agent (tool calls as needed)
    -> Guardrail checks (input/output) -> Final response
    -> Run trace (per-agent, per-tool-call log)
```

## Components

- `agents_core.backend` — swappable LLM backend interface, fake backend
  default so the project runs offline
- `agents_core.trace` — per-agent, per-tool-call run trace for debugging
- `agents_core.agents` — triage agent + specialist agents wired via the
  Agents SDK's handoff mechanism
- `agents_core.tools` — generic, non-secret tool functions callable by a
  specialist agent
- `agents_core.guardrails` — input/output checks that can reject or flag a
  run before/after the agent responds

## Design Notes

- Apply this portfolio's `agentic-loops/stateful-run-lifecycle` knowledge-base
  pattern for the bounded run loop and deliberate termination — do not
  reimplement turn/tool-call limits from scratch.
- Keep the LLM backend swappable behind an interface (see `multi-llm-router`
  for the general provider-swap pattern); default to a fake backend so tests
  and local runs need no API key.
- Every run must be bounded (max turns / max tool calls) — an unbounded loop
  is the most common agent-orchestration bug.
- Guardrails run on both input (before triage) and output (before the final
  response is returned) — a guardrail that only checks output misses
  out-of-scope requests that shouldn't reach a specialist agent at all.

## Consolidation note

This project is standalone — it does not consolidate any other portfolio
repo. `docs/architecture.md` exists here purely to document the pipeline and
knowledge-base pattern references for whoever implements Phase 1.
