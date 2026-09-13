"""CLI entry point: run one request through the agent system end to end.

Phase 1 has no triage/specialist agents yet (Phase 2) and no tool calls
(Phase 3), so a run here is the smallest version of the Knowledge-base
agentic-loops/stateful-run-lifecycle shape: one handoff (to a placeholder
"default" agent) recorded in the trace, one backend call, deliberate
termination. The bounded multi-turn loop itself lands in Phase 3 once
there's something to iterate over (a tool-call pause/resume cycle) --
this phase's "run" is already the loop's smallest possible instance
(one iteration, one terminal status) rather than a different shape that
would need reworking later.

    python -m agents_core.run --prompt "example request"
    python -m agents_core.run --prompt "example request" --trace
"""
from __future__ import annotations

import argparse
import sys
import uuid

from .backend import get_backend
from .schema import Message
from .trace import RunTrace, TraceStore

#: Phase 1 has no triage yet -- every run hands off to this one placeholder
#: agent. Phase 2 replaces this constant with real triage/specialist names.
DEFAULT_AGENT = "default"


def run_once(
    prompt: str,
    *,
    backend_name: str | None = None,
    trace_store: TraceStore | None = None,
) -> tuple[str, RunTrace]:
    """Run one request through the (currently single-agent) system.

    Returns the backend's response text and the run's trace. Raises on any
    backend failure (unknown backend name, transport/SDK error, ...) --
    callers (the CLI) turn that into a clean error and a non-zero exit
    rather than a traceback.
    """
    store = trace_store if trace_store is not None else TraceStore()
    run_id = str(uuid.uuid4())
    trace = store.start_run(run_id)
    trace.record_handoff(DEFAULT_AGENT, reason="phase 1: single default agent, no triage yet")

    backend = get_backend(backend_name)
    response = backend.complete([Message(role="user", content=prompt)])
    return response.text, trace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agents_core.run",
        description="Run one request through the agent system and print the final response.",
    )
    parser.add_argument("--prompt", required=True, help="The request to run.")
    parser.add_argument(
        "--backend",
        default=None,
        help="Override AGENT_BACKEND for this run (default: the fake backend).",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Also print the run's handoff/tool-call trace to stderr.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text, trace = run_once(args.prompt, backend_name=args.backend)
    except Exception as exc:  # CLI boundary: report cleanly, exit non-zero
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(text)
    if args.trace:
        for event in trace.events:
            print(f"trace: {event}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
