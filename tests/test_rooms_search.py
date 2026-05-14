from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_rooms_search_suite_found(driver, base_url):
    driver.get(base_url + "/rooms?q=suite")

    # expect Lux Suite card text somewhere on page
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    assert "Lux Suite" in driver.page_source


def test_rooms_search_no_results(driver, base_url):
    driver.get(base_url + "/rooms?q=zzzzzzzzzz")

    empty = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="rooms-empty"]'))
    )
    assert "No rooms found" in empty.text
