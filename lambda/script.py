import os, re, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Your credentials and constants
USERNAME = "prianshu@alleviatehealth.care"
PASSWORD = "testalleviate123"
LOGIN_URL = "https://platform.alleviatehealth.care"
IMPLICIT_WAIT = 5
EXPLICIT_WAIT = 15

def create_driver():
    options = webdriver.ChromeOptions()
    options.binary_location = "/opt/chrome/chrome"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-data-dir=/tmp/user-data")
    options.add_argument("--data-path=/tmp/data-path")
    options.add_argument("--disk-cache-dir=/tmp/cache-dir")
    service = ChromeService(executable_path="/opt/chromedriver")
    return webdriver.Chrome(service=service, options=options)

def validate_10_digit_phone(s: str) -> str:
    digits = re.sub(r"\D", "", str(s))
    if len(digits) != 10:
        raise ValueError(f"Phone must be 10 digits; got {len(digits)}.")
    return digits

def login(driver):
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, EXPLICIT_WAIT)
    wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    wait.until(EC.url_contains("/trials"))
    print("Login successful.")
    driver.find_element(By.CSS_SELECTOR, "a[href='/settings']").click()
    wait.until(EC.url_contains("/settings"))
    print("On settings page.")
    return True

def enter_number(num, driver):
    wait = WebDriverWait(driver, EXPLICIT_WAIT)
    phone_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='tel']")))
    phone_input.clear()
    phone_input.send_keys(num)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Save changes']"))).click()
    print(f"✓ Saved phone: {num}")
    return True

def lambda_handler(event, context):
    print(f"Received event: {event}")
    try:
        phone_input_value = event['pathParameters']['phone']
    except (KeyError, TypeError):
        return {"statusCode": 400, "body": json.dumps({"message": "Could not find 'phone' parameter in the URL path."})}

    try:
        phone_clean = validate_10_digit_phone(phone_input_value)
    except ValueError as e:
        return {"statusCode": 400, "body": json.dumps({"message": str(e)})}

    driver = create_driver()
    try:
        if login(driver):
            enter_number(phone_clean, driver)
            return {"statusCode": 200, "body": json.dumps({"message": f"Successfully updated phone to {phone_clean}"})}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"statusCode": 500, "body": json.dumps({"message": f"An error occurred: {str(e)}"}) }
    finally:
        driver.quit()