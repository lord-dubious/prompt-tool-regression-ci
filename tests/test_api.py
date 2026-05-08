from pathlib import Path

from fastapi.testclient import TestClient

from prompt_tool_regression_ci.config import Settings
from prompt_tool_regression_ci.main import create_app


def client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(Settings(database_path=tmp_path / "demo.sqlite3")))


def test_health_and_summary(tmp_path: Path) -> None:
    response = client(tmp_path).get("/api/health")
    assert response.json() == {"status": "ok"}
    summary = client(tmp_path).get("/api/summary").json()
    assert summary["suite_count"] == 2
    assert summary["case_count"] == 6
    assert summary["run_count"] == 3
    assert summary["changed_results"] == 1


def test_suite_detail_and_runs(tmp_path: Path) -> None:
    api = client(tmp_path)
    suites = api.get("/api/suites").json()
    assert suites[0]["id"] == "suite_support"
    detail = api.get("/api/suites/suite_support").json()
    assert len(detail["cases"]) == 4
    assert {run["label"] for run in detail["runs"]} == {
        "baseline prompts",
        "candidate prompt rewrite",
    }
    run = api.get("/api/runs/run_support_candidate").json()
    assert len(run["results"]) == 4
    assert any(result["status"] == "changed" for result in run["results"])


def test_reset_and_404s(tmp_path: Path) -> None:
    api = client(tmp_path)
    assert api.post("/api/demo/reset").json()["run_count"] == 3
    assert api.get("/api/suites/missing").status_code == 404
    assert api.get("/api/runs/missing").status_code == 404


def test_execute_suite_creates_reviewable_run(tmp_path: Path) -> None:
    api = client(tmp_path)
    response = api.post(
        "/api/runs/execute",
        json={
            "suite_id": "suite_support",
            "id": "run_local_support",
            "label": "local support execution",
            "prompt_version": "review-branch",
        },
    )
    assert response.status_code == 200
    detail = response.json()
    assert detail["run"]["id"] == "run_local_support"
    assert detail["run"]["changed"] == 1
    assert len(detail["results"]) == 4
    assert api.get("/api/summary").json()["run_count"] == 4


def test_execute_suite_replaces_existing_run(tmp_path: Path) -> None:
    api = client(tmp_path)
    payload = {"suite_id": "suite_tools", "id": "run_replace", "label": "first"}
    assert api.post("/api/runs/execute", json=payload).status_code == 200
    payload["label"] = "second"
    second = api.post("/api/runs/execute", json=payload).json()
    assert second["run"]["label"] == "second"
    assert second["run"]["failed"] == 1
    assert api.get("/api/summary").json()["run_count"] == 4


def test_execute_suite_rejects_missing_suite(tmp_path: Path) -> None:
    api = client(tmp_path)
    assert api.post("/api/runs/execute", json={"suite_id": "missing"}).status_code == 404
