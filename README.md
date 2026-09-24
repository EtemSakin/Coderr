# Coderr Backend

Coderr is a Django REST Framework backend for a service marketplace. It provides authentication, user profiles, offers, orders, reviews, statistics, file uploads, filtering, search, ordering, and token-based authentication.

## Tech Stack

- Python 3.10+
- Django 5.2
- Django REST Framework
- Django Filter
- SQLite
- Token Authentication
- Pillow
- python-dotenv

## Project Structure

```text
Coderr/
├── backend/
│   ├── core/
│   ├── auth_app/
│   ├── offers_app/
│   ├── orders_app/
│   ├── reviews_app/
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
└── README.md
```

Each Django app keeps its API logic inside an `api/` directory.

## Main API Areas

- Registration and login
- Customer and business profiles
- Offers and offer details
- Orders and order status handling
- Reviews and ratings
- Order counters
- General platform statistics via `/api/base-info/`

The API uses DRF token authentication. Authenticated requests send the token in the following format:

```text
Authorization: Token <token>
```

## Local Setup

Clone the repository and open the project directory.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r backend\requirements.txt
```

Create the local environment file:

```powershell
Copy-Item backend\.env.example backend\.env
```

The example configuration contains development values. Replace the secret key before using the project outside a local development environment.

Apply the database migrations:

```powershell
python backend\manage.py migrate
```

Create an administrator account if needed:

```powershell
python backend\manage.py createsuperuser
```

Start the development server:

```powershell
python backend\manage.py runserver
```

The API is then available at:

```text
http://127.0.0.1:8000/api/
```

The Django admin is available at:

```text
http://127.0.0.1:8000/admin/
```

## Environment Variables

The backend reads its environment variables from `backend/.env`.

```env
SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

The real `.env` file is excluded from Git and must not be committed.

## Uploaded Files

Profile images and offer images are stored locally in the `backend/media/` directory during development. The media directory is excluded from Git.

## Database

The project uses SQLite for local development. The database file is excluded from Git and is created locally when migrations are applied.
