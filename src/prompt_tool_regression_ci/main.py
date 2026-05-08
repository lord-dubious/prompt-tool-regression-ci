from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from prompt_tool_regression_ci.api import router as api_router
from prompt_tool_regression_ci.config import Settings
from prompt_tool_regression_ci.repository import RegressionRepository
from prompt_tool_regression_ci.web import router as web_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings.from_env()
    repository = RegressionRepository(resolved.database_path)
    repository.ensure_seeded()
    app = FastAPI(
        title="Prompt/Tool Regression CI",
        summary="Local-first prompt and tool-call regression harness",
        version="0.1.0",
    )
    app.state.repository = repository
    app.mount("/static", StaticFiles(directory=Path(__file__).parent / "web_assets"), name="static")
    app.include_router(web_router)
    app.include_router(api_router)
    return app


app = create_app()


def run() -> None:
    uvicorn.run("prompt_tool_regression_ci.main:app", host="127.0.0.1", port=8030, reload=False)
