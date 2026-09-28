# Coderr Backend

Coderr is a Django REST Framework backend for a service marketplace. It provides
authentication, user profiles, offers, orders, reviews, statistics, file
uploads, filtering, search, ordering, and token-based authentication.

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
│   ├── app_auth/
│   ├── app_offers/
│   ├── app_orders/
│   ├── app_reviews/
│   ├── create_sample_data.py
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
└── README.md
```

The four `*_app` directories are the actual Django apps and each keeps its API
logic inside an `api/` directory. The `app_*` packages are lightweight
compatibility shims used only by the mentor-provided sample-data script. They are
not registered as Django apps.

## Main API Areas

- Registration and login
- Customer and business profiles
- Offers and offer details
- Orders and order status handling
- Reviews and ratings
- Order counters
- General platform statistics via `/api/base-info/`

The API uses DRF token authentication. Authenticated requests send the token in
the following format:

```text
Authorization: Token <token>
```

### Public and Protected Endpoints

Public endpoints:

- `POST /api/registration/`
- `POST /api/login/`
- `GET /api/offers/`
- `GET /api/base-info/`

Profile endpoints, individual offers, offer details, orders, order counters, and
reviews require token authentication. Write operations additionally enforce the
customer, business, owner, reviewer, or staff role required by that resource.

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

The example configuration contains development values. Replace the secret key
before using the project outside a local development environment.

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

## Sample Data

The repository includes the mentor-provided `backend/create_sample_data.py`
script unchanged. It creates example customers, businesses, offers, orders, and
reviews. The compatibility packages described above adapt its original model
imports and field names to this project without modifying the mentor script.

After migrations have been applied, run:

```powershell
python backend\create_sample_data.py
```

Useful sample usernames include `customer1`, `customer2`, `business1`,
`business2`, `customer_guest`, and `business_guest`. Their test passwords
are defined in the mentor-provided sample-data script.

The script uses `get_or_create()` so it can be run again without deliberately
duplicating the seeded records.

## Environment Variables

The backend reads its environment variables from `backend/.env`.

```env
SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

The real `.env` file is excluded from Git and must not be committed.

## Tests and Coverage

Run the complete API test suite from the repository root:

```powershell
coverage erase
coverage run backend\manage.py test auth_app offers_app orders_app reviews_app
coverage report -m
```

The coverage configuration excludes migrations, tests, Django entry-point files,
the unchanged mentor sample-data script, and its compatibility shims. The report
therefore measures the application code that implements the Coderr API.

## Uploaded Files

Profile images and offer images are stored locally in the `backend/media/`
directory during development. The media directory is excluded from Git. With
`DEBUG=True`, Django serves these files from the `/media/` URL during local
development.

## Database

The project uses SQLite for local development. The database file is excluded
from Git and is created locally when migrations are applied.
