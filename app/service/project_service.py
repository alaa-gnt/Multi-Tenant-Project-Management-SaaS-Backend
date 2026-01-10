from sqlalchemy.orm import Session
from app.db.repository import ProjectRepository
from app.db.schema import ProjectCreate, ProjectUpdate, ProjectResponse
from fastapi import HTTPException, status
from app.db.models.project import Project
from app.db.models.user import User


# ===== Project CRUD ===== #


# --------------------------------------------------------------------------------
def createProject(project_data: ProjectCreate, current_user: User, db: Session) -> ProjectResponse:
    """Create a new project in user's organization"""
    project_repo = ProjectRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization to create projects."
        )
    
    # Create project with user's org_id
    project_data.org_id = current_user.org_id
    project = project_repo.create(project_data)
    
    return project
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def getProjectById(project_id: int, current_user: User, db: Session) -> ProjectResponse:
    """Get a specific project by ID"""
    project_repo = ProjectRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Get project (org-scoped)
    project = project_repo.get_by_id(project_id, current_user.org_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    
    return project
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def getAllProjects(current_user: User, db: Session, skip: int = 0, limit: int = 100) -> list[ProjectResponse]:
    """Get all projects in user's organization"""
    project_repo = ProjectRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Get all projects in org
    projects = project_repo.get_all_by_organization(current_user.org_id, skip, limit)
    
    return projects
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def updateProject(project_id: int, project_data: ProjectUpdate, current_user: User, db: Session) -> ProjectResponse:
    """Update a project (owner/admin only)"""
    project_repo = ProjectRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Check if user has permission (owner or admin)
    if current_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner or admin can update projects."
        )
    
    # Update project (org-scoped)
    updated_project = project_repo.update(project_id, current_user.org_id, project_data)
    if updated_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    
    return updated_project
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def deleteProject(project_id: int, current_user: User, db: Session) -> dict:
    """Delete a project (owner/admin only)"""
    project_repo = ProjectRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Check if user has permission (owner or admin)
    if current_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner or admin can delete projects."
        )
    
    # Delete project (org-scoped)
    success = project_repo.delete(project_id, current_user.org_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    
    return {
        "message": "Project deleted successfully",
        "project_id": project_id
    }
# --------------------------------------------------------------------------------


# ===== Project Management ===== #


# --------------------------------------------------------------------------------
def archiveProject(project_id: int, current_user: User, db: Session) -> ProjectResponse:
    """Archive a project (owner/admin only)"""
    project_repo = ProjectRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Check if user has permission
    if current_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner or admin can archive projects."
        )
    
    # Archive project
    archived_project = project_repo.archive(project_id, current_user.org_id)
    if archived_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    
    return archived_project
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def unarchiveProject(project_id: int, current_user: User, db: Session) -> ProjectResponse:
    """Unarchive a project (owner/admin only)"""
    project_repo = ProjectRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Check if user has permission
    if current_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner or admin can unarchive projects."
        )
    
    # Unarchive project
    unarchived_project = project_repo.unarchive(project_id, current_user.org_id)
    if unarchived_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    
    return unarchived_project
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def getArchivedProjects(current_user: User, db: Session, skip: int = 0, limit: int = 100) -> list[ProjectResponse]:
    """Get all archived projects in user's organization"""
    project_repo = ProjectRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Get archived projects
    projects = project_repo.get_by_status(current_user.org_id, is_archived=True, skip=skip, limit=limit)
    
    return projects
# --------------------------------------------------------------------------------
