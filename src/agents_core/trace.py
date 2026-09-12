"""Per-run trace: which agent handled each step and which tools were
called, so a run's behavior is inspectable after the fact instead of only
visible in its final output.

Shaped to also carry the Phase 3 bounded run loop's tool-call pause/resume
cycle (Knowledge-base pattern: agentic-loops/stateful-run-lifecycle.md --
a run is a sequence of handoffs interleaved with tool-call
request/result pairs) without needing a schema change once that loop
lands -- `record_tool_call` already takes the call's arguments and result
together as one event, not two events a caller must correlate itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class UnknownRun(KeyError):
    """Raised by `TraceStore.get` for a run_id no run was ever started
    under -- never returns `None` for a typo'd/expired run_id, since a
    caller inspecting a trace needs to know "this run never happened" is
    different from "this run produced an empty trace"."""

    def __init__(self, run_id: str):
        super().__init__(f"No trace recorded for run_id {run_id!r}")


@dataclass(frozen=True)
class HandoffEvent:
    """One agent taking over the run, in order."""

    sequence: int
    to_agent: str
    reason: str | None = None


@dataclass(frozen=True)
class ToolCallEvent:
    """One tool call and its result, attributed to the agent that made it."""

    sequence: int
    agent: str
    tool_name: str
    args: dict[str, Any]
    result: Any


@dataclass
class RunTrace:
    """The ordered trace for a single run. Not thread-safe -- one run is
    handled by one loop iteration at a time, per the bounded-run-loop
    design this feeds into."""

    run_id: str
    _events: list[HandoffEvent | ToolCallEvent] = field(default_factory=list)

    def record_handoff(self, to_agent: str, *, reason: str | None = None) -> HandoffEvent:
        event = HandoffEvent(sequence=len(self._events), to_agent=to_agent, reason=reason)
        self._events.append(event)
        return event

    def record_tool_call(
        self, agent: str, tool_name: str, args: dict[str, Any], result: Any
    ) -> ToolCallEvent:
        event = ToolCallEvent(
            sequence=len(self._events), agent=agent, tool_name=tool_name, args=args, result=result
        )
        self._events.append(event)
        return event

    @property
    def events(self) -> tuple[HandoffEvent | ToolCallEvent, ...]:
        return tuple(self._events)

    @property
    def handoffs(self) -> tuple[HandoffEvent, ...]:
        return tuple(e for e in self._events if isinstance(e, HandoffEvent))

    @property
    def tool_calls(self) -> tuple[ToolCallEvent, ...]:
        return tuple(e for e in self._events if isinstance(e, ToolCallEvent))


class TraceStore:
    """Holds one `RunTrace` per run_id so a caller can retrieve it after
    the run completes -- e.g. a CLI printing `--trace`, or a test asserting
    on the handoff/tool-call sequence. A fresh `TraceStore` is meant to be
    constructed per process/test (robustness rule 11: no hidden module-level
    mutable state a caller's result could silently depend on)."""

    def __init__(self) -> None:
        self._runs: dict[str, RunTrace] = {}

    def start_run(self, run_id: str) -> RunTrace:
        if run_id in self._runs:
            raise ValueError(f"run_id {run_id!r} already started")
        trace = RunTrace(run_id=run_id)
        self._runs[run_id] = trace
        return trace

    def get(self, run_id: str) -> RunTrace:
        try:
            return self._runs[run_id]
        except KeyError:
            raise UnknownRun(run_id) from None
