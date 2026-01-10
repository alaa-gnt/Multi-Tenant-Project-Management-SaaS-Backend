from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.db.schema import ProjectCreate, ProjectUpdate, ProjectResponse
from app.service import project_service


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


# ===== Project CRUD ===== #

@router.post("/create", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project in your organization"""
    return project_service.createProject(data, current_user, db)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project by ID"""
    return project_service.getProjectById(project_id, current_user, db)


@router.get("/", response_model=list[ProjectResponse])
def get_all_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active projects in your organization"""
    return project_service.getAllProjects(current_user, db, skip, limit)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a project (owner/admin only)"""
    return project_service.updateProject(project_id, data, current_user, db)


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project (owner/admin only)"""
    return project_service.deleteProject(project_id, current_user, db)


# ===== Project Management ===== #

@router.post("/{project_id}/archive", response_model=ProjectResponse)
def archive_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive a project (owner/admin only)"""
    return project_service.archiveProject(project_id, current_user, db)


@router.post("/{project_id}/unarchive", response_model=ProjectResponse)
def unarchive_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unarchive a project (owner/admin only)"""
    return project_service.unarchiveProject(project_id, current_user, db)


@router.get("/archived/list", response_model=list[ProjectResponse])
def get_archived_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all archived projects in your organization"""
    return project_service.getArchivedProjects(current_user, db, skip, limit)
