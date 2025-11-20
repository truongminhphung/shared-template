

project/
├── alembic/                 # Database Migration Scripts (versioned)
│   ├── versions/
│   └── env.py
├── alembic.ini              # Alembic Config
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── health.py    # Health Check endpoint
│   ├── core/
│   │   ├── config.py        # Settings and Env Config (add if missing)
│   │   ├── exceptions.py    # Global Error Handling
│   │   └── middleware.py    # CORS, Request IDs
│   ├── db/
│   │   ├── session.py       # Database Session Management (add if missing)
│   │   └── base.py          # Declarative Base (add if missing)
│   ├── models/
│   │   └── user.py          # Example Model (add your models)
│   ├── services/
│   │   └── user_service.py  # Example Service Layer (business logic)
│   └── main.py              # Application entry point (FastAPI instance)
├── tests/                   # Unit & Integration Tests
│   └── test_health.py       # Example test (add your tests)
├── Dockerfile               # Containerization spec
├── pyproject.toml           # Project metadata/dependencies
├── README.md                # Project documentation (recommended)
└── .env                     # Environment variables (recommended, ignored by VCS)
