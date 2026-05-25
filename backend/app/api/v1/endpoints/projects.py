from collections.abc import Callable
from typing import Annotated, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.demo_auth import get_session_username
from app.repositories.cjm_read import CJMReadRepository
from app.repositories.cjm_update import CJMUpdateRepository
from app.schemas.cjm import (
    ArchiveRequest,
    CJMBarrier,
    CJMBarrierCreate,
    CJMBarrierPatch,
    CJMCommunicationPoint,
    CJMCommunicationPointCreate,
    CJMCommunicationPointPatch,
    CJMExpectation,
    CJMExpectationCreate,
    CJMExpectationPatch,
    CJMGoal,
    CJMGoalCreate,
    CJMGoalPatch,
    CJMKPI,
    CJMKPICreate,
    CJMKPIPatch,
    CJMLPR,
    CJMLPRCreate,
    CJMLPRPatch,
    CJMProjectRead,
    ProjectContextBlockCreate,
    ProjectContextBlockRead,
    ProjectEffectivenessRead,
)
from app.schemas.project import CJMProjectCreate, CJMProjectPassport, CJMProjectPatch
from app.services.cjm_read import CJMReadService
from app.services.cjm_update import CJMPatchValueError, CJMUpdateService

router = APIRouter(prefix="/projects", tags=["projects"])

T = TypeVar("T")


def get_cjm_read_service(db: Annotated[Session, Depends(get_db)]) -> CJMReadService:
    return CJMReadService(CJMReadRepository(db))


def get_cjm_update_service(db: Annotated[Session, Depends(get_db)]) -> CJMUpdateService:
    read_repository = CJMReadRepository(db)
    return CJMUpdateService(
        CJMUpdateRepository(db),
        CJMReadService(read_repository),
    )


def _project_or_404(project_code: str, loader: Callable[[str], T | None]) -> T:
    result = loader(project_code)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CJM project '{project_code}' was not found.",
        )
    return result


def _entity_or_404(result: T | None, entity_name: str, entity_code: str) -> T:
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} '{entity_code}' was not found.",
        )
    return result


def _patch_value_error(error: CJMPatchValueError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))


def _updated_by(request: Request) -> str:
    return get_session_username(request) or "local_dev"


