from datetime import date, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def set_date_js(driver, css_selector, value):
    driver.execute_script(
        "document.querySelector(arguments[0]).value = arguments[1];"
        "document.querySelector(arguments[0]).dispatchEvent(new Event('input', {bubbles:true}));"
        "document.querySelector(arguments[0]).dispatchEvent(new Event('change', {bubbles:true}));",
        css_selector, value
    )


def reset_session(driver, base_url):
    driver.get(base_url + "/test/reset")


def login(driver, base_url):
    driver.get(base_url + "/login")
    driver.find_element(By.CSS_SELECTOR, '[data-test="login-username"]').send_keys("admin")
    driver.find_element(By.CSS_SELECTOR, '[data-test="login-password"]').send_keys("1234")
    driver.find_element(By.CSS_SELECTOR, '[data-test="login-submit"]').click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="nav-logout"]'))
    )


def test_create_booking_then_cancel(driver, base_url):
    reset_session(driver, base_url)
    login(driver, base_url)

    driver.get(base_url + "/booking")

    room_select = Select(driver.find_element(By.CSS_SELECTOR, '[data-test="booking-room"]'))
    room_select.select_by_value("1")

    ci = date.today() + timedelta(days=2)
    co = date.today() + timedelta(days=4)

    # IMPORTANT: set date fields using JS (more reliable than send_keys on type=date)
    set_date_js(driver, '[data-test="booking-checkin"]', ci.isoformat())
    set_date_js(driver, '[data-test="booking-checkout"]', co.isoformat())

    guests = driver.find_element(By.CSS_SELECTOR, '[data-test="booking-guests"]')
    guests.clear()
    guests.send_keys("1")

    driver.find_element(By.CSS_SELECTOR, '[data-test="booking-submit"]').click()

    WebDriverWait(driver, 5).until(EC.url_contains("/reservations"))

    table = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="res-table"]'))
    )
    assert "Cairo Comfort Single" in table.text
    assert "Booked" in table.text

    cancel_btn = driver.find_element(By.CSS_SELECTOR, '[data-test^="res-cancel-"]')
    cancel_btn.click()

    # IMPORTANT: accept confirm popup
    WebDriverWait(driver, 5).until(EC.alert_is_present())
    driver.switch_to.alert.accept()

    # Wait for the page to reload after cancel action
    import time
    time.sleep(1)  # Allow page to fully reload after form submission

    # verify status changed after cancel - re-locate the element fresh
    table2 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="res-table"]'))
    )
    # Use driver.page_source as a fallback to avoid stale element issues
    assert "Cancelled" in driver.page_source


def test_booking_validation_checkout_before_checkin(driver, base_url):
    reset_session(driver, base_url)
    login(driver, base_url)

    driver.get(base_url + "/booking")

    room_select = Select(driver.find_element(By.CSS_SELECTOR, '[data-test="booking-room"]'))
    room_select.select_by_value("2")

    ci = date.today() + timedelta(days=5)
    co = date.today() + timedelta(days=4)

    # set invalid dates reliably
    set_date_js(driver, '[data-test="booking-checkin"]', ci.isoformat())
    set_date_js(driver, '[data-test="booking-checkout"]', co.isoformat())

    driver.find_element(By.CSS_SELECTOR, '[data-test="booking-submit"]').click()

    flash = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="flash"]'))
    )
    assert "Check-out must be after check-in" in flash.text


def test_booking_validation_guests_exceed_capacity(driver, base_url):
    reset_session(driver, base_url)
    login(driver, base_url)

    driver.get(base_url + "/booking")

    room_select = Select(driver.find_element(By.CSS_SELECTOR, '[data-test="booking-room"]'))
    room_select.select_by_value("1")

    ci = date.today() + timedelta(days=2)
    co = date.today() + timedelta(days=3)

    set_date_js(driver, '[data-test="booking-checkin"]', ci.isoformat())
    set_date_js(driver, '[data-test="booking-checkout"]', co.isoformat())

    guests = driver.find_element(By.CSS_SELECTOR, '[data-test="booking-guests"]')
    guests.clear()
    guests.send_keys("2")  # exceeds capacity (room 1 capacity is 1)

    driver.find_element(By.CSS_SELECTOR, '[data-test="booking-submit"]').click()

    flash = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="flash"]'))
    )
    assert "Guests must be between 1 and 1" in flash.text
