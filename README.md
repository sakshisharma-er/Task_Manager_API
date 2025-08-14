# Task Manager API

A Django REST Framework project for managing tasks with role-based permissions.

<!-- ***************************Setup******************************* -->
1. Clone repo and create virtual environment.
    python -m venv venv
    venv\Scripts\activate

2. Install dependencies:
bash
pip install -r requirements.txt

3. for migrations use
    py manage.py makemigrations
    py manage.py migrate
<!-- ******************User Role******************** -->
User Roles

Admin: Full permissions (is_staff=True, is_superuser=True)

Staff: Limited permissions (is_staff=True, is_superuser=False)
<!-- *********************Permissions********************** -->
Permissions
Method Access
POST:-Staff & Admin
PUT:-Staff & Admin
DELETE:-Admin only
GET:-Any authenticated