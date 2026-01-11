# Multi-Tenant Project Management SaaS Backend

A robust FastAPI-based backend for a multi-tenant project management SaaS application with organization-based access control, JWT authentication, and comprehensive CRUD operations.

## 🚀 Features --

### Core Functionality
- **User Authentication**: JWT-based authentication with bcrypt password hashing
- **Multi-Tenant Architecture**: Organization-scoped data isolation
- **Deferred Organization Setup**: Users register first, then create or join organizations
- **Role-Based Access Control**: Owner, Admin, and Member roles with different permissions
- **Organization Management**: Create, update, invite members, transfer ownership
- **Project Management**: Create, update, archive projects with deadline tracking
- **Task Management**: Create, update tasks with status tracking (todo, in_progress, done, blocked)
- **Invite System**: Unique invite codes for organization member recruitment

### Key Features
- ✅ Organization invite codes with regeneration capability
- ✅ Project archiving and restoration
- ✅ Task status management and filtering
- ✅ Task statistics and overview
- ✅ Multi-tenant data isolation (all queries are org-scoped)
- ✅ Permission-based endpoints (owner/admin restrictions)

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose) + bcrypt (passlib)
- **Validation**: Pydantic v2
- **Containerization**: Docker (PostgreSQL)
- **API Documentation**: Swagger UI (auto-generated)

## 📊 Database Schema

![Database Schema](pm-database-prj.png)

### Tables Overview

#### Users
- User authentication and profile information
- Nullable `role` and `org_id` for deferred organization setup
- Can exist without organization until creating or joining one

#### Organizations
- Central tenant table for multi-tenant architecture
- Contains `invite_code` for member invitations
- Has one owner (user) and many members

#### Projects
- Belong to organizations
- Support archiving with `is_archived` flag
- Include deadline tracking

#### Tasks
- Belong to both projects and organizations (multi-tenant isolation)
- Status tracking: todo, in_progress, done, blocked
- Org-scoped for data isolation

### Database Schema (DBML)

```dbml
Table users {
  id integer [primary key, increment]
  name varchar [not null]
  email varchar [unique, not null]
  password varchar [not null]
  role varchar [null, note: 'owner, admin, or member']
  org_id integer [null, ref: > organizations.id]
}

Table organizations {
  id integer [primary key, increment]
  name varchar [not null]
  description varchar [null]
  owner_id integer [not null, ref: > users.id]
  invite_code varchar [unique, null, note: 'Format: ABC-DEF-123']
}

Table projects {
  id integer [primary key, increment]
  name varchar [not null]
  description varchar [null]
  org_id integer [not null, ref: > organizations.id]
  is_archived boolean [default: false]
  deadline timestamp [null]
}

Table tasks {
  id integer [primary key, increment]
  title varchar [not null]
  content varchar [null]
  status varchar [not null, note: 'todo, in_progress, done, blocked']
  project_id integer [not null, ref: > projects.id]
  org_id integer [not null, ref: > organizations.id]
}
```

