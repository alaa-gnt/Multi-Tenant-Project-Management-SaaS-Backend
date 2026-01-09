from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import Optional, List
from app.db.models.task import Task
from app.db.schema.task import TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, task: TaskCreate) -> Task:
        """Create a new task (org-scoped)"""
        db_task = Task(
            title=task.title,
            content=task.content,
            status=task.status,
            project_id=task.project_id,
            org_id=task.org_id
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def get_by_id(self, task_id: int, org_id: int) -> Optional[Task]:
        """Get task by ID (org-scoped)"""
        return self.db.query(Task).filter(
            and_(Task.id == task_id, Task.org_id == org_id)
        ).first()

    def get_all_by_project(self, project_id: int, org_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks in a project"""
        return self.db.query(Task).filter(
            and_(Task.project_id == project_id, Task.org_id == org_id)
        ).offset(skip).limit(limit).all()

    def get_all_by_organization(self, org_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks in an organization"""
        return self.db.query(Task).filter(Task.org_id == org_id).offset(skip).limit(limit).all()

    def get_by_status(self, org_id: int, status: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get tasks by status within org"""
        return self.db.query(Task).filter(
            and_(Task.org_id == org_id, Task.status == status)
        ).offset(skip).limit(limit).all()

    def get_by_project_and_status(self, project_id: int, org_id: int, status: str) -> List[Task]:
        """Get tasks by project and status"""
        return self.db.query(Task).filter(
            and_(Task.project_id == project_id, Task.org_id == org_id, Task.status == status)
        ).all()

    def filter_tasks(
        self,
        org_id: int,
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Filter tasks by multiple criteria"""
        query = self.db.query(Task).filter(Task.org_id == org_id)

        if project_id is not None:
            query = query.filter(Task.project_id == project_id)

        if status is not None:
            query = query.filter(Task.status == status)

        return query.offset(skip).limit(limit).all()

    def get_with_project(self, task_id: int, org_id: int) -> Optional[Task]:
        """Get task with project details"""
        return self.db.query(Task).options(joinedload(Task.project)).filter(
            and_(Task.id == task_id, Task.org_id == org_id)
        ).first()

    def update(self, task_id: int, org_id: int, task_update: TaskUpdate) -> Optional[Task]:
        """Update task details (org-scoped)"""
        db_task = self.get_by_id(task_id, org_id)
        if not db_task:
            return None

        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def update_status(self, task_id: int, org_id: int, status: str) -> Optional[Task]:
        """Update task status"""
        db_task = self.get_by_id(task_id, org_id)
        if not db_task:
            return None

        db_task.status = status
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def bulk_update_status(self, task_ids: List[int], org_id: int, status: str) -> int:
        """Bulk update task statuses"""
        result = self.db.query(Task).filter(
            and_(Task.id.in_(task_ids), Task.org_id == org_id)
        ).update({"status": status}, synchronize_session=False)
        self.db.commit()
        return result

    def bulk_delete(self, task_ids: List[int], org_id: int) -> int:
        """Bulk delete tasks"""
        result = self.db.query(Task).filter(
            and_(Task.id.in_(task_ids), Task.org_id == org_id)
        ).delete(synchronize_session=False)
        self.db.commit()
        return result

    def delete(self, task_id: int, org_id: int) -> bool:
        """Delete task (org-scoped)"""
        db_task = self.get_by_id(task_id, org_id)
        if not db_task:
            return False

        self.db.delete(db_task)
        self.db.commit()
        return True

    def count_by_project(self, project_id: int, org_id: int) -> int:
        """Count tasks in a project"""
        return self.db.query(Task).filter(
            and_(Task.project_id == project_id, Task.org_id == org_id)
        ).count()

    def count_by_status(self, org_id: int, status: str) -> int:
        """Count tasks by status in organization"""
        return self.db.query(Task).filter(
            and_(Task.org_id == org_id, Task.status == status)
        ).count()
