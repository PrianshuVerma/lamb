import os
import re
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()


USERNAME = "prianshu@alleviatehealth.care"
PASSWORD = "testalleviate123"

LOGIN_URL = "https://platform.alleviatehealth.care"
HEADLESS = False
IMPLICIT_WAIT = 5
EXPLICIT_WAIT = 15


def validate_10_digit_phone(s: str) -> str:
    """Return a clean 10-digit string or raise ValueError."""
    digits = re.sub(r"\D", "", str(s))
    if len(digits) != 10:
        raise ValueError(
            f"Phone must be exactly 10 digits after cleaning; got {len(digits)} digits ({digits})."
        )
    return digits


def create_driver(headless: bool = False):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1366,900") 
        options.add_argument("--force-device-scale-factor=1")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver


def enter_number(num, driver):
    """Assumes we are already on the Settings page."""
    wait = WebDriverWait(driver, EXPLICIT_WAIT)

    phone_input = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='tel']"))
    )
    phone_input.clear()
    phone_input.send_keys(num)

    save_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Save changes']")
        )
    )
    save_btn.click()

    # Confirm value was entered
    try:
        WebDriverWait(driver, 8).until(
            lambda d: phone_input.get_attribute("value") == num
        )
    except TimeoutException:
        pass

    print("Saved phone:", phone_input.get_attribute("value"))
    return True


def login(driver):
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, EXPLICIT_WAIT)

    try:
        username_el = wait.until(EC.visibility_of_element_located((By.ID, "email")))
        password_el = driver.find_element(By.ID, "password")
    except TimeoutException:
        print("Login fields not found — you may need to change selectors.")
        raise

    username_el.clear()
    username_el.send_keys(USERNAME)
    password_el.clear()
    password_el.send_keys(PASSWORD)

    submit_el = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_el.click()

    wait.until(EC.url_contains("/trials"))
    print("Login successful, now on trials page:", driver.current_url)

    # Go to settings
    settings_link = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/settings']"))
    )
    settings_link.click()
    wait.until(EC.url_contains("/settings"))
    print("On settings page")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phone", help="10-digit phone number (any format, will be cleaned)")
    args = parser.parse_args()

    phone_input_value = os.getenv("PHONE") or args.phone or input("Enter phone number (10 digits, any format): ").strip()

    # Validate before launching browser
    try:
        phone_clean = validate_10_digit_phone(phone_input_value)
    except ValueError as e:
        print("Invalid phone number:", e)
        return  # quit script immediately

    driver = create_driver(HEADLESS)
    driver.maximize_window()
    try:
        if login(driver):
            enter_number(phone_clean, driver)
    finally:
        if not HEADLESS:
            print("Leaving browser open for 10s for inspection...")
            time.sleep(10)
        driver.quit()


if __name__ == "__main__":
    main()
