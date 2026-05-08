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
