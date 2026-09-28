# Coderr Backend

Coderr is a Django REST Framework backend for a service marketplace. It provides
authentication, customer and business profiles, offers, orders, reviews,
statistics, file uploads, filtering, search, ordering, and token-based
authentication.

## Overview

The project implements the backend API for Coderr. Customers can browse offers,
place orders, and review business users. Business users can maintain their
profiles, publish service offers with pricing tiers, and update the status of
their orders.

## Features

- User registration and login
- DRF token authentication
- Customer and business account roles
- Customer and business profiles
- Profile and offer image uploads
- Service offers with basic, standard, and premium pricing tiers
- Offer filtering, search, ordering, and pagination
- Customer order creation
- Business order-status handling
- Reviews and ratings
- Object-level permissions
- Order counters
- Public platform statistics
- Automated Django API tests
- Environment-based configuration with `.env`
- Mentor-provided sample-data script

## Technology Stack

### Backend

- Python 3.10+
- Django 5.2
- Django REST Framework
- DRF Token Authentication
- django-filter
- django-cors-headers
- Pillow
- python-dotenv
- SQLite
- Coverage.py

## Project Structure

```text
Coderr/
├── backend/
│   ├── core/
│   ├── auth_app/
│   │   └── api/
│   ├── offers_app/
│   │   └── api/
│   ├── orders_app/
│   │   └── api/
│   ├── reviews_app/
│   │   └── api/
│   ├── app_auth/
│   ├── app_offers/
│   ├── app_orders/
│   ├── app_reviews/
│   ├── create_sample_data.py
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── .coveragerc
├── .gitignore
└── README.md
```

The four `*_app` directories are the actual Django apps. Each app keeps its API
logic inside an `api/` directory.

The `app_*` packages are lightweight compatibility shims used only by the
mentor-provided sample-data script. They are not registered as Django apps.

## Quick Start

### 1. Set up the backend

Clone the repository and open the project directory.

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
python backend\manage.py migrate
python backend\manage.py runserver
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
python backend/manage.py migrate
python backend/manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/api/
```

The Django admin will be available at:

```text
http://127.0.0.1:8000/admin/
```

### 2. Create an administrator account

With the virtual environment activated:

#### Windows PowerShell

```powershell
python backend\manage.py createsuperuser
```

#### macOS / Linux

```bash
python backend/manage.py createsuperuser
```

## Sample Data

The repository includes the mentor-provided `backend/create_sample_data.py`
script unchanged. It creates example customers, businesses, offers, orders, and
reviews.

The compatibility packages described above adapt the script's original model
imports and field names to this project without modifying the mentor script.

After migrations have been applied, run:

#### Windows PowerShell

```powershell
python backend\create_sample_data.py
```

#### macOS / Linux

```bash
python backend/create_sample_data.py
```

Useful sample usernames include `customer1`, `customer2`, `business1`,
`business2`, `customer_guest`, and `business_guest`. Their test passwords
are defined in the mentor-provided sample-data script.

The script uses `get_or_create()` so it can be run again without deliberately
duplicating the seeded records.

## Authentication

The API uses DRF token authentication. Authenticated requests send the token in
the following format:

```text
Authorization: Token <token>
```

### Public Endpoints

- `POST /api/registration/`
- `POST /api/login/`
- `GET /api/offers/`
- `GET /api/base-info/`

### Protected Endpoints

Profile endpoints, individual offers, offer details, orders, order counters, and
reviews require token authentication.

Write operations additionally enforce the customer, business, owner, reviewer,
or staff role required by the respective resource.

## Main API Areas

- Registration and login
- Customer and business profiles
- Offers and offer details
- Orders and order status handling
- Reviews and ratings
- Order counters
- General platform statistics via `/api/base-info/`

## Environment Configuration

The backend reads its environment variables from `backend/.env`.

Create the file from the provided example:

#### Windows PowerShell

```powershell
Copy-Item backend\.env.example backend\.env
```

#### macOS / Linux

```bash
cp backend/.env.example backend/.env
```

Example development configuration:

```env
SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

The real `.env` file is excluded from version control and must not be
committed. Replace the example secret key before using the project outside a
local development environment.

## Tests and Coverage

With the virtual environment activated, run the complete API test suite from the
repository root.

#### Windows PowerShell

```powershell
coverage erase
coverage run backend\manage.py test auth_app offers_app orders_app reviews_app
coverage report -m
```

#### macOS / Linux

```bash
coverage erase
coverage run backend/manage.py test auth_app offers_app orders_app reviews_app
coverage report -m
```

The coverage configuration excludes migrations, tests, Django entry-point files,
the unchanged mentor sample-data script, and its compatibility shims. The report
therefore measures the application code that implements the Coderr API.

## Uploaded Files

Profile images and offer images are stored locally in the `backend/media/`
directory during development. The media directory is excluded from Git.

With `DEBUG=True`, Django serves these files from the `/media/` URL during
local development.

## Database

The project uses SQLite for local development. The database file is excluded
from Git and is created locally when migrations are applied.

## Documentation

- `README.md` — project overview, setup, authentication, sample data, and tests
- `backend/.env.example` — example environment configuration
- `backend/create_sample_data.py` — mentor-provided sample-data script
