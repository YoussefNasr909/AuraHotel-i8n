from flask import Flask, render_template, request, redirect, url_for, session, flash, g, make_response, abort, jsonify
from functools import wraps
from datetime import datetime
import json
import os
import re
from pathlib import Path
from models import db, User, Room, Reservation
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# ─── Language Configuration ───────────────────────────────────────
LANGUAGES = {
    "en": {"name": "English", "dir": "ltr", "locale": "en-US"},
    "ar": {"name": "العربية", "dir": "rtl", "locale": "ar-EG"},
    "zh": {"name": "中文", "dir": "ltr", "locale": "zh-CN"},
    "es": {"name": "Español", "dir": "ltr", "locale": "es-ES"},
    "hi": {"name": "हिन्दी", "dir": "ltr", "locale": "hi-IN"},
}
DEFAULT_LANGUAGE = "en"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TRANSLATIONS = {}

# ─── Region Configuration ────────────────────────────────────────
REGIONS = {
    "US": {"name": "United States",        "currency": "USD", "locale": "en-US",  "theme": "global",     "unitSystem": "imperial", "tempUnit": "fahrenheit", "timeFormat": "12h"},
    "GB": {"name": "United Kingdom",       "currency": "GBP", "locale": "en-GB",  "theme": "europe",     "unitSystem": "metric",   "tempUnit": "celsius",    "timeFormat": "24h"},
    "EU": {"name": "European Union",       "currency": "EUR", "locale": "en-IE",  "theme": "europe",     "unitSystem": "metric",   "tempUnit": "celsius",    "timeFormat": "24h"},
    "ES": {"name": "Spain",                "currency": "EUR", "locale": "es-ES",  "theme": "iberia",     "unitSystem": "metric",   "tempUnit": "celsius",    "timeFormat": "24h"},
    "EG": {"name": "Egypt",                "currency": "EGP", "locale": "ar-EG",  "theme": "middleEast", "unitSystem": "metric",   "tempUnit": "celsius",    "timeFormat": "12h"},
    "SA": {"name": "Saudi Arabia",         "currency": "SAR", "locale": "ar-SA",  "theme": "middleEast", "unitSystem": "metric",   "tempUnit": "celsius",    "timeFormat": "12h"},
    "AE": {"name": "United Arab Emirates", "currency": "AED", "locale": "ar-AE",  "theme": "middleEast", "unitSystem": "metric",   "tempUnit": "celsius",    "timeFormat": "12h"},
    "CN": {"name": "China",                "currency": "CNY", "locale": "zh-CN",  "theme": "eastAsia",   "unitSystem": "metric",   "tempUnit": "celsius",    "timeFormat": "24h"},
    "JP": {"name": "Japan",                "currency": "JPY", "locale": "ja-JP",  "theme": "eastAsia",   "unitSystem": "metric",   "tempUnit": "celsius",    "timeFormat": "24h"},
    "IN": {"name": "India",                "currency": "INR", "locale": "hi-IN",  "theme": "southAsia",  "unitSystem": "metric",   "tempUnit": "celsius",    "timeFormat": "12h"},
}

VALID_THEMES = {"global", "middleEast", "eastAsia", "europe", "southAsia", "iberia"}
VALID_THEME_MODES = {"light", "dark", "system"}
VALID_UNIT_SYSTEMS = {"metric", "imperial"}
VALID_TEMP_UNITS = {"celsius", "fahrenheit"}
VALID_TIME_FORMATS = {"12h", "24h"}


def load_translations():
    translations_dir = Path(__file__).with_name("translations")
    data = {}
    for lang in LANGUAGES:
        file_path = translations_dir / f"{lang}.json"
        if file_path.exists():
            data[lang] = json.loads(file_path.read_text(encoding="utf-8"))
        else:
            data[lang] = {}
    return data


TRANSLATIONS = load_translations()