**Visualize this schema**: Copy the DBML code above to [dbdiagram.io](https://dbdiagram.io/) for an interactive ER diagram.

## 📁 Project Structure

```
Multi-Tenant-Project-Management-SaaS-Backend/
├── app/
│   ├── core/
│   │   ├── database.py          # Database connection & session
│   │   ├── dependencies.py      # FastAPI dependencies (get_db, get_current_user)
│   │   └── security.py          # JWT & password hashing utilities
│   ├── db/
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── project.py
│   │   │   └── task.py
│   │   ├── repository/          # Data access layer
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── project.py
│   │   │   └── task.py
│   │   └── schema/              # Pydantic schemas
│   │       ├── user.py
│   │       ├── organization.py
│   │       ├── project.py
│   │       └── task.py
│   ├── router/                  # API endpoints
│   │   ├── auth_router.py
│   │   ├── user_router.py
│   │   ├── organization_router.py
│   │   ├── project_router.py
│   │   └── task_router.py
│   ├── service/                 # Business logic
│   │   ├── user_service.py
│   │   ├── organization_service.py
│   │   ├── project_service.py
│   │   └── task_service.py
│   └── utils/
│       └── init_db.py           # Database initialization
├── main.py                      # FastAPI application entry point
├── pm-database-prj.png          # Database schema diagram
└── README.md
```

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL (or Docker)
- pip & virtualenv

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Multi-Tenant-Project-Management-SaaS-Backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install fastapi sqlalchemy psycopg2-binary python-jose passlib bcrypt uvicorn
   ```

4. **Setup PostgreSQL Database**
   
   **Option A: Using Docker (Recommended)**
   ```bash
   docker run -d \
     --name postgres-pm \
     -e POSTGRES_USER=user \
     -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=postgres \
     -p 5432:5432 \
     postgres:latest
   ```

   **Option B: Local PostgreSQL**
   - Install PostgreSQL
   - Create database: `postgres`
   - Update connection string in `app/core/database.py`

5. **Configure Database Connection**
   
   Update `app/core/database.py`:
   ```python
   DATABASE_URL = "postgresql://user:password@localhost:5432/postgres"
   ```

6. **Run the application**
   ```bash
   fastapi dev main.py
   ```

   The API will be available at: `http://127.0.0.1:8000`
   
   Interactive API docs: `http://127.0.0.1:8000/docs`

## 📚 API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### Users (`/users`)
- `GET /users/me` - Get current user profile

### Organizations (`/organizations`)
- `POST /organizations/create` - Create organization (user becomes owner)
- `POST /organizations/join` - Join organization via invite code
- `GET /organizations/invite-code` - Get organization invite code
- `POST /organizations/invite-code/regenerate` - Regenerate invite code
- `GET /organizations/details` - Get organization details
- `PUT /organizations/members/role` - Update member role (owner/admin)
- `PUT /organizations/update` - Update organization details
- `DELETE /organizations/delete` - Delete organization (owner only)
- `DELETE /organizations/leave` - Leave organization
- `POST /organizations/transfer-ownership` - Transfer ownership

### Projects (`/projects`)
- `POST /projects/create` - Create project
- `GET /projects/{id}` - Get project by ID
- `GET /projects/` - Get all projects (paginated)
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project
- `POST /projects/{id}/archive` - Archive project
- `POST /projects/{id}/unarchive` - Unarchive project
- `GET /projects/archived/list` - Get archived projects

### Tasks (`/tasks`)
- `POST /tasks/create` - Create task
- `GET /tasks/{id}` - Get task by ID
- `GET /tasks/project/{project_id}` - Get all tasks by project
- `GET /tasks/` - Get all tasks in organization
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `PATCH /tasks/{id}/status` - Update task status
- `GET /tasks/filter/status` - Filter tasks by status
- `GET /tasks/statistics/overview` - Get task statistics

## 🧪 Testing with Postman

### 1. Register a User
```
POST http://127.0.0.1:8000/auth/register
Body (JSON):
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

### 2. Login
```
POST http://127.0.0.1:8000/auth/login
Body (x-www-form-urlencoded):
username: john@example.com
password: securepass123

Response: Copy the "access_token"
```

### 3. Set Authorization Header
For all subsequent requests, add:
```
Header:
Authorization: Bearer <your_access_token>
```

### 4. Create Organization
```
POST http://127.0.0.1:8000/organizations/create
Headers: Authorization: Bearer <token>
Body (JSON):
{
  "name": "My Company",
  "description": "Our awesome organization"
}
```

### 5. Create Project
```
POST http://127.0.0.1:8000/projects/create
Headers: Authorization: Bearer <token>
Body (JSON):
{
  "name": "Website Redesign",
  "description": "Redesign company website",
  "deadline": "2026-03-01T00:00:00"
}
```

### 6. Create Task
```
POST http://127.0.0.1:8000/tasks/create
Headers: Authorization: Bearer <token>
Body (JSON):
{
  "title": "Design homepage mockup",
  "content": "Create modern homepage design",
  "status": "todo",
  "project_id": 1
}
```

### 7. Invite Second User
```
GET http://127.0.0.1:8000/organizations/invite-code
Headers: Authorization: Bearer <token>

Response: Copy the invite_code (e.g., "ABC-DEF-123")

Register second user → Login → Use invite code:
POST http://127.0.0.1:8000/organizations/join
Headers: Authorization: Bearer <second_user_token>
Body (JSON):
{
  "invite_code": "ABC-DEF-123"
}
```

## 🔐 Authentication Flow

1. **User Registration**: User registers with email/password (no organization yet)
2. **Login**: User logs in and receives JWT token
3. **Organization Setup**: 
   - Option A: Create new organization → User becomes owner
   - Option B: Join existing organization via invite code → User becomes member
4. **Access Resources**: All project/task operations require user to belong to an organization

## 🎯 Key Design Decisions

### Deferred Organization Setup
Users can register and login without belonging to an organization. This allows:
- Flexible onboarding flow
- Users to decide between creating or joining organizations
- Proper role assignment based on action (owner vs member)

### Multi-Tenant Data Isolation
All queries for projects and tasks are org-scoped:
- Projects: Filtered by `current_user.org_id`
- Tasks: Filtered by `current_user.org_id`
- Prevents data leakage between organizations

### Repository Pattern
Separates data access logic from business logic:
- **Repository**: Database operations (CRUD)
- **Service**: Business logic, validation, permissions
- **Router**: HTTP endpoints, request/response handling

## 🔄 Workflow Example

```
1. Alice registers → Creates "TechCorp" organization (becomes owner)
2. Alice gets invite code: "ABC-DEF-123"
3. Bob registers → Joins "TechCorp" using code (becomes member)
4. Alice creates "Mobile App" project
5. Alice creates task "Design UI" in "Mobile App" project
6. Bob can view and update the task (same organization)
7. Charlie (from different org) cannot see TechCorp's data
```

##  Common Issues

### Database Connection Error
- Ensure PostgreSQL is running
- Check connection string in `app/core/database.py`
- Verify database exists: `postgres`

### Import Errors
- Ensure all dependencies are installed
- Check Python version (3.10+)

### Authentication Errors
- Verify JWT token is included in Authorization header
- Check token format: `Bearer <token>`
- Token may have expired (generate new one by logging in)

## 📄 License

This project is licensed under the MIT License.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using FastAPI**
