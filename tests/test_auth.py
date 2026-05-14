from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def reset_session(driver, base_url):
    driver.get(base_url + "/test/reset")


def login(driver, base_url, username, password):
    driver.get(base_url + "/login")
    driver.find_element(By.CSS_SELECTOR, '[data-test="login-username"]').send_keys(username)
    driver.find_element(By.CSS_SELECTOR, '[data-test="login-password"]').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, '[data-test="login-submit"]').click()


def test_login_success(driver, base_url):
    reset_session(driver, base_url)
    login(driver, base_url, "admin", "1234")

    # expect a success flash
    flash = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="flash"]'))
    )
    assert "Login successful" in flash.text


def test_login_failure(driver, base_url):
    reset_session(driver, base_url)
    login(driver, base_url, "admin", "wrong")

    flash = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="flash"]'))
    )
    assert "Wrong username or password" in flash.text


def test_protected_page_redirects_to_login(driver, base_url):
    reset_session(driver, base_url)
    driver.get(base_url + "/booking")

    # should redirect to login
    WebDriverWait(driver, 5).until(EC.url_contains("/login"))
    assert "/login" in driver.current_url