def translate(key, lang=None, **kwargs):
    lang = lang or getattr(g, "lang", session.get("lang", DEFAULT_LANGUAGE))
    value = TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS[DEFAULT_LANGUAGE].get(key) or key
    if kwargs:
        return value.format(**kwargs)
    return value


def current_language():
    requested = request.args.get("lang") or request.form.get("lang")
    stored = session.get("lang") or request.cookies.get("aura_lang")
    lang = requested or stored or DEFAULT_LANGUAGE
    return lang if lang in LANGUAGES else DEFAULT_LANGUAGE


def valid_password(password):
    return (
        len(password) >= 8
        and re.search(r"[A-Za-z]", password)
        and re.search(r"\d", password)
    )


def format_currency(value, currency=None):
    """Server-side currency formatter. Client JS overrides with Intl."""
    amount = float(value)
    if currency is None:
        region = session.get("region", "US")
        currency = REGIONS.get(region, REGIONS["US"])["currency"]

    locale = LANGUAGES.get(getattr(g, "lang", DEFAULT_LANGUAGE), LANGUAGES[DEFAULT_LANGUAGE])["locale"]

    # Basic server-side formatting; the client-side Intl formatter refines this
    if currency == "JPY":
        formatted = f"{amount:,.0f}"
    else:
        formatted = f"{amount:,.2f}"

    # Simple symbol mapping for server-side fallback
    symbols = {
        "USD": "$", "GBP": "£", "EUR": "€", "EGP": "E£",
        "SAR": "﷼", "AED": "د.إ", "CNY": "¥", "JPY": "¥", "INR": "₹",
    }
    symbol = symbols.get(currency, currency)

    if locale.startswith("ar"):
        return f"{formatted} {symbol}"
    return f"{symbol}{formatted}"


def format_date(value):
    if not value:
        return ""
    if getattr(g, "lang", DEFAULT_LANGUAGE) == "ar":
        return value.strftime("%d/%m/%Y")
    if getattr(g, "lang", DEFAULT_LANGUAGE) == "zh":
        return value.strftime("%Y/%m/%d")
    return value.strftime("%b %d, %Y")


def ensure_user_columns():
    """Auto-migrate missing columns for development convenience."""
    columns = {
        row[1] for row in db.session.execute(db.text("PRAGMA table_info(user)")).fetchall()
    }
    additions = {
        "full_name":         "ALTER TABLE user ADD COLUMN full_name VARCHAR(160)",
        "email":             "ALTER TABLE user ADD COLUMN email VARCHAR(255)",
        "preferred_language":"ALTER TABLE user ADD COLUMN preferred_language VARCHAR(8) DEFAULT 'en'",
        "region":            "ALTER TABLE user ADD COLUMN region VARCHAR(8) DEFAULT 'US'",
        "currency":          "ALTER TABLE user ADD COLUMN currency VARCHAR(8) DEFAULT 'USD'",
        "unit_system":       "ALTER TABLE user ADD COLUMN unit_system VARCHAR(10) DEFAULT 'metric'",
        "temperature_unit":  "ALTER TABLE user ADD COLUMN temperature_unit VARCHAR(12) DEFAULT 'celsius'",
        "time_format":       "ALTER TABLE user ADD COLUMN time_format VARCHAR(4) DEFAULT '12h'",
        "theme_mode":        "ALTER TABLE user ADD COLUMN theme_mode VARCHAR(8) DEFAULT 'system'",
        "color_theme":       "ALTER TABLE user ADD COLUMN color_theme VARCHAR(16) DEFAULT 'global'",
    }
    for column, statement in additions.items():
        if column not in columns:
            db.session.execute(db.text(statement))
    db.session.commit()


@app.before_request
def set_locale():
    g.lang = current_language()
    g.dir = LANGUAGES[g.lang]["dir"]
    if g.lang != session.get("lang"):
        session["lang"] = g.lang


