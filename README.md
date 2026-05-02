# Smart Rental Application

A Django-based rental property application built from the `SearchingYourHome` project.

## Project structure

- `manage.py` — Django management script
- `SearchingYourHome/` — Django project settings and URLs
- `Room/` — main app containing models, views, templates, and forms
- `media/` — uploaded media and image assets
- `db.sqlite3` — local SQLite database (not tracked by Git)

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install Django==2.2.6
```

3. Run migrations:

```powershell
python manage.py migrate
```

4. Start the development server:

```powershell
python manage.py runserver
```

5. Open the app in your browser:

```text
http://127.0.0.1:8000/
```

## Notes

- The project is configured for Django 2.2 and SQLite.
- Sensitive settings (`SECRET_KEY`) are currently stored in `SearchingYourHome/settings.py`; move these to environment variables before deploying.
- `.gitignore` is configured to exclude virtual environments, IDE files, Python cache files, and database files.

## Recommended next steps

- Add `requirements.txt` for dependency management
- Create a `.env` file and update settings to load secret configuration from environment variables
- Remove any locally generated `.pyc` or IDE files from the working tree if still present
