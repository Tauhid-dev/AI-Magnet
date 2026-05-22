# Database Migrations

Alembic migrations for the backend live here.

Run from the repository root:

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

The migration environment reads `DATABASE_URL` from the environment when present.
