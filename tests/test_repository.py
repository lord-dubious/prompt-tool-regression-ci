from pathlib import Path

from prompt_tool_regression_ci.repository import RegressionRepository


def test_seed_is_idempotent(tmp_path: Path) -> None:
    repo = RegressionRepository(tmp_path / "demo.sqlite3")
    repo.ensure_seeded()
    repo.ensure_seeded()
    assert repo.summary().suite_count == 2
    assert repo.summary().run_count == 3


def test_run_detail_hydrates_tool_calls(tmp_path: Path) -> None:
    repo = RegressionRepository(tmp_path / "demo.sqlite3")
    repo.reset_demo_data()
    detail = repo.run_detail("run_tools_candidate")
    assert detail is not None
    failed = [result for result in detail.results if result.status == "failed"]
    assert failed
    assert failed[0].tool_calls[0].error_message == "stale policy fixture"


def test_execute_suite_persists_results_and_tool_calls(tmp_path: Path) -> None:
    from prompt_tool_regression_ci.models import RegressionRunRequest

    repo = RegressionRepository(tmp_path / "demo.sqlite3")
    repo.reset_demo_data()
    detail = repo.execute_suite(
        RegressionRunRequest(suite_id="suite_tools", id="run_local_tools", label="local tools")
    )
    assert detail is not None
    assert detail.run.status == "failed"
    assert detail.run.failed == 1
    assert any(result.tool_calls for result in detail.results)
    assert repo.run_detail("run_local_tools") == detail


def test_execute_suite_replaces_same_run_id(tmp_path: Path) -> None:
    from prompt_tool_regression_ci.models import RegressionRunRequest

    repo = RegressionRepository(tmp_path / "demo.sqlite3")
    repo.reset_demo_data()
    repo.execute_suite(
        RegressionRunRequest(suite_id="suite_support", id="run_replace", label="one")
    )
    detail = repo.execute_suite(
        RegressionRunRequest(suite_id="suite_support", id="run_replace", label="two")
    )
    assert detail is not None
    assert detail.run.label == "two"
    assert len(detail.results) == 4
    assert repo.summary().run_count == 4
