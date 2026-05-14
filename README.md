# AURA Hotel

A Flask hotel-booking demo with SQLAlchemy persistence, Selenium/pytest coverage, a refreshed responsive UI, sign-up flow, and lightweight internationalization for English, Arabic, and Chinese.

## Features

- Room browsing with search, type filter, max-price validation, and room detail pages
- Account sign-up with full name, email, password confirmation, password guidance, and preferred language
- Login with the demo admin username or registered user email
- Protected booking and reservation management flows
- Availability checks, date validation, guest-capacity validation, and cancel states
- Language selector with persisted preference and Arabic RTL support
- Locale-aware client-side formatting using `Intl.NumberFormat` and `Intl.DateTimeFormat`
- Neutral design tokens, accessible focus states, reduced-motion support, and responsive layouts
- Admin dashboard with reservation stats and pytest history

## Quick Start

```powershell
pip install -r requirements.txt
python seed_db.py
python app.py
```

The app runs at `http://127.0.0.1:5000`.

## Demo Credentials

| Username | Password |
| --- | --- |
| `admin` | `1234` |

Registered users can sign in with their email address.

## Project Structure

```text
app.py                 Flask routes, auth, booking workflow, and i18n helpers
models.py              SQLAlchemy models
seed_db.py             Demo data seeding
requirements.txt       Runtime and test dependencies
static/css/styles.css  Design system and responsive UI styles
static/js/i18n-ui.js   Locale formatting and form enhancements
templates/             Jinja pages
translations/          en/ar/zh translation JSON files
tests/                 pytest and Selenium tests
```

## Internationalization

Translations live in `translations/{language}.json`. To add another language:

1. Add a language entry to `LANGUAGES` in `app.py`.
2. Create `translations/<code>.json` with the same keys as `translations/en.json`.
3. Set the correct `dir` value, especially for RTL languages.
4. Keep user-facing strings in templates behind `t("key")`.

## Testing

```powershell
pytest -v
pytest -v --html=report.html --self-contained-html
```

The dashboard reads `test_results/latest.json` and `test_results/history.json`, which are written by `tests/conftest.py` after pytest runs.

## Production Notes

- Replace the SQLite demo account creation in `/signup` with the production identity API when backend auth is ready.
- Move `app.secret_key` to an environment variable before deploying.
- Add CSRF protection before exposing write forms publicly.
- Keep color semantics paired with text/icons so status is never communicated by color alone.
