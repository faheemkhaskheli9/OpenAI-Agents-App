# Evaluation Notes: OpenAI Agents App

## Metrics

- **Correct-handoff rate** — for a small labeled set of (request, expected
  specialist agent) pairs, the fraction where triage handed off to the
  expected agent.
- **Guardrail trigger accuracy** — for a set of in-scope and out-of-scope
  requests, the fraction correctly allowed through / rejected.
- **Run boundedness** — every test run completes within the configured max
  turns/tool calls (no run should ever hit the loop's hard failure path).

## Result Log

_Fill in as phases land — one row per evaluation run._

| Date | Phase | Metric | Value | Notes |
|------|-------|--------|-------|-------|
| _TBD_ | | | | |
