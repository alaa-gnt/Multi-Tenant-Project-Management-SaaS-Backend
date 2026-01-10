from sqlalchemy.orm import Session
from app.db.repository import TaskRepository, ProjectRepository
from app.db.schema import TaskCreate, TaskUpdate, TaskResponse
from fastapi import HTTPException, status
from app.db.models.task import Task
from app.db.models.user import User


# ===== Task CRUD ===== #


# --------------------------------------------------------------------------------
def createTask(task_data: TaskCreate, current_user: User, db: Session) -> TaskResponse:
    """Create a new task in a project"""
    task_repo = TaskRepository(db)
    project_repo = ProjectRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization to create tasks."
        )
    
    # Verify project exists and belongs to user's org
    project = project_repo.get_by_id(task_data.project_id, current_user.org_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or doesn't belong to your organization."
        )
    
    # Create task with user's org_id
    task_dict = task_data.model_dump()
    task_dict['org_id'] = current_user.org_id
    task = Task(**task_dict)
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def getTaskById(task_id: int, current_user: User, db: Session) -> TaskResponse:
    """Get a specific task by ID"""
    task_repo = TaskRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Get task (org-scoped)
    task = task_repo.get_by_id(task_id, current_user.org_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    
    return task
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def getAllTasksByProject(project_id: int, current_user: User, db: Session, skip: int = 0, limit: int = 100) -> list[TaskResponse]:
    """Get all tasks for a specific project"""
    task_repo = TaskRepository(db)
    project_repo = ProjectRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Verify project exists and belongs to user's org
    project = project_repo.get_by_id(project_id, current_user.org_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or doesn't belong to your organization."
        )
    
    # Get tasks for project
    tasks = task_repo.get_all_by_project(project_id, current_user.org_id, skip, limit)
    
    return tasks
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def getAllTasksByOrg(current_user: User, db: Session, skip: int = 0, limit: int = 100) -> list[TaskResponse]:
    """Get all tasks in user's organization"""
    task_repo = TaskRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Get all tasks in org
    tasks = task_repo.get_all_by_organization(current_user.org_id, skip, limit)
    
    return tasks
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def updateTask(task_id: int, task_data: TaskUpdate, current_user: User, db: Session) -> TaskResponse:
    """Update a task"""
    task_repo = TaskRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Update task (org-scoped)
    updated_task = task_repo.update(task_id, current_user.org_id, task_data)
    if updated_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    
    return updated_task
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def deleteTask(task_id: int, current_user: User, db: Session) -> dict:
    """Delete a task"""
    task_repo = TaskRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Delete task (org-scoped)
    success = task_repo.delete(task_id, current_user.org_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    
    return {
        "message": "Task deleted successfully",
        "task_id": task_id
    }
# --------------------------------------------------------------------------------


# ===== Task Management ===== #


# --------------------------------------------------------------------------------
def updateTaskStatus(task_id: int, new_status: str, current_user: User, db: Session) -> TaskResponse:
    """Update task status (todo, in_progress, done, etc.)"""
    task_repo = TaskRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Validate status
    valid_statuses = ["todo", "in_progress", "done", "blocked"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Update status
    updated_task = task_repo.update_status(task_id, current_user.org_id, new_status)
    if updated_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    
    return updated_task
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def getTasksByStatus(status_filter: str, current_user: User, db: Session, skip: int = 0, limit: int = 100) -> list[TaskResponse]:
    """Get tasks filtered by status"""
    task_repo = TaskRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Get tasks by status
    tasks = task_repo.get_by_status(current_user.org_id, status_filter, skip, limit)
    
    return tasks
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def getTaskStatistics(current_user: User, db: Session) -> dict:
    """Get task statistics for user's organization"""
    task_repo = TaskRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization."
        )
    
    # Count tasks by status
    statuses = ["todo", "in_progress", "done", "blocked"]
    statistics = {}
    
    for status_item in statuses:
        count = task_repo.count_by_status(current_user.org_id, status_item)
        statistics[status_item] = count
    
    # Total tasks
    all_tasks = task_repo.get_all_by_organization(current_user.org_id)
    statistics["total"] = len(all_tasks)
    
    return statistics
# --------------------------------------------------------------------------------
