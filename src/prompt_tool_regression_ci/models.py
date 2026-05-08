from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


class RunStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    CHANGED = "changed"


class ResultStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    CHANGED = "changed"


class ToolStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestSuite(BaseModel):
    id: str
    name: str
    description: str
    owner: str
    created_at: datetime


class ToolExpectation(BaseModel):
    tool_name: str
    input_contains: str
    output_contains: str
    required: bool = True


class TestCase(BaseModel):
    id: str
    suite_id: str
    name: str
    prompt: str
    expected_response: str
    safety_policy: str
    expectations: list[ToolExpectation] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class RegressionRun(BaseModel):
    id: str
    suite_id: str
    label: str
    status: RunStatus
    started_at: datetime
    completed_at: datetime
    passed: int
    failed: int
    changed: int
    latency_ms: int


class RegressionRunRequest(BaseModel):
    suite_id: str
    id: str | None = None
    label: str = "local regression execution"
    prompt_version: str = "local-review"


class ToolCallRecord(BaseModel):
    id: str
    result_id: str
    tool_name: str
    input_summary: str
    output_summary: str
    status: ToolStatus
    latency_ms: int
    error_message: str | None = None


class RegressionDiff(BaseModel):
    expected: str
    actual: str
    reason: str


class RunResult(BaseModel):
    id: str
    run_id: str
    case_id: str
    status: ResultStatus
    actual_response: str
    diff: RegressionDiff | None = None
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SuiteDetail(BaseModel):
    suite: TestSuite
    cases: list[TestCase]
    runs: list[RegressionRun]


class RunDetail(BaseModel):
    run: RegressionRun
    results: list[RunResult]


class DashboardSummary(BaseModel):
    suite_count: int
    case_count: int
    run_count: int
    passing_runs: int
    failing_runs: int
    changed_results: int
    latest_run_id: str | None
