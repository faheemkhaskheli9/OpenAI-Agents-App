"""Tests for issue #3: CLI entry point that runs one request end to end.

No network access or API key is used -- the CLI runs against the fake
backend by default, and the failure-path test triggers get_backend's
"unknown backend" ValueError rather than a real transport error.
"""
from __future__ import annotations

from agents_core.run import DEFAULT_AGENT, main, run_once


def test_run_once_returns_the_fake_backends_response():
    text, trace = run_once("hello there")
    assert "hello there" in text
    assert trace.handoffs[0].to_agent == DEFAULT_AGENT


def test_cli_prints_the_final_response(capsys):
    rc = main(["--prompt", "example request"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "example request" in out


def test_cli_defaults_to_the_fake_backend(capsys, monkeypatch):
    monkeypatch.delenv("AGENT_BACKEND", raising=False)
    rc = main(["--prompt", "hi"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "[fake-backend:" in out


def test_cli_exits_non_zero_on_unhandled_run_failure(capsys):
    rc = main(["--prompt", "hi", "--backend", "not-a-real-backend"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "error:" in captured.err


def test_cli_trace_flag_prints_the_handoff_to_stderr(capsys):
    rc = main(["--prompt", "hi", "--trace"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "trace:" in captured.err
    assert DEFAULT_AGENT in captured.err
