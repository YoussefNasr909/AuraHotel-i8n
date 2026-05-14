from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(160))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False)
    preferred_language = db.Column(db.String(8), default="en")
    is_admin = db.Column(db.Boolean, default=False)

    # Region-aware preferences
    region = db.Column(db.String(8), default="US")
    currency = db.Column(db.String(8), default="USD")
    unit_system = db.Column(db.String(10), default="metric")       # metric | imperial
    temperature_unit = db.Column(db.String(12), default="celsius")  # celsius | fahrenheit
    time_format = db.Column(db.String(4), default="12h")            # 12h | 24h
    theme_mode = db.Column(db.String(8), default="system")          # light | dark | system
    color_theme = db.Column(db.String(16), default="global")        # global | middleEast | eastAsia | europe | southAsia

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500))
    desc = db.Column(db.Text)
    _amenities = db.Column(db.String(500), name="amenities") # Stored as JSON string

    @property
    def amenities(self):
        if self._amenities:
            return json.loads(self._amenities)
        return []

    @amenities.setter
    def amenities(self, value):
        self._amenities = json.dumps(value)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Booked")

    room = db.relationship('Room', backref=db.backref('reservations', lazy=True))
    user = db.relationship('User', backref=db.backref('reservations', lazy=True))
