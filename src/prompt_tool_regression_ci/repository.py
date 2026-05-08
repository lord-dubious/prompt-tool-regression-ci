from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from prompt_tool_regression_ci import demo_data
from prompt_tool_regression_ci.models import (
    DashboardSummary,
    RegressionRun,
    RunDetail,
    RunResult,
    SuiteDetail,
    TestCase,
    TestSuite,
    ToolCallRecord,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


class RegressionRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS suites (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, suite_id TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, suite_id TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS results (id TEXT PRIMARY KEY, run_id TEXT NOT NULL, case_id TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS tool_calls (id TEXT PRIMARY KEY, result_id TEXT NOT NULL, payload TEXT NOT NULL);
                """
            )

    def reset_demo_data(self) -> None:
        self.initialize()
        with self._connect() as connection:
            for table in ["tool_calls", "results", "runs", "cases", "suites"]:
                connection.execute(f"DELETE FROM {table}")
            for suite in demo_data.demo_suites():
                self._insert(connection, "suites", suite.id, suite)
            for case in demo_data.demo_cases():
                self._insert(connection, "cases", case.id, case, suite_id=case.suite_id)
            for run in demo_data.demo_runs():
                self._insert(connection, "runs", run.id, run, suite_id=run.suite_id)
            for result in demo_data.demo_results():
                self._insert(
                    connection,
                    "results",
                    result.id,
                    result,
                    run_id=result.run_id,
                    case_id=result.case_id,
                )
            for tool_call in demo_data.demo_tool_calls():
                self._insert(
                    connection, "tool_calls", tool_call.id, tool_call, result_id=tool_call.result_id
                )

    def ensure_seeded(self) -> None:
        self.initialize()
        with self._connect() as connection:
            count = connection.execute("SELECT COUNT(*) FROM suites").fetchone()[0]
        if count == 0:
            self.reset_demo_data()

    def list_suites(self) -> list[TestSuite]:
        return self._fetch_many("SELECT payload FROM suites ORDER BY id", TestSuite)

    def suite_detail(self, suite_id: str) -> SuiteDetail | None:
        suite = self._fetch_one("SELECT payload FROM suites WHERE id = ?", TestSuite, (suite_id,))
        if suite is None:
            return None
        cases = self._fetch_many(
            "SELECT payload FROM cases WHERE suite_id = ? ORDER BY id", TestCase, (suite_id,)
        )
        runs = self._fetch_many(
            "SELECT payload FROM runs WHERE suite_id = ? ORDER BY id", RegressionRun, (suite_id,)
        )
        return SuiteDetail(suite=suite, cases=cases, runs=runs)

    def list_runs(self) -> list[RegressionRun]:
        return self._fetch_many("SELECT payload FROM runs ORDER BY id", RegressionRun)

    def run_detail(self, run_id: str) -> RunDetail | None:
        run = self._fetch_one("SELECT payload FROM runs WHERE id = ?", RegressionRun, (run_id,))
        if run is None:
            return None
        results = self._fetch_many(
            "SELECT payload FROM results WHERE run_id = ? ORDER BY id", RunResult, (run_id,)
        )
        calls_by_result = {result.id: [] for result in results}
        calls = self._fetch_many("SELECT payload FROM tool_calls ORDER BY id", ToolCallRecord)
        for call in calls:
            if call.result_id in calls_by_result:
                calls_by_result[call.result_id].append(call)
        hydrated = [
            result.model_copy(update={"tool_calls": calls_by_result[result.id]})
            for result in results
        ]
        return RunDetail(run=run, results=hydrated)

    def summary(self) -> DashboardSummary:
        runs = self.list_runs()
        results = self._fetch_many("SELECT payload FROM results", RunResult)
        return DashboardSummary(
            suite_count=len(self.list_suites()),
            case_count=len(self._fetch_many("SELECT payload FROM cases", TestCase)),
            run_count=len(runs),
            passing_runs=sum(1 for run in runs if run.status == "passed"),
            failing_runs=sum(1 for run in runs if run.status == "failed"),
            changed_results=sum(1 for result in results if result.status == "changed"),
            latest_run_id=runs[0].id if runs else None,
        )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _insert(
        self,
        connection: sqlite3.Connection,
        table: str,
        identifier: str,
        model: BaseModel,
        **columns: str,
    ) -> None:
        payload = model.model_dump_json()
        if table == "suites":
            connection.execute(
                "INSERT INTO suites (id, payload) VALUES (?, ?)", (identifier, payload)
            )
        elif table == "cases":
            connection.execute(
                "INSERT INTO cases (id, suite_id, payload) VALUES (?, ?, ?)",
                (identifier, columns["suite_id"], payload),
            )
        elif table == "runs":
            connection.execute(
                "INSERT INTO runs (id, suite_id, payload) VALUES (?, ?, ?)",
                (identifier, columns["suite_id"], payload),
            )
        elif table == "results":
            connection.execute(
                "INSERT INTO results (id, run_id, case_id, payload) VALUES (?, ?, ?, ?)",
                (identifier, columns["run_id"], columns["case_id"], payload),
            )
        else:
            connection.execute(
                "INSERT INTO tool_calls (id, result_id, payload) VALUES (?, ?, ?)",
                (identifier, columns["result_id"], payload),
            )

    def _fetch_one(
        self, query: str, model: type[ModelT], params: tuple[str, ...] = ()
    ) -> ModelT | None:
        with self._connect() as connection:
            row = connection.execute(query, params).fetchone()
        if row is None:
            return None
        return model.model_validate(json.loads(row[0]))

    def _fetch_many(
        self, query: str, model: type[ModelT], params: tuple[str, ...] = ()
    ) -> list[ModelT]:
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [model.model_validate(json.loads(row[0])) for row in rows]
