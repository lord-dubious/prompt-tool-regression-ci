from pathlib import Path

from fastapi.testclient import TestClient

from prompt_tool_regression_ci.config import Settings
from prompt_tool_regression_ci.main import create_app


def test_dashboard_assets(tmp_path: Path) -> None:
    api = TestClient(create_app(Settings(database_path=tmp_path / "demo.sqlite3")))
    page = api.get("/")
    assert page.status_code == 200
    assert "Prompt/Tool CI" in page.text
    assert "Execute suite" in page.text
    script = api.get("/static/app.js")
    assert script.status_code == 200
    assert "/api/summary" in script.text
    assert "/api/runs/execute" in script.text
    css = api.get("/static/styles.css")
    assert "gate-ring" in css.text
    js = api.get("/static/app.js")
    assert "/api/summary" in js.text
