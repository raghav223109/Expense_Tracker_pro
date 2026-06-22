# Expense Pro

A simple Flask-based expense tracker web app.

## Features

- Track expenses and manage user accounts
- Templates for signup, login, password reset, and admin
- PWA-ready assets (service worker, manifest)

## Requirements

- Python 3.8+
- See dependencies in [requirements.txt](requirements.txt)

## Quick Start

1. Clone the repository and change directory:

```
git clone <repo-url>
cd expense_pro
```

2. Create and activate a virtual environment (Windows example):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
flask run
```

By default the app entry point is [app.py](app.py).

## Project Structure

- [app.py](app.py) – Flask application entry point
- [requirements.txt](requirements.txt) – Python dependencies
- [templates/](templates/) – Jinja2 HTML templates (index, login, signup, etc.)
- [static/manifest.json](static/manifest.json) – PWA manifest
- [static/style.css](static/style.css) – Stylesheet
- [static/sw.js](static/sw.js) – Service worker

## Templates

The UI templates are under the `templates` folder, including:

- [templates/index.html](templates/index.html)
- [templates/login.html](templates/login.html)
- [templates/signup.html](templates/signup.html)
- [templates/admin.html](templates/admin.html)

## Configuration

Place runtime configuration or secrets in the `instance/` folder (not checked into source control).

## Contributing

1. Fork the repo
2. Create a feature branch
3. Open a pull request with a clear description


