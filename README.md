# Cocktail REST API 🍹

REST API built using Django and Django REST Framework as a backend recruitment project.

The application allows users to manage cocktails and their ingredients through HTTP requests.

## Technologies

- Python
- Django
- Django REST Framework
- SQLite
- JWT Authentication
- Git & GitHub

## Features

- CRUD operations for cocktails
- Ingredient management using Many-to-Many relationships
- Filtering cocktails by name and count
- Pagination
- User registration
- JWT authentication
- Role-based permissions
- Automated API tests

## Installation

Clone the repository:

```
git clone https://github.com/ker-mie/cocktail-rest-api.git
cd cocktail-rest-api  
```

Create a virtual environment:

```
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```
pip install -r requirements.txt
```

Generate a secret key using:

```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Fill a `.env` file in the directory containing `manage.py`:

```
DJANGO_SECRET_KEY=your_generated_secret_key
```

Apply database migrations:

```
python manage.py migrate
```

Start the development server:

```
python manage.py runserver
```

## Running Tests

Run automated tests using:

```
python manage.py test
```
## API Documentation

Interactive API documentation is generated using **drf-spectacular** (OpenAPI 3.0).

After starting the development server, you can access:

| Documentation | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/api/docs/ |
| ReDoc | http://127.0.0.1:8000/api/redoc/ |
| OpenAPI Schema | http://127.0.0.1:8000/api/schema/ |

Swagger UI allows you to explore available endpoints, inspect request and response schemas, and test API requests directly from your browser.

## Authentication

The API supports session authentication and JSON Web Tokens (JWT).

JWT tokens can be obtained through the `/api/token/` endpoint.

Protected endpoints require authentication. Editing and deleting cocktails is restricted to administrators.

## Author

Jan Lenarcik
