from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime
from app.db.models.project import Project
from app.db.schema.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project: ProjectCreate) -> Project:
        """Create a new project (org-scoped)"""
        db_project = Project(
            name=project.name,
            description=project.description,
            org_id=project.org_id,
            deadline=project.deadline
        )
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def get_by_id(self, project_id: int, org_id: int) -> Optional[Project]:
        """Get project by ID (org-scoped)"""
        return self.db.query(Project).filter(
            and_(Project.id == project_id, Project.org_id == org_id)
        ).first()

    def get_all_by_organization(self, org_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects in an organization"""
        return self.db.query(Project).filter(Project.org_id == org_id).offset(skip).limit(limit).all()

    def get_by_status(self, org_id: int, is_archived: bool = False, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get projects by status (archived/active) within org"""
        return self.db.query(Project).filter(
            and_(Project.org_id == org_id, Project.is_archived == is_archived)
        ).offset(skip).limit(limit).all()

    def get_with_tasks(self, project_id: int, org_id: int) -> Optional[Project]:
        """Get project with all tasks"""
        return self.db.query(Project).options(joinedload(Project.tasks)).filter(
            and_(Project.id == project_id, Project.org_id == org_id)
        ).first()

    def search_by_name(self, org_id: int, name: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """Search projects by name within org"""
        return self.db.query(Project).filter(
            and_(Project.org_id == org_id, Project.name.ilike(f"%{name}%"))
        ).offset(skip).limit(limit).all()

    def get_by_deadline_range(self, org_id: int, start_date: datetime, end_date: datetime) -> List[Project]:
        """Get projects by deadline range"""
        return self.db.query(Project).filter(
            and_(
                Project.org_id == org_id,
                Project.deadline.between(start_date, end_date)
            )
        ).all()

    def get_overdue_projects(self, org_id: int) -> List[Project]:
        """Get overdue projects (deadline passed and not archived)"""
        return self.db.query(Project).filter(
            and_(
                Project.org_id == org_id,
                Project.is_archived == False,
                Project.deadline < datetime.now()
            )
        ).all()

    def update(self, project_id: int, org_id: int, project_update: ProjectUpdate) -> Optional[Project]:
        """Update project details (org-scoped)"""
        db_project = self.get_by_id(project_id, org_id)
        if not db_project:
            return None

        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)

        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def archive(self, project_id: int, org_id: int) -> Optional[Project]:
        """Archive a project"""
        db_project = self.get_by_id(project_id, org_id)
        if not db_project:
            return None

        db_project.is_archived = True
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def unarchive(self, project_id: int, org_id: int) -> Optional[Project]:
        """Unarchive a project"""
        db_project = self.get_by_id(project_id, org_id)
        if not db_project:
            return None

        db_project.is_archived = False
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def delete(self, project_id: int, org_id: int) -> bool:
        """Delete project (org-scoped)"""
        db_project = self.get_by_id(project_id, org_id)
        if not db_project:
            return False

        self.db.delete(db_project)
        self.db.commit()
        return True
