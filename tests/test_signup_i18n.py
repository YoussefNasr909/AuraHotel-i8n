import time

from app import app


def test_signup_validation_rejects_weak_password():
    client = app.test_client()

    response = client.post(
        "/signup",
        data={
            "full_name": "Test User",
            "email": f"weak{int(time.time())}@example.com",
            "password": "short",
            "confirm_password": "short",
            "preferred_language": "en",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Password must be at least 8 characters" in response.data


def test_language_selector_sets_arabic_rtl():
    client = app.test_client()

    response = client.get("/?lang=ar")

    assert response.status_code == 200
    assert b'lang="ar"' in response.data
    assert b'dir="rtl"' in response.data


def test_openssl_health_endpoint_exposes_status():
    client = app.test_client()

    response = client.get("/health/openssl")
    data = response.get_json()

    assert response.status_code == 200
    assert "available" in data
    assert "version" in data
    assert "https_enabled" in data
