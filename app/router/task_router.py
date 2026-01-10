from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.db.schema import TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdate
from app.service import task_service


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# ===== Task CRUD ===== #

@router.post("/create", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task in a project"""
    return task_service.createTask(data, current_user, db)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID"""
    return task_service.getTaskById(task_id, current_user, db)


@router.get("/project/{project_id}", response_model=list[TaskResponse])
def get_tasks_by_project(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for a specific project"""
    return task_service.getAllTasksByProject(project_id, current_user, db, skip, limit)


@router.get("/", response_model=list[TaskResponse])
def get_all_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks in your organization"""
    return task_service.getAllTasksByOrg(current_user, db, skip, limit)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task"""
    return task_service.updateTask(task_id, data, current_user, db)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    return task_service.deleteTask(task_id, current_user, db)


# ===== Task Management ===== #

@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task status (todo, in_progress, done, blocked)"""
    return task_service.updateTaskStatus(task_id, data.status, current_user, db)


@router.get("/filter/status", response_model=list[TaskResponse])
def get_tasks_by_status(
    status_filter: str = Query(..., description="Filter by status: todo, in_progress, done, blocked"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks filtered by status"""
    return task_service.getTasksByStatus(status_filter, current_user, db, skip, limit)


@router.get("/statistics/overview")
def get_task_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task statistics (counts by status)"""
    return task_service.getTaskStatistics(current_user, db)
