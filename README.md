# TaskFlow Backend

Backend part of the **TaskFlow** project built with **Django** and **Django REST Framework**.  
This API provides authentication, task management, categories, comments, filtering, and CRUD operations. [file:1]

## Project Description

TaskFlow is a simple task management system where users can:
- register and log in,
- create categories,
- create and manage tasks,
- filter tasks by category and status,
- search tasks by title,
- mark tasks as done or not done,
- add comments to tasks. [file:1]

The backend is implemented according to the course requirements for a Django + DRF project, including models, serializers, FBV, CBV, authentication, CRUD, and CORS support. [file:1]

## Technologies

- Python
- Django
- Django REST Framework
- Simple JWT
- django-cors-headers
- SQLite [file:1]

## Main Features

- JWT authentication: register, login, logout, profile [file:1]
- Full CRUD for tasks [file:1]
- CRUD for categories [file:1]
- Task filtering by category [file:1]
- Task filtering by status [file:1]
- Task search by title [file:1]
- Comments for tasks
- Objects linked to authenticated user (`request.user`) [file:1]

## Models

The project contains the following models:
- `Category`
- `Task`
- `Comment`
- `TaskHistory` [file:1]

ForeignKey relationships are used between users, categories, tasks, and comments, which satisfies the backend requirements. [file:1]

## API Endpoints

### Auth
- `POST /api/register/`
- `POST /api/login/`
- `POST /api/logout/`
- `GET /api/profile/` [file:1]

### Categories
- `GET /api/categories/`
- `POST /api/categories/`
- `GET /api/categories/<id>/`
- `PUT /api/categories/<id>/`
- `DELETE /api/categories/<id>/` [file:1]

### Tasks
- `GET /api/tasks/`
- `POST /api/tasks/`
- `GET /api/tasks/<id>/`
- `PUT /api/tasks/<id>/`
- `PATCH /api/tasks/<id>/`
- `DELETE /api/tasks/<id>/` [file:1]

### Comments
- `GET /api/comments/`
- `POST /api/comments/` [file:1]

## Task Filters

Examples:
- `GET /api/tasks/?category=1`
- `GET /api/tasks/?status=done`
- `GET /api/tasks/?search=django` [file:1]

## Installation

Clone the repository and open the backend folder:

```bash
cd back
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

### Windows PowerShell
```bash
venv\Scripts\activate
```

### Windows CMD
```bash
venv\Scripts\activate.bat
```

Install dependencies:

```bash
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt
```

Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create superuser:

```bash
python manage.py createsuperuser
```

Run server:

```bash
python manage.py runserver
```

## Authentication

Protected endpoints require JWT access token in headers:

```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

This is needed for authenticated actions such as creating categories and tasks. [file:1]

## Example Request

### Login
```json
{
  "username": "testuser",
  "password": "12345678"
}
```

### Create category
```json
{
  "name": "Study",
  "color": "blue"
}
```

### Create task
```json
{
  "title": "Finish Django backend",
  "description": "Write models and API",
  "status": "not_done",
  "priority": "high",
  "due_date": "2026-04-10",
  "category": 1
}
```

## Notes

- CORS is configured for Angular dev server (`http://localhost:4200`). [file:1]
- Angular frontend communicates with this backend via HttpClient service, as required by the project description. [file:1]
- The project is prepared for Postman testing with JWT authentication and CRUD requests. [file:1]

## Author

Student project for Web Development course, KBTU. [file:1]
