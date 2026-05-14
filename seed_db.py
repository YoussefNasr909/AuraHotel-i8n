from app import app, REGIONS
from models import db, User, Room

ROOMS_DATA = [
    {
        "id": 1,
        "name": "Cairo Comfort Single",
        "type": "Single",
        "price": 55,
        "capacity": 1,
        "amenities": ["Wi-Fi", "AC", "Breakfast", "Desk"],
        "image": "https://images.unsplash.com/photo-1568495248636-6432b97bd949?q=80&w=1074&auto=format&fit=crop",
        "desc": "room.desc.cairo_comfort"
    },
    {
        "id": 2,
        "name": "Nile View Double",
        "type": "Double",
        "price": 85,
        "capacity": 2,
        "amenities": ["Wi-Fi", "AC", "Balcony", "Breakfast"],
        "image": "https://images.unsplash.com/photo-1505692952047-1a78307da8f2?q=80&w=1200&auto=format&fit=crop",
        "desc": "room.desc.nile_view"
    },
    {
        "id": 3,
        "name": "Lux Suite",
        "type": "Suite",
        "price": 160,
        "capacity": 4,
        "amenities": ["Wi-Fi", "AC", "Jacuzzi", "Living Area", "Breakfast"],
        "image": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?q=80&w=1200&auto=format&fit=crop",
        "desc": "room.desc.lux_suite"
    },
    {
        "id": 4,
        "name": "Red Sea Royal Suite",
        "type": "Suite",
        "price": 250,
        "capacity": 2,
        "amenities": ["Sea View", "Private Balcony", "Jacuzzi", "Champagne Service"],
        "image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?q=80&w=1074&auto=format&fit=crop",
        "desc": "room.desc.red_sea_royal"
    },
    {
        "id": 5,
        "name": "Aswan Ancient Twin",
        "type": "Double",
        "price": 95,
        "capacity": 2,
        "amenities": ["Wi-Fi", "AC", "Themed Decor", "City View"],
        "image": "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?q=80&w=1170&auto=format&fit=crop",
        "desc": "room.desc.aswan_ancient"
    },
    {
        "id": 6,
        "name": "Modern Minimalist Loft",
        "type": "Suite",
        "price": 180,
        "capacity": 2,
        "amenities": ["Smart Home", "Projector", "Mini Bar", "City Skyline"],
        "image": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?q=80&w=1171&auto=format&fit=crop",
        "desc": "room.desc.modern_minimalist"
    },
    {
        "id": 7,
        "name": "Family Penthouse",
        "type": "Suite",
        "price": 320,
        "capacity": 6,
        "amenities": ["3 Bedrooms", "Kitchen", "Large Terrace", "Family Games"],
        "image": "https://images.unsplash.com/photo-1591088398332-8a7791972843?q=80&w=1074&auto=format&fit=crop",
        "desc": "room.desc.family_penthouse"
    }
]

from werkzeug.security import generate_password_hash

# ... (rest of code) ...

def seed():
    with app.app_context():
        db.create_all()
        
        # Seed User
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin", 
                full_name="AURA Admin",
                email="admin@aura.example",
                password=generate_password_hash("1234"),
                preferred_language="en",
                is_admin=True,
                region="US",
                currency="USD",
                unit_system="imperial",
                temperature_unit="fahrenheit",
                time_format="12h",
                color_theme="global"
            )
            db.session.add(admin)

        for region_code, region_data in REGIONS.items():
            username = f"user_{region_code.lower()}"
            if not User.query.filter_by(username=username).first():
                lang = "en"
                if region_code in ["EG", "SA", "AE"]: lang = "ar"
                elif region_code == "CN": lang = "zh"
                elif region_code == "ES": lang = "es"
                elif region_code == "IN": lang = "hi"

                new_user = User(
                    username=username,
                    full_name=f"{region_data['name']} User",
                    email=f"{region_code.lower()}@aura.example",
                    password=generate_password_hash("1234"),
                    preferred_language=lang,
                    is_admin=False,
                    region=region_code,
                    currency=region_data["currency"],
                    unit_system=region_data["unitSystem"],
                    temperature_unit=region_data["tempUnit"],
                    time_format=region_data["timeFormat"],
                    color_theme=region_data["theme"]
                )
                db.session.add(new_user)
        
        # Seed Rooms
        for r_data in ROOMS_DATA:
            if not Room.query.get(r_data["id"]):
                room = Room(
                    id=r_data["id"],
                    name=r_data["name"],
                    type=r_data["type"],
                    price=r_data["price"],
                    capacity=r_data["capacity"],
                    image=r_data["image"],
                    desc=r_data["desc"]
                )
                room.amenities = r_data["amenities"]
                db.session.add(room)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed()
