import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


GYM_URL = "https://appbrewery.github.io/gym/"

ACCOUNT_EMAIL = "agnieszka@test.com"
ACCOUNT_PASSWORD = "PasswordGym123;"

CLASS_DAY = (1,3) # (Tuesday)
CLASS_HOUR = 18

MSG_DICTIONARY = {
    "Join Waitlist": "Joined waitlist for",
    "Book Class": "Booked",
    "Booked": "Already booked",
    "Waitlisted": "Already on waitlist"
}

new_bookings = 0
waitlist_joined = 0
booked_waitlisted = 0

class_list = []

def book_class(booking_button, text_to_wait_for):
    booking_button.click()
    # Wait for button state to change - will time out if booking failed
    wait.until(lambda x: booking_button.text == text_to_wait_for)

def retry(func, retries=7, description=None):
    for i in range(retries):
        print(f"Trying {description}. Attempt: {i + 1}")
        try:
            return func()
        except TimeoutException:
            if i == retries - 1:
                raise
            time.sleep(1)

def login():
    # Localise log in button and click it
    login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-button")))
    login_button.click()
    # Find email and password fields
    email_input = wait.until(EC.presence_of_element_located((By.ID, "email-input")))
    password_input = driver.find_element(By.NAME, value="password")
    # Insert credentials
    email_input.clear()
    email_input.send_keys(ACCOUNT_EMAIL)
    password_input.clear()
    password_input.send_keys(ACCOUNT_PASSWORD)
    # Localise and click submit button
    submit_button = driver.find_element(By.ID, value="submit-button")
    submit_button.click()
    # Check if page is correctly displayed
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#schedule-page > h1")))
    # is_class_schedule_visible = driver.find_element(By.ID, value="schedule-page")


# Configure Selenium to stay open using Chrome option
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

# Create directory to store Chrome Profile
user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
# Pass directory as an argument to keep all preferences and settings from profile
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

driver = webdriver.Chrome(options=chrome_options)
driver.get(GYM_URL)
driver.maximize_window()

# ----------------  Step 2 - Automated Login ----------------

wait = WebDriverWait(driver, timeout=5, ignored_exceptions=[NoSuchElementException])

retry(login, description="login")

# ----------------  Step 3 - Class Booking: Book Upcoming Tuesday Class  ----------------

available_classes = driver.find_elements(By.CSS_SELECTOR, value='div[id^="class-card"]')

for cls in available_classes:
    class_date = ''.join(cls.get_attribute("id").split("-")[3:-1])
    hour = cls.get_attribute("id").split("-")[-1]
    class_date = ' '.join((class_date, hour))
    class_date = datetime.fromisoformat(class_date)

    if class_date.weekday() in CLASS_DAY and class_date.hour == CLASS_HOUR:
        # print("Found it!")
        # print(date, hour)
        class_name = cls.find_element(By.TAG_NAME, value="h3").text
        button = cls.find_element(By.TAG_NAME, value="button")

# ----------------  Step 4 - Class Booking: Checking if a class is already booked ----------------

        print_text = MSG_DICTIONARY[button.text]
        if button.text == "Join Waitlist":
            retry(lambda: book_class(button, "Waitlisted"), description="waitlisting")
            waitlist_joined+=1
            class_list.append(f"[New Waitlist] {class_name} on {class_date.strftime("%a, %b %d")}")
        elif button.text == "Book Class":
            retry(lambda: book_class(button, "Booked"), description="booking")
            new_bookings+=1
            class_list.append(f"[New Booking] {class_name} on {class_date.strftime("%a, %b %d")}")
        else:
            booked_waitlisted+=1

        print(f"✓ {print_text}: {class_name} on {class_date.strftime("%a, %b %d")}")

# ----------------  Step 5 - Class Booking: Add Statistics ----------------

# summary_message = (f"\n--- BOOKING SUMMARY ---\n"
#                    f"Classes booked: {new_bookings}\n"
#                    f"Waitlists joined: {waitlist_joined}\n"
#                    f"Already booked/waitlisted: {booked_waitlisted}\n"
#                    f"Total Tuesday & Thursday 6pm classes processed: {new_bookings+waitlist_joined+booked_waitlisted}")
# print(summary_message)



# ----------------  Step 6 - Class Booking: Add Detailed Statistics ----------------
# print("\n--- DETAILED CLASS LIST ---")
# for element in class_list:
#     print(f"  • {element}")

print(f"\n--- Total Tuesday/Thursday 6pm classes: {new_bookings+waitlist_joined+booked_waitlisted} ---")


print("\n--- VERIFYING ON MY BOOKINGS PAGE ---")
bookings_button = driver.find_element(By.ID, value="my-bookings-link")
bookings_button.click()

wait.until(EC.presence_of_element_located((By.ID, "my-bookings-page")))

bookings = driver.find_elements(By.CSS_SELECTOR, "div[id*='card-']")
booking_verification = 0

for card in bookings:
    try:
        when_paragraph = card.find_element(By.XPATH, ".//p[strong[text()='When:']]")
        when_text = when_paragraph.text

        if ("Tue" in when_text or "Thu" in when_text) and "6:00 PM" in when_text:
            card_name = card.find_element(By.TAG_NAME, "h3")
            print(f"  ✓ Verified: {card_name.text}")
            booking_verification+=1
    except NoSuchElementException:
        pass

print("\n--- VERIFICATION RESULT ---")
print(f"Expected: {new_bookings+waitlist_joined+booked_waitlisted}")
print(f"Found: {booking_verification}")
if booking_verification == (new_bookings+waitlist_joined+booked_waitlisted):
    print("✅ SUCCESS: All bookings verified!")
else:
    missing_booking = booking_verification - (new_bookings+waitlist_joined+booked_waitlisted)
    print(f"❌ MISMATCH: Missing {missing_booking} bookings")
