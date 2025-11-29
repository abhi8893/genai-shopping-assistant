# Ecom Backend Service

## Repo structure


```
.
├── core/
│   ├── config.py
│   ├── database.py
│   ├── logging.py
│   └── security.py
│
├── domains/
│   ├── users/
│   │   ├── models/
│   │   │   └── user.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   ├── api/
│   │   │   └── router.py
│   │   ├── migrations/
│   │   │   ├── env.py
│   │   │   ├── alembic.ini
│   │   │   └── versions/
│   │   └── __init__.py
│   │
│   ├── products/
│   │   ├── models/
│   │   ├── repository.py
│   │   ├── service.py
│   │   ├── api/
│   │   ├── migrations/
│   │   │   ├── env.py
│   │   │   ├── alembic.ini
│   │   │   └── versions/
│   │   └── __init__.py
│   │
│   ├── cart/
│   │   ├── models/
│   │   ├── repository.py
│   │   ├── service.py
│   │   ├── api/
│   │   ├── migrations/
│   │   └── __init__.py
│   │
│   └── auth/
│       ├── models/
│       ├── repository.py
│       ├── service.py
│       ├── api/
│       ├── migrations/
│       └── __init__.py
│
├── api/
│   ├── router.py       # central API gateway
│   └── dependencies.py
│
├── scripts/
│   └── run_all_migrations.py
│
├── app.py               # FastAPI entrypoint
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md

```