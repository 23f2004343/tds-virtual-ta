from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from bs4 import BeautifulSoup

# ========== CONFIGURATION ==========
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
LOGIN_URL = f"{BASE_URL}/login"
CATEGORY_URL = f"{BASE_URL}/c/courses/tds-kb/34"
# ===================================

def selenium_login_and_get_cookies(username, password):
    print("🔐 Starting headless browser for login...")

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(LOGIN_URL)

    time.sleep(3)  # Wait for page to load

    # Click login button to show login form
    try:
        login_button = driver.find_element(By.CSS_SELECTOR, "button.login-button")
        login_button.click()
        time.sleep(2)
    except:
        pass  # On some setups, form may already be shown

    # Fill in login form
    email_input = driver.find_element(By.ID, "login-account-name")
    password_input = driver.find_element(By.ID, "login-password")
    email_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

    time.sleep(5)  # Wait for login to process

    if "login" in driver.current_url:
        print("❌ Login failed. Check your credentials.")
        driver.quit()
        exit()

    print("✅ Login successful!")

    # Get cookies from browser
    cookies = driver.get_cookies()
    driver.quit()

    # Convert to requests-compatible cookies
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    return session

def fetch_category_topics(session):
    print("📥 Fetching category topics...")

    resp = session.get(f"{CATEGORY_URL}.json")
    if resp.status_code != 200:
        print("Failed to fetch category page.")
        return []

    data = resp.json()
    topics = data.get("topic_list", {}).get("topics", [])
    return topics

def main():
    print("Discourse Scraper via Selenium")
    print("=" * 40)

    username = input("Enter your Discourse username/email: ")
    password = input("Enter your password (input will be visible): ")

    session = selenium_login_and_get_cookies(username, password)

    topics = fetch_category_topics(session)
    print(f"\n✅ Found {len(topics)} topics in the category.\n")
    for t in topics[:10]:  # Show a few
        print(f"{t['id']}: {t['title']}")

if __name__ == "__main__":
    main()
