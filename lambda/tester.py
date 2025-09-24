import os, time, json, traceback
from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import re



USERNAME = "prianshu@alleviatehealth.care"
PASSWORD = "testalleviate123"
LOGIN_URL = "https://platform.alleviatehealth.care"
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 22


def enter_number(num, driver):

    wait = WebDriverWait(driver, EXPLICIT_WAIT)
    phone_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='tel']")))
    phone_input.click()
    phone_input.send_keys(Keys.CONTROL + "a")
    phone_input.send_keys(Keys.DELETE)
    phone_input.send_keys(num)
    driver.execute_script("""
      const el = arguments[0];
      el.dispatchEvent(new Event('input',  {bubbles:true}));
      el.dispatchEvent(new Event('change', {bubbles:true}));
    """, phone_input)
    phone_input.send_keys(Keys.TAB)
    save_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[normalize-space()='Save changes']")
    ))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
    save_btn.click()
    wait = WebDriverWait(driver, EXPLICIT_WAIT)
    print(f"Saved phone: {num}")

    try:
        
        logout_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[normalize-space()='Sign out'] | //a[normalize-space()='Sign out']"
        )))
        logout_btn.click()
        print("Clicked Sign out.")
        return True
    except Exception as e:
        print(f"Could not sign out: {e}")
        return False


def login(driver):
    w = WebDriverWait(driver, EXPLICIT_WAIT)

    # Login
    driver.get(LOGIN_URL)
    w.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # past the login page 
    w.until(EC.any_of(
        EC.url_contains("/trials"),
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='app-shell']")),
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-page='dashboard']"))
    ))
    print("Login successful.")

    # Go  settings 
    driver.get(f"{LOGIN_URL}/settings")

    # wait for settings to load
    try:
        w.until(EC.any_of(
            EC.url_contains("/settings"),
        ))
        print("On settings page.")
        return True
    except TimeoutException:
        # Fallback: some UIs hide Settings 
        try:
            
            menu = w.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/settings']")))
            menu.click()
            w.until(EC.url_contains("/settings"))
            print("On settings page via menu.")
            return True
        except Exception as e:
            print(f"Settings nav failed: {e}")
            raise

def _find_chrome_binary():
    #  else system installs
    for p in (
        "/opt/chrome/chrome-linux64/chrome",
        "/opt/chrome/chrome",                       
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ):
        if os.path.exists(p):
            return p
    return None

def _find_chromedriver():
    for p in (
        "/opt/chrome-driver/chromedriver-linux64/chromedriver",
        "/opt/chromedriver/chromedriver",
        "/usr/bin/chromedriver",
    ):
        if os.path.exists(p):
            return p
    return None

def lambda_handler(event, context):
    try:
        print("EVENT:", json.dumps(event))  # helpful in CloudWatch

        phone = (event.get("pathParameters") or {}).get("phone")

        # Function URL
        if not phone:
            phone = (event.get("queryStringParameters") or {}).get("phone")

        if not phone:
            return {"statusCode": 400, "body": "Provide phone via ?phone=123... or /phone/{phone}"}

        # Normalize
        normalized = re.sub(r"\D", "", phone)

        # Validate: must be exactly 10 digits
        if not (normalized.isdigit() and len(normalized) == 10):
            return {
                "statusCode": 400,
                "body": f"Invalid phone number: {phone}. Must be exactly 10 digits."
            }

        phone = normalized

        chrome_binary = _find_chrome_binary()
        driver_binary = _find_chromedriver()
        if not chrome_binary or not driver_binary:
            raise RuntimeError(f"Chrome/Driver not found. chrome={chrome_binary}, driver={driver_binary}")

        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--window-size=1366,900") 
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
        chrome_options.add_argument(f"--data-path={mkdtemp()}")
        chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        chrome_options.add_argument("--remote-debugging-pipe")
        chrome_options.binary_location = chrome_binary

        service = Service(executable_path=driver_binary, service_log_path="/tmp/chromedriver.log")

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(IMPLICIT_WAIT)
        try:
            login(driver)
            enter_number(phone, driver)

        finally:
            driver.quit()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "Successfully updated phone number"
        }

    except Exception as e:
        err = traceback.format_exc()
        print("ERROR:", err)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
