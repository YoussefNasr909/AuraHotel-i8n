# AURA Hotel - Global Personalization Engine

AURA Hotel is a comprehensive Flask hotel-booking web application featuring a robust **Global Regional Personalization Engine**, SQLAlchemy database persistence, Selenium/pytest coverage, and a fully dynamic, responsive UI. 

The application is built to seamlessly adapt its language, currency, unit systems, time formats, and aesthetic color palettes based on a user's selected global region.

## ✨ Core Features

- **Regional Personalization Engine**: Automatically sets local currency (e.g., USD, GBP, JPY), date/time formats (12h vs 24h), and unit systems (metric vs imperial) based on the user's region.
- **Dynamic Aesthetic Color Themes**: Automatically applies one of 5 distinct color palettes to match the regional identity (Global Blue, Indigo Europe, Desert Gold, Imperial Crimson, Emerald Green).
- **Lightweight Internationalization (i18n)**: Full language support for English, Arabic, and Chinese, complete with Right-to-Left (RTL) layout transitions.
- **Simple OpenSSL Integration**: Includes `pyOpenSSL`, a small health endpoint, and an optional local HTTPS mode for development.
- **Client-Side Localization**: Uses modern `Intl.NumberFormat` and `Intl.DateTimeFormat` via `region.js` to instantly format currencies, numbers, and dates without server-side reloading.
- **Booking & Reservations**: Room browsing, availability overlap checks, date validation, guest capacity limits, and a reservation management flow.
- **Admin Dashboard**: Analytics, reservation stats, and historical pytest results.
- **Modern UI/UX**: Neutral design tokens, accessible focus states, dynamic gradients using CSS `color-mix`, and smooth micro-animations.

## 🚀 Quick Start

Ensure you have Python installed, then run the following in your terminal (Powershell/Cmd):

```powershell
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Seed the Database (Creates all regional accounts & rooms)
python seed_db.py

# 3. Start the Flask Application
python app.py
```

The app will start at `http://127.0.0.1:5000`.

If you want simple local HTTPS for development:

```powershell
$env:FLASK_USE_HTTPS="1"
python app.py
```

Then open `https://127.0.0.1:5000`.

## 🌍 Supported Regions & Demo Credentials

When you run `python seed_db.py`, the database is populated with multiple test accounts. Each account is strictly tied to a region, triggering a unique combination of languages, currencies, and color themes.

**Universal Password for all accounts:** `1234`

| Region | Username | Language | Currency | Theme Palette |
| :--- | :--- | :--- | :--- | :--- |
| **Admin (US)** | `admin` | English | USD ($) | Global Blue |
| **United Kingdom** | `user_gb` | English | GBP (£) | Royal Indigo |
| **European Union** | `user_eu` | English | EUR (€) | Royal Indigo |
| **Egypt** | `user_eg` | Arabic (RTL) | EGP (E£) | Desert Gold |
| **Saudi Arabia** | `user_sa` | Arabic (RTL) | SAR (﷼) | Desert Gold |
| **UAE** | `user_ae` | Arabic (RTL) | AED (د.إ) | Desert Gold |
| **China** | `user_cn` | Chinese | CNY (¥) | Imperial Crimson |
| **Japan** | `user_jp` | English | JPY (¥) | Imperial Crimson |
| **India** | `user_in` | English | INR (₹) | Emerald Green |

*Log in with any of these accounts to instantly see the entire application transform its UI, language, and formatting.*

## 📁 Project Structure

```text
app.py                 Flask routing, context processors, auth, and booking logic.
models.py              SQLAlchemy schema (User, Room, Reservation).
seed_db.py             Database population script for rooms and regional users.
static/css/styles.css  Core design system, variables, layouts, and components.
static/css/themes.css  Color palettes for the 5 global regional themes.
static/js/region.js    Client-side Intl formatter and theme engine.
templates/             Jinja2 HTML templates.
translations/          JSON dictionary files (en, ar, zh).
tests/                 Pytest and Selenium browser automation tests.
instance/              (Generated) SQLite database directory.
```

## 🛠️ Personalization Architecture

1. **Backend Injection**: When a user logs in, `app.py` looks up their `region` and injects the strict regional configurations (currency code, color theme name, layout direction) directly into the Jinja template rendering context via `@app.context_processor`.
2. **HTML Data Attributes**: The `base.html` template receives these variables and applies them to the `<html>` tag as `data-color-theme` and `dir`, as well as on UI elements as `data-currency` and `data-currency-code`.
3. **CSS Execution**: `themes.css` catches the `data-color-theme` attribute and overrides the global `--primary` and `--accent` CSS variables. `styles.css` handles the rendering dynamically using `color-mix()`.
4. **JS Formatting**: `region.js` reads the HTML data-attributes, grabs the user's localized browser environment, and loops through the DOM to rewrite raw numbers/dates into highly accurate local formats using `Intl.NumberFormat`.

## 🧪 Testing

The project uses `pytest` and `selenium` to ensure reliability.

```powershell
# Run all tests
pytest -v

# Generate a detailed HTML report
pytest -v --html=report.html --self-contained-html
```

Test results are automatically written to `test_results/latest.json` which is consumed by the Admin Dashboard.

## 🔒 How to Verify OpenSSL is Working

To make sure OpenSSL is fully working in your project, you can verify it in two ways: via the automated test suite and by running the local server in HTTPS mode.

### 1. Run the Local Server with HTTPS Enabled
This tests if Flask can successfully use OpenSSL to generate a temporary SSL certificate and secure your traffic.

Run this command in your PowerShell terminal:
```powershell
$env:FLASK_USE_HTTPS="1"; .\.venv\Scripts\python app.py
```

**What to look for:**
Look at your terminal output. You should see the server running on `https` instead of `http`:
```text
 * Running on https://127.0.0.1:5000
```
While the server is running, open your browser and go to `https://127.0.0.1:5000/health/openssl`. You will see a JSON response confirming that OpenSSL is available and `https_enabled` is true! *(Note: your browser may warn you about a "self-signed certificate," which is completely normal for local development. Proceed past the warning.)* 

*(Press `CTRL+C` to stop the server when you're done).*

### 2. Run the OpenSSL Automated Test
Your project already has a specific test written to verify the OpenSSL diagnostics endpoint. You can run just this test to confirm it works programmatically. 

Run this command in your PowerShell terminal:
```powershell
.\.venv\Scripts\python -m pytest tests/test_signup_i18n.py::test_openssl_health_endpoint_exposes_status -v
```

**What to look for:**
You should see a green `PASSED` message like this:
```text
tests/test_signup_i18n.py::test_openssl_health_endpoint_exposes_status PASSED [100%]
```

If both of these checks work, your OpenSSL integration is perfectly configured and healthy!
