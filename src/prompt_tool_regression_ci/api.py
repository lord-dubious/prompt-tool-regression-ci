from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from prompt_tool_regression_ci.models import (
    DashboardSummary,
    RegressionRun,
    RunDetail,
    SuiteDetail,
    TestSuite,
)
from prompt_tool_regression_ci.repository import RegressionRepository

router = APIRouter(prefix="/api", tags=["regression"])


def get_repository(request: Request) -> RegressionRepository:
    return request.app.state.repository


RepositoryDep = Annotated[RegressionRepository, Depends(get_repository)]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/summary")
def summary(repository: RepositoryDep) -> DashboardSummary:
    return repository.summary()


@router.post("/demo/reset")
def reset_demo(repository: RepositoryDep) -> DashboardSummary:
    repository.reset_demo_data()
    return repository.summary()


@router.get("/suites")
def suites(repository: RepositoryDep) -> list[TestSuite]:
    return repository.list_suites()


@router.get("/suites/{suite_id}")
def suite_detail(suite_id: str, repository: RepositoryDep) -> SuiteDetail:
    detail = repository.suite_detail(suite_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Suite not found")
    return detail


@router.get("/runs")
def runs(repository: RepositoryDep) -> list[RegressionRun]:
    return repository.list_runs()


@router.get("/runs/{run_id}")
def run_detail(run_id: str, repository: RepositoryDep) -> RunDetail:
    detail = repository.run_detail(run_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return detail
