# OpenAI Agents App

> Agentic AI portfolio project — independent open-source implementation.
> This is an original, from-scratch build. It is not affiliated with, and does not
> contain any code, prompts, data, or business logic from, any employer or client.

![status](https://img.shields.io/badge/status-in%20development-yellow)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

## 1. Problem

Multi-agent orchestration (specialized agents that hand off to each other,
call tools, and stay within guardrails) is easy to get wrong: a single
monolithic prompt, no visibility into which agent handled a step, no bound on
tool calls or turns. This project is a small, generic demo of the OpenAI
Agents SDK's core primitives — agents, handoffs, tool calls, and guardrails —
built around a generic triage-and-specialist scenario (not any real product
or client workflow) so the orchestration pattern is easy to read and reuse.

## 2. Architecture

```text
User request -> Triage agent (classifies intent)
    -> handoff -> Specialist agent (tool calls as needed)
    -> Guardrail checks (input/output) -> Final response
    -> Run trace (per-agent, per-tool-call log)
```

An `agents_core` layer owns the swappable LLM backend and run-trace logging;
the triage/specialist agents and their tools are built on top of it.

## 3. Technology Stack

- Python, OpenAI Agents SDK
- LLM backend behind a swappable interface (see `multi-llm-router` in this
  portfolio for the general provider-swap pattern) — a fake/local backend by
  default so the project runs and is testable with no API key
- Pytest for tests

## 4. Feature List

- A triage agent that classifies an incoming request and hands off to one of
  2+ specialist agents
- At least one specialist agent that calls a real (but generic, non-secret)
  tool — e.g. a calculator or a public-data lookup function
- Input/output guardrails (e.g. reject an out-of-scope request before it
  reaches a specialist agent)
- A run trace showing which agent handled each step and which tools were
  called, for debugging/demo purposes
- A bounded run loop (max turns/tool calls) so a misbehaving agent can't loop
  forever

## 5. Implementation Plan

1. Phase 1: `agents_core` — swappable LLM backend interface with a fake
   backend, run-trace logging, project skeleton
2. Phase 2: Triage agent + at least 2 specialist agents wired via the Agents
   SDK's handoff mechanism
3. Phase 3: Tool calling for at least one specialist agent (a generic,
   non-secret tool) with a bounded run loop (stateful-run-lifecycle KB
   pattern for deliberate termination)
4. Phase 4: Input/output guardrails and tests covering both a normal run and
   a guardrail-triggering run
5. Phase 5: Docker, CI, docs, example transcripts

## Task Tracking

Work will be broken into phase-tagged user stories tracked as GitHub Issues,
not in this file. Implement Phase 1 issues first (later phases depend on it).
When you start one, add label `status:in-progress`. When you finish, close it
referencing the commit (e.g. `git commit -m "... Closes #4"`) and push.

## 6. Repository Structure

```text
OpenAI-Agents-App/
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── .env.example
├── docker/
├── docs/
│   ├── architecture.md
│   └── evaluation.md
├── src/
├── tests/
├── configs/
├── scripts/
├── notebooks/
├── examples/
├── assets/
└── .github/
    └── workflows/
```

## 7. Setup

```bash
git clone <this-repo-url>
cd OpenAI-Agents-App
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt   # or: pip install -e .
cp .env.example .env              # fill in API keys / config
```

## 8. Dataset

No dataset — this is an agent-orchestration demo, not a trained model. Any
example data used by the demo tool(s) is synthetic/public.

## 9. Training / Execution

```bash
# Once Phase 2 lands:
python -m agents_core.run --prompt "example request"
```

## 10. Evaluation

Document evaluation metrics and how to reproduce them here (see
`docs/evaluation.md`): correct-handoff rate on a small labeled prompt set,
and guardrail trigger accuracy.

## 11. Results

_To be filled in as the implementation progresses — example run traces go
here._

## 12. API

_This project is a CLI/library demo, not a served API. If that changes,
document endpoints here._

## 13. Docker

```bash
docker build -t openai-agents-app .
docker run openai-agents-app
```

## 14. Tests

```bash
pytest tests/
```

## 15. Limitations

- This is a from-scratch, independent recreation built for portfolio
  purposes — a demo of the orchestration pattern, not a production agent
  product.
- Scaffold stage: no code has been implemented yet — see §5 Implementation
  Plan.

## 16. Future Work

- Add a third specialist agent to demonstrate a deeper handoff chain.
- Add a real (rate-limited, public) API-backed tool alongside the offline
  demo tool.
- Track open items as GitHub Issues.

## 17. Disclosure

This repository is an **independent open-source recreation inspired by the
kind of production systems I have worked on professionally**. It contains no
employer or client source code, prompts, datasets, credentials, architecture
diagrams, or business logic. All code, data, and documentation here are
original or built on publicly available datasets and open-source tools.

---
_Last updated: 2026-09-12_
