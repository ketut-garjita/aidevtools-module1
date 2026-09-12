# Household Chores Manager (ChoreMate)

A web application built with Django and Tailwind CSS for managing shared household chores among roommates and flatmates.

## Features
- **Chore Model & Management**: Track title, description, assigned roommate, due date, status (`pending`, `completed`), and completion date.
- **Django Admin Integration**: Full administrative interface with search, status filters, and bulk actions.
- **Chore Dashboard & List**: Real-time statistics, overdue indicators, filter by status and assigned roommate.
- **Chore Creation**: User-friendly form with date selection and input validation.
- **One-Click Completion**: Mark chores done with automatic completion timestamp recording.
- **Comprehensive Unit & Integration Tests**: 100% test coverage for models, views, and admin.

---

## Setup & Running the Application

### 1. Activate the Virtual Environment
On Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Apply Database Migrations
```powershell
python manage.py migrate
```

### 3. (Optional) Create Admin Superuser
```powershell
python manage.py createsuperuser
```

### 4. Run the Development Server
```powershell
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.
Visit `http://127.0.0.1:8000/admin/` to access the Django Admin interface.

---

## Running Tests
```powershell
python manage.py test
```