@router.get("", response_model=list[CJMProjectPassport])
def list_projects(
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> list[CJMProjectPassport]:
    return service.list_projects()


@router.post("", response_model=CJMProjectPassport, status_code=status.HTTP_201_CREATED)
def create_project(
    request: Request,
    payload: CJMProjectCreate,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMProjectPassport:
    try:
        return service.create_project(payload, _updated_by(request))
    except CJMPatchValueError as error:
        raise _patch_value_error(error) from error


@router.get("/{project_code}", response_model=CJMProjectPassport)
def get_project(
    project_code: str,
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> CJMProjectPassport:
    return _project_or_404(project_code, service.get_project)


@router.patch("/{project_code}", response_model=CJMProjectPassport)
def patch_project(
    request: Request,
    project_code: str,
    patch: CJMProjectPatch,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMProjectPassport:
    try:
        return _project_or_404(
            project_code,
            lambda code: service.update_project(code, patch, _updated_by(request)),
        )
    except CJMPatchValueError as error:
        raise _patch_value_error(error) from error


@router.post("/{project_code}/archive", response_model=CJMProjectPassport)
def archive_project(
    request: Request,
    project_code: str,
    payload: ArchiveRequest,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMProjectPassport:
    return _project_or_404(
        project_code,
        lambda code: service.archive_project(code, _updated_by(request), payload.archive_reason),
    )


@router.get("/{project_code}/cjm", response_model=CJMProjectRead)
def get_project_cjm(
    project_code: str,
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> CJMProjectRead:
    return _project_or_404(project_code, service.get_project_cjm)


@router.get("/{project_code}/effectiveness", response_model=ProjectEffectivenessRead)
def get_project_effectiveness(
    project_code: str,
    service: Annotated[CJMReadService, Depends(get_cjm_read_service)],
) -> ProjectEffectivenessRead:
    return _project_or_404(project_code, service.get_project_effectiveness)


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


@router.post("/{project_code}/goals", response_model=CJMGoal, status_code=status.HTTP_201_CREATED)
def create_project_goal(
    request: Request,
    project_code: str,
    payload: CJMGoalCreate,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMGoal:
    return _entity_or_404(
        service.create_goal(project_code, payload, _updated_by(request)),
        "Project",
        project_code,
    )


@router.post("/{project_code}/lprs", response_model=CJMLPR, status_code=status.HTTP_201_CREATED)
def create_project_lpr(
    request: Request,
    project_code: str,
    payload: CJMLPRCreate,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMLPR:
    return _entity_or_404(
        service.create_lpr(project_code, payload, _updated_by(request)),
        "Project",
        project_code,
    )


@router.post("/{project_code}/barriers", response_model=CJMBarrier, status_code=status.HTTP_201_CREATED)
def create_project_barrier(
    request: Request,
    project_code: str,
    payload: CJMBarrierCreate,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMBarrier:
    return _entity_or_404(
        service.create_barrier(project_code, payload, _updated_by(request)),
        "Project",
        project_code,
    )


@router.post(
    "/{project_code}/expectations",
    response_model=CJMExpectation,
    status_code=status.HTTP_201_CREATED,
)
def create_project_expectation(
    request: Request,
    project_code: str,
    payload: CJMExpectationCreate,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMExpectation:
    return _entity_or_404(
        service.create_expectation(project_code, payload, _updated_by(request)),
        "Project",
        project_code,
    )


@router.post("/{project_code}/kpis", response_model=CJMKPI, status_code=status.HTTP_201_CREATED)
def create_project_kpi(
    request: Request,
    project_code: str,
    payload: CJMKPICreate,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMKPI:
    return _entity_or_404(
        service.create_kpi(project_code, payload, _updated_by(request)),
        "Project",
        project_code,
    )


@router.post(
    "/{project_code}/communications",
    response_model=CJMCommunicationPoint,
    status_code=status.HTTP_201_CREATED,
)
def create_project_communication(
    request: Request,
    project_code: str,
    payload: CJMCommunicationPointCreate,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMCommunicationPoint:
    return _entity_or_404(
        service.create_communication(project_code, payload, _updated_by(request)),
        "Project",
        project_code,
    )


@router.post(
    "/{project_code}/context-blocks",
    response_model=ProjectContextBlockRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project_context_block(
    request: Request,
    project_code: str,
    payload: ProjectContextBlockCreate,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> ProjectContextBlockRead:
    return _entity_or_404(
        service.create_context_block(project_code, payload, _updated_by(request)),
        "Project",
        project_code,
    )


@router.patch("/{project_code}/goals/{goal_code}", response_model=CJMGoal)
def patch_project_goal(
    request: Request,
    project_code: str,
    goal_code: str,
    patch: CJMGoalPatch,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMGoal:
    try:
        return _entity_or_404(
            service.update_goal(project_code, goal_code, patch, _updated_by(request)),
            "Goal",
            goal_code,
        )
    except CJMPatchValueError as error:
        raise _patch_value_error(error) from error


@router.post("/{project_code}/goals/{goal_code}/archive", response_model=CJMGoal)
def archive_project_goal(
    request: Request,
    project_code: str,
    goal_code: str,
    payload: ArchiveRequest,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMGoal:
    return _entity_or_404(
        service.archive_goal(project_code, goal_code, _updated_by(request), payload.archive_reason),
        "Goal",
        goal_code,
    )


@router.patch("/{project_code}/lprs/{lpr_code}", response_model=CJMLPR)
def patch_project_lpr(
    request: Request,
    project_code: str,
    lpr_code: str,
    patch: CJMLPRPatch,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMLPR:
    try:
        return _entity_or_404(
            service.update_lpr(project_code, lpr_code, patch, _updated_by(request)),
            "LPR",
            lpr_code,
        )
    except CJMPatchValueError as error:
        raise _patch_value_error(error) from error


@router.post("/{project_code}/lprs/{lpr_code}/archive", response_model=CJMLPR)
def archive_project_lpr(
    request: Request,
    project_code: str,
    lpr_code: str,
    payload: ArchiveRequest,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMLPR:
    return _entity_or_404(
        service.archive_lpr(project_code, lpr_code, _updated_by(request), payload.archive_reason),
        "LPR",
        lpr_code,
    )


@router.patch("/{project_code}/barriers/{barrier_code}", response_model=CJMBarrier)
def patch_project_barrier(
    request: Request,
    project_code: str,
    barrier_code: str,
    patch: CJMBarrierPatch,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMBarrier:
    try:
        return _entity_or_404(
            service.update_barrier(project_code, barrier_code, patch, _updated_by(request)),
            "Barrier",
            barrier_code,
        )
    except CJMPatchValueError as error:
        raise _patch_value_error(error) from error


@router.post("/{project_code}/barriers/{barrier_code}/archive", response_model=CJMBarrier)
def archive_project_barrier(
    request: Request,
    project_code: str,
    barrier_code: str,
    payload: ArchiveRequest,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMBarrier:
    return _entity_or_404(
        service.archive_barrier(
            project_code,
            barrier_code,
            _updated_by(request),
            payload.archive_reason,
        ),
        "Barrier",
        barrier_code,
    )


@router.patch("/{project_code}/expectations/{expectation_code}", response_model=CJMExpectation)
def patch_project_expectation(
    request: Request,
    project_code: str,
    expectation_code: str,
    patch: CJMExpectationPatch,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMExpectation:
    try:
        return _entity_or_404(
            service.update_expectation(
                project_code,
                expectation_code,
                patch,
                _updated_by(request),
            ),
            "Expectation",
            expectation_code,
        )
    except CJMPatchValueError as error:
        raise _patch_value_error(error) from error


@router.post(
    "/{project_code}/expectations/{expectation_code}/archive",
    response_model=CJMExpectation,
)
def archive_project_expectation(
    request: Request,
    project_code: str,
    expectation_code: str,
    payload: ArchiveRequest,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMExpectation:
    return _entity_or_404(
        service.archive_expectation(
            project_code,
            expectation_code,
            _updated_by(request),
            payload.archive_reason,
        ),
        "Expectation",
        expectation_code,
    )


@router.patch("/{project_code}/kpis/{kpi_code}", response_model=CJMKPI)
def patch_project_kpi(
    request: Request,
    project_code: str,
    kpi_code: str,
    patch: CJMKPIPatch,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMKPI:
    try:
        return _entity_or_404(
            service.update_kpi(project_code, kpi_code, patch, _updated_by(request)),
            "KPI",
            kpi_code,
        )
    except CJMPatchValueError as error:
        raise _patch_value_error(error) from error


@router.post("/{project_code}/kpis/{kpi_code}/archive", response_model=CJMKPI)
def archive_project_kpi(
    request: Request,
    project_code: str,
    kpi_code: str,
    payload: ArchiveRequest,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMKPI:
    return _entity_or_404(
        service.archive_kpi(project_code, kpi_code, _updated_by(request), payload.archive_reason),
        "KPI",
        kpi_code,
    )


@router.patch(
    "/{project_code}/communications/{communication_code}",
    response_model=CJMCommunicationPoint,
)
def patch_project_communication(
    request: Request,
    project_code: str,
    communication_code: str,
    patch: CJMCommunicationPointPatch,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMCommunicationPoint:
    try:
        return _entity_or_404(
            service.update_communication(
                project_code,
                communication_code,
                patch,
                _updated_by(request),
            ),
            "Communication",
            communication_code,
        )
    except CJMPatchValueError as error:
        raise _patch_value_error(error) from error


@router.post(
    "/{project_code}/communications/{communication_code}/archive",
    response_model=CJMCommunicationPoint,
)
def archive_project_communication(
    request: Request,
    project_code: str,
    communication_code: str,
    payload: ArchiveRequest,
    service: Annotated[CJMUpdateService, Depends(get_cjm_update_service)],
) -> CJMCommunicationPoint:
    return _entity_or_404(
        service.archive_communication(
            project_code,
            communication_code,
            _updated_by(request),
            payload.archive_reason,
        ),
        "Communication",
        communication_code,
    )
