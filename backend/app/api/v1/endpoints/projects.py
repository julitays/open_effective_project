from collections.abc import Callable
from typing import Annotated, TypeVar

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.cjm_read import CJMReadRepository
from app.schemas.cjm import (
    CJMBarrier,
    CJMCommunicationPoint,
    CJMExpectation,
    CJMGoal,
    CJMKPI,
    CJMLPR,
    CJMProjectRead,
)
from app.schemas.project import CJMProjectPassport
from app.services.cjm_read import CJMReadService

router = APIRouter(prefix="/projects", tags=["projects"])

T = TypeVar("T")


def get_cjm_read_service(db: Annotated[Session, Depends(get_db)]) -> CJMReadService:
    return CJMReadService(CJMReadRepository(db))


def _project_or_404(project_code: str, loader: Callable[[str], T | None]) -> T:
    result = loader(project_code)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CJM project '{project_code}' was not found.",
        )
    return result


@router.get("", response_model=list[CJMProjectPassport])
def list_projects(
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> list[CJMProjectPassport]:
    return service.list_projects()


@router.get("/{project_code}", response_model=CJMProjectPassport)
def get_project(
    project_code: str,
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> CJMProjectPassport:
    return _project_or_404(project_code, service.get_project)


@router.get("/{project_code}/cjm", response_model=CJMProjectRead)
def get_project_cjm(
    project_code: str,
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> CJMProjectRead:
    return _project_or_404(project_code, service.get_project_cjm)


@router.get("/{project_code}/lprs", response_model=list[CJMLPR])
def get_project_lprs(
    project_code: str,
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> list[CJMLPR]:
    return _project_or_404(project_code, service.get_project_lprs)


@router.get("/{project_code}/barriers", response_model=list[CJMBarrier])
def get_project_barriers(
    project_code: str,
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> list[CJMBarrier]:
    return _project_or_404(project_code, service.get_project_barriers)


@router.get("/{project_code}/expectations", response_model=list[CJMExpectation])
def get_project_expectations(
    project_code: str,
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> list[CJMExpectation]:
    return _project_or_404(project_code, service.get_project_expectations)


@router.get("/{project_code}/kpis", response_model=list[CJMKPI])
def get_project_kpis(
    project_code: str,
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> list[CJMKPI]:
    return _project_or_404(project_code, service.get_project_kpis)


@router.get("/{project_code}/communications", response_model=list[CJMCommunicationPoint])
def get_project_communications(
    project_code: str,
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> list[CJMCommunicationPoint]:
    return _project_or_404(project_code, service.get_project_communications)


@router.get("/{project_code}/goals", response_model=list[CJMGoal])
def get_project_goals(
    project_code: str,
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> list[CJMGoal]:
    return _project_or_404(project_code, service.get_project_goals)