@app.after_request
def persist_locale(response):
    response.set_cookie("aura_lang", g.get("lang", DEFAULT_LANGUAGE), max_age=60 * 60 * 24 * 365, samesite="Lax")
    return response


@app.context_processor
def inject_i18n():
    region = session.get("region", "US")
    region_config = REGIONS.get(region, REGIONS["US"])

    return {
        "t": translate,
        "languages": LANGUAGES,
        "regions": REGIONS,
        "current_lang": getattr(g, "lang", DEFAULT_LANGUAGE),
        "current_dir": getattr(g, "dir", "ltr"),
        "current_region": region,
        "current_currency": region_config["currency"],
        "current_theme_mode": session.get("theme_mode", "system"),
        "current_color_theme": region_config["theme"],
        "format_currency": format_currency,
        "format_date": format_date,
    }


with app.app_context():
    db.create_all()
    ensure_user_columns()


def load_test_results():
    results_dir = Path("test_results")
    latest_file = results_dir / "latest.json"
    history_file = results_dir / "history.json"

    latest = None
    history = []

    if latest_file.exists():
        try:
            latest = json.loads(latest_file.read_text(encoding="utf-8"))
        except Exception:
            latest = None

    if history_file.exists():
        try:
            history = json.loads(history_file.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = []
        except Exception:
            history = []

    return latest, history


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            flash(translate("flash.login_required"), "warning")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in") or not session.get("is_admin"):
            flash(translate("flash.admin_required"), "danger")
            return redirect(url_for("home"))
        return view_func(*args, **kwargs)
    return wrapper


# ─── Language Switch ────────────────────────────────────────────
@app.route("/language", methods=["POST"])
def set_language():
    lang = request.form.get("lang", DEFAULT_LANGUAGE)
    if lang in LANGUAGES:
        session["lang"] = lang
    redirect_to = request.form.get("next") or request.referrer or url_for("home")
    response = make_response(redirect(redirect_to))
    response.set_cookie("aura_lang", session.get("lang", DEFAULT_LANGUAGE), max_age=60 * 60 * 24 * 365, samesite="Lax")
    return response

@app.route("/set_theme", methods=["POST"])
def set_theme():
    data = request.get_json()
    if data and "theme_mode" in data:
        mode = data["theme_mode"]
        if mode in VALID_THEME_MODES:
            session["theme_mode"] = mode
            if session.get("logged_in"):
                user = User.query.get(session["user_id"])
                if user:
                    user.theme_mode = mode
                    db.session.commit()
            return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid theme mode"}), 400




# ─── Pages ──────────────────────────────────────────────────────
@app.route("/")
def home():
    q = request.args.get("q", "").strip()
    rooms_query = Room.query
    if q:
        rooms_query = rooms_query.filter(
            (Room.name.ilike(f'%{q}%')) | 
            (Room.type.ilike(f'%{q}%')) | 
            (Room.desc.ilike(f'%{q}%'))
        )
    featured = rooms_query.limit(3).all()
    return render_template("home.html", featured=featured, q=q)


@app.route("/rooms")
def rooms():
    q = request.args.get("q", "").strip()
    room_type = request.args.get("type", "").strip()
    max_price = request.args.get("max_price", "").strip()

    rooms_query = Room.query

    if q:
        rooms_query = rooms_query.filter(
            (Room.name.ilike(f'%{q}%')) | 
            (Room.type.ilike(f'%{q}%')) | 
            (Room.desc.ilike(f'%{q}%'))
        )
    if room_type:
        rooms_query = rooms_query.filter(Room.type == room_type)
    if max_price:
        try:
            price_value = float(max_price)
            if price_value < 0:
                flash(translate("flash.max_price_positive"), "warning")
            else:
                rooms_query = rooms_query.filter(Room.price <= price_value)
        except ValueError:
            flash(translate("flash.max_price_number"), "warning")

    data = rooms_query.all()
    all_rooms = Room.query.all()
    types = sorted(list({r.type for r in all_rooms}))
    return render_template("rooms.html", rooms=data, q=q, types=types, selected_type=room_type, max_price=max_price)


@app.route("/rooms/<int:room_id>")
def room_detail(room_id):
    room = Room.query.get_or_404(room_id)
    return render_template("room_detail.html", room=room)


# ─── Auth ───────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
@app.route("/signup", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        preferred_language = request.form.get("preferred_language", DEFAULT_LANGUAGE).strip()
        region = request.form.get("region", "US").strip()

        form_data = {
            "full_name": full_name,
            "email": email,
            "preferred_language": preferred_language if preferred_language in LANGUAGES else DEFAULT_LANGUAGE,
            "region": region if region in REGIONS else "US",
        }

        if not full_name or not email or not password or not confirm_password:
            flash(translate("flash.signup_required"), "danger")
            return render_template("register.html", form_data=form_data)

        if not EMAIL_RE.match(email):
            flash(translate("flash.email_invalid"), "danger")
            return render_template("register.html", form_data=form_data)

        if preferred_language not in LANGUAGES:
            flash(translate("flash.language_invalid"), "danger")
            return render_template("register.html", form_data=form_data)

        if not valid_password(password):
            flash(translate("flash.password_weak"), "danger")
            return render_template("register.html", form_data=form_data)

        if password != confirm_password:
            flash(translate("flash.password_mismatch"), "danger")
            return render_template("register.html", form_data=form_data)

        existing_user = User.query.filter((User.email == email) | (User.username == email)).first()
        if existing_user:
            flash(translate("flash.email_exists"), "danger")
            return render_template("register.html", form_data=form_data)

        new_user = User(
            username=email,
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),
            preferred_language=preferred_language,
            region=region,
        )
        db.session.add(new_user)
        db.session.commit()

        session["lang"] = preferred_language
        flash(translate("flash.account_created", lang=preferred_language), "success")
        return redirect(url_for("login"))

    return render_template("register.html", form_data={
        "preferred_language": session.get("lang", DEFAULT_LANGUAGE),
        "region": session.get("region", "US"),
    })


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter((User.username == username) | (User.email == username.lower())).first()
        if user and check_password_hash(user.password, password):
            session["logged_in"] = True
            session["user_id"] = user.id
            session["username"] = user.username
            session["display_name"] = user.full_name or user.username
            session["is_admin"] = user.is_admin

            # Load user preferences into session
            if user.preferred_language in LANGUAGES:
                session["lang"] = user.preferred_language
            session["region"] = user.region or "US"
            session["theme_mode"] = user.theme_mode or "system"

            flash(translate("flash.login_success"), "success")
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("home"))

        flash(translate("flash.login_failed"), "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash(translate("flash.logged_out"), "info")
    return redirect(url_for("home"))



# ─── Booking ────────────────────────────────────────────────────
@app.route("/booking", methods=["GET", "POST"])
@login_required
def booking():
    room_id = request.args.get("room_id", "").strip()
    selected_room = None
    if room_id.isdigit():
        selected_room = Room.query.get(int(room_id))

    if request.method == "POST":
        chosen_room_id = request.form.get("room_id", "").strip()
        check_in = request.form.get("check_in", "").strip()
        check_out = request.form.get("check_out", "").strip()
        guests = request.form.get("guests", "1").strip()

        if not chosen_room_id or not chosen_room_id.isdigit() or not check_in or not check_out:
            flash(translate("flash.booking_required"), "danger")
            return render_template("booking.html", rooms=Room.query.all(), selected_room=selected_room)

        room = Room.query.get(int(chosen_room_id))
        if not room:
            flash(translate("flash.room_not_found"), "danger")
            return render_template("booking.html", rooms=Room.query.all(), selected_room=selected_room)

        try:
            ci = datetime.strptime(check_in, "%Y-%m-%d").date()
            co = datetime.strptime(check_out, "%Y-%m-%d").date()
            today = datetime.now().date()
            if ci < today:
                flash(translate("flash.checkin_future"), "danger")
                return render_template("booking.html", rooms=Room.query.all(), selected_room=room)
            if co <= ci:
                flash(translate("flash.checkout_after_checkin"), "danger")
                return render_template("booking.html", rooms=Room.query.all(), selected_room=room)
        except ValueError:
            flash(translate("flash.invalid_date"), "danger")
            return render_template("booking.html", rooms=Room.query.all(), selected_room=room)

        try:
            guests_int = int(guests)
        except ValueError:
            guests_int = 0

        if guests_int < 1 or guests_int > room.capacity:
            flash(translate("flash.guests_range", capacity=room.capacity), "danger")
            return render_template("booking.html", rooms=Room.query.all(), selected_room=room)

        # Availability check (overlap)
        conflict = Reservation.query.filter(
            Reservation.room_id == room.id,
            Reservation.status == "Booked",
            Reservation.check_in < co,
            Reservation.check_out > ci
        ).first()

        if conflict:
            flash(translate("flash.room_conflict"), "danger")
            return render_template("booking.html", rooms=Room.query.all(), selected_room=room)

        reservation = Reservation(
            room_id=room.id,
            user_id=session["user_id"],
            check_in=ci,
            check_out=co,
            guests=guests_int,
            status="Booked"
        )
        db.session.add(reservation)
        db.session.commit()

        flash(translate("flash.reservation_created"), "success")
        return redirect(url_for("reservations"))

    return render_template("booking.html", rooms=Room.query.all(), selected_room=selected_room)


@app.route("/reservations")
@login_required
def reservations():
    q = request.args.get("q", "").strip().lower()
    status = request.args.get("status", "").strip()

    res_query = Reservation.query.filter_by(user_id=session["user_id"])

    if q:
        res_query = res_query.join(Room).filter(
            (Room.name.ilike(f'%{q}%')) | (Room.type.ilike(f'%{q}%'))
        )

    if status:
        res_query = res_query.filter(Reservation.status == status)

    items = res_query.all()
    return render_template("reservations.html", reservations=items, q=q, status=status)


@app.route("/reservations/<int:res_id>/cancel", methods=["POST"])
@login_required
def cancel_reservation(res_id):
    res = Reservation.query.filter_by(id=res_id, user_id=session["user_id"]).first()
    if not res:
        flash(translate("flash.reservation_not_found"), "warning")
    elif res.status == "Cancelled":
        flash(translate("flash.reservation_already_cancelled"), "info")
    else:
        res.status = "Cancelled"
        db.session.commit()
        flash(translate("flash.reservation_cancelled"), "info")
    return redirect(url_for("reservations"))


# ─── Dashboard (Admin Only) ────────────────────────────────────
@app.route("/dashboard")
@admin_required
def dashboard():
    all_res = Reservation.query.all()
    total_res = len(all_res)
    booked = len([r for r in all_res if r.status == "Booked"])
    cancelled = len([r for r in all_res if r.status == "Cancelled"])
    total_rooms = Room.query.count()
    latest_test, test_history = load_test_results()
    
    recent = Reservation.query.order_by(Reservation.id.desc()).limit(6).all()
    return render_template(
        "dashboard.html",
        total_rooms=total_rooms,
        total_res=total_res,
        booked=booked,
        cancelled=cancelled,
        recent=recent,
        latest_test=latest_test,
        test_history=test_history
    )


# ─── Test Reset (Dev Only) ─────────────────────────────────────
@app.route("/test/reset")
def test_reset():
    if not app.debug and not app.config.get("TESTING"):
        abort(404)
    Reservation.query.delete()
    try:
        db.session.execute(db.text("DELETE FROM sqlite_sequence WHERE name='reservation'"))
    except Exception:
        db.session.rollback()
        Reservation.query.delete()
    db.session.commit()
    session.clear()
    return "OK", 200



if __name__ == "__main__":
    app.run(debug=True)
