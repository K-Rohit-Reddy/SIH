from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Function to log in using Twitter authentication
def signin_twitter_auth(driver, username, password):
    try:
        # Navigate to Twitter login page
        driver.get("https://x.com/i/flow/login")
        
        # Wait until the username field is present and visible
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']"))
        )
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)

        # Wait for a few seconds to ensure the next page loads
        time.sleep(3)

        # Wait until the password field is visible and present
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='current-password']"))
        )
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        # Wait for login to complete
        time.sleep(3)

        print("Logged in using Twitter authentication.")
    except Exception as e:
        print(f"An error occurred during login: {str(e)}")

# Set up paths and ChromeDriver
driver = webdriver.Chrome()
driver.maximize_window()

# Your Twitter credentials
u_name = "Lorven197843"  # Enter your username here
passw = "Test@123"       # Enter your password here

# Call the login function
signin_twitter_auth(driver, u_name, passw)

# Wait for 10 seconds after login
time.sleep(10)

# Go to the profile page after logging in
profile_url = f"https://x.com/{u_name}"
driver.get(profile_url)

# Wait for profile page to load by checking for a key element (increase timeout to 20 seconds)
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="primaryColumn"]'))
    )
    print("Profile page has fully loaded.")
except Exception as e:
    print(f"Error waiting for the profile page to load: {e}")
    driver.quit()

# Scroll down the page to load more tweets (increase number of scrolls if necessary)
n_scrolls = 3  # Increase scrolls to ensure tweets load
for _ in range(n_scrolls):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Increase sleep time for slower loading pages

# Wait for tweets to be present (increase timeout)
try:
    tweets_section = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Timeline: Lorven\'s posts"]'))
    )
except Exception as e:
    print(f"Error: Tweets section not found. {e}")
    driver.quit()

tweets = tweets_section.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')

# Store tweet links
tweet_links = []
for tweet in tweets:
    try:
        link = tweet.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]').get_attribute('href')
        if link and link not in tweet_links:
            tweet_links.append(link)
    except Exception as e:
        print(f"Error retrieving link from tweet: {e}")
        continue

print(f"Found {len(tweet_links)} tweets.")

# Set up directory for screenshots
path = os.path.join(os.getcwd(), "Tweets_" + u_name)
os.makedirs(path, exist_ok=True)

# Create PDF document
pdf_filename = "tweets_" + u_name + ".pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4
margin = 30

c.setFont("Times-Roman", 36)
c.drawCentredString(width / 2, height - 100, "TWEETS")
c.setFont("Times-Roman", 32)
c.drawCentredString(width / 2, height - 140, f"{u_name}")
c.showPage()

# Function to scale images for PDF
def scale_image(img, max_width, max_height):
    img_width, img_height = img.size
    aspect_ratio = img_height / img_width

    if img_width > max_width:
        img_width = max_width
        img_height = img_width * aspect_ratio

    if img_height > max_height:
        img_height = max_height
        img_width = img_height / aspect_ratio

    return img_width, img_height

# Capture each tweet and save to PDF
for counter, tweet_link in enumerate(tweet_links, start=1):
    try:
        driver.get(tweet_link)
        time.sleep(3)

        # Take a screenshot of the tweet
        screenshot_path = os.path.join(path, f"tweet_{counter}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved for tweet {counter}.")

        # Add screenshot to PDF
        img = Image.open(screenshot_path)
        img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
        x = (width - img_pdf_width) / 2
        y = (height - img_pdf_height) / 2
        c.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
        c.showPage()

    except Exception as e:
        print(f"Error processing tweet {counter}: {e}")
        continue

# Save PDF and quit browser
c.save()
driver.quit()
