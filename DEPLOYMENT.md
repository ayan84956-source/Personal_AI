# Private cloud deployment

This app can be deployed to Streamlit Community Cloud and opened from any
device. The app requires a password, and PostgreSQL keeps conversations and
memories available across restarts and devices.

## 1. Create a hosted PostgreSQL database

Create a database with a PostgreSQL provider such as Supabase. Copy its
PostgreSQL connection URL and ensure SSL is enabled (`sslmode=require`).
Keep the URL private; it contains database credentials.

## 2. Push the app to GitHub

Create a GitHub repository containing the app files and push this project.
Do not commit `.env`, `.streamlit/secrets.toml`, the `.venv` directory, or
`data/personal_ai.db`. The provided `.gitignore` excludes these local files.

## 3. Deploy with Streamlit Community Cloud

Create a new app in Streamlit Community Cloud, select the repository and
branch, and set the app file path to `app.py`. In the app's **Settings →
Secrets**, add:

```toml
GROQ_API_KEY = "your Groq API key"
APP_PASSWORD = "a long, unique password"
DATABASE_URL = "postgresql://user:password@host:port/database?sslmode=require"
```

Use a strong password and do not share the app link or password publicly.
The login gate protects this single-user app and all conversations/memories
are shared in the same private account.

## 4. Optional: copy existing local data

The hosted database starts empty. To copy the local SQLite conversations and
memories, put the PostgreSQL URL in your local `.env` as `DATABASE_URL`, then
run this once from the project folder:

```powershell
.\.venv\Scripts\python.exe .\migrate_sqlite_to_postgres.py
```

Migration refuses to proceed if any hosted table already contains data. Back
up `data/personal_ai.db` before migrating.

## Local development

Local development continues to use SQLite unless `DATABASE_URL` is set. Add
`GROQ_API_KEY` and `APP_PASSWORD` to `.env` to run the password-protected app
locally.
