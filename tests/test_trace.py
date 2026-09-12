"""Tests for issue #2: per-agent, per-tool-call run trace logging."""

from __future__ import annotations

import pytest

from agents_core.trace import RunTrace, TraceStore, UnknownRun


def test_records_handoffs_in_order():
    trace = RunTrace(run_id="run-1")
    trace.record_handoff("triage")
    trace.record_handoff("billing", reason="billing keyword detected")

    assert [h.to_agent for h in trace.handoffs] == ["triage", "billing"]
    assert trace.handoffs[1].reason == "billing keyword detected"


def test_records_tool_calls_with_args_and_result():
    trace = RunTrace(run_id="run-1")
    trace.record_tool_call("billing", "lookup_invoice", {"invoice_id": "INV-1"}, {"status": "paid"})

    call = trace.tool_calls[0]
    assert call.agent == "billing"
    assert call.tool_name == "lookup_invoice"
    assert call.args == {"invoice_id": "INV-1"}
    assert call.result == {"status": "paid"}


def test_events_preserve_overall_chronological_order():
    trace = RunTrace(run_id="run-1")
    trace.record_handoff("triage")
    trace.record_tool_call("triage", "classify", {"text": "hi"}, "billing")
    trace.record_handoff("billing")

    kinds = [type(e).__name__ for e in trace.events]
    assert kinds == ["HandoffEvent", "ToolCallEvent", "HandoffEvent"]
    assert [e.sequence for e in trace.events] == [0, 1, 2]


def test_trace_store_retrieves_a_run_by_id_after_it_completes():
    store = TraceStore()
    trace = store.start_run("run-42")
    trace.record_handoff("triage")

    retrieved = store.get("run-42")

    assert retrieved is trace
    assert [h.to_agent for h in retrieved.handoffs] == ["triage"]


def test_trace_store_unknown_run_id_raises_clear_error_not_none():
    store = TraceStore()
    with pytest.raises(UnknownRun):
        store.get("never-started")


def test_trace_store_rejects_starting_the_same_run_id_twice():
    store = TraceStore()
    store.start_run("run-1")
    with pytest.raises(ValueError):
        store.start_run("run-1")


def test_two_trace_store_instances_are_independent():
    # Guards against a hidden module-level registry a caller's result
    # could silently depend on (robustness rule 11).
    a, b = TraceStore(), TraceStore()
    a.start_run("run-1")
    assert "run-1" not in b._runs
