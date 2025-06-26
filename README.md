# Minimal E-commerce Django Project

This is a minimal e-commerce web application built with Django and PostgreSQL.

## Features
- User authentication (JWT)
- Product catalog and categories
- Shopping cart and checkout
- Order management
- Admin interface

## Project Structure
```
e-comm-project/
├── manage.py
├── Pipfile / Pipfile.lock
├── .env
├── store/           # Main Django app
├── templates/       # HTML templates
├── static/          # Static files
├── media/           # Uploaded media
└── ...
```

## Prerequisites
- [Python 3.8+](https://www.python.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Pipenv](https://pipenv.pypa.io/en/latest/)

## Environment Variables
Set your database credentials in the `.env` file:
```
DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```
> Note: `DB_HOST` should be `localhost` when running locally.

## Quick Start

1. **Install dependencies:**
    ```
    pipenv install
    ```

2. **Apply migrations:**
    ```
    python manage.py migrate
    ```

3. **Create a superuser:**
    ```
    python manage.py createsuperuser
    ```

4. **Run the development server:**
    ```
    python manage.py runserver
    ```

5. **Access the app:**
    - Web: [http://localhost:8000/](http://localhost:8000/)
    - Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

## Useful Commands
- Run tests:
  ```
  python manage.py test
  ```
- Collect static files:
  ```python manage.py collectstatic --noinput
  ```

## Notes
- Static and media files are stored in the `static/` and `media/` directories.
- Update your Django `settings.py` to use environment variables for database configuration.
