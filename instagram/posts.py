from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

service = Service("C:/Users/katik/Desktop/insta-to-pdf/py/chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.get("http://www.instagram.com")

time.sleep(6)

username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
u_name = "amma_500026"
passw = "Test123@"

username.clear()
password.clear()
username.send_keys(u_name)
password.send_keys(passw)

time.sleep(2)

login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
login_button.click()


time.sleep(8)

profile_url = "https://www.instagram.com/" + u_name + "/"
driver.get(profile_url)

time.sleep(6)

n_scrolls = 2
for _ in range(n_scrolls):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

time.sleep(4)

post_links = []
div_elements = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.x1lliihq.x1n2onr6.xh8yej3.x4gyw5p.xfllauq.xo2y696.x11i5rnm.x2pgyrj'))
)

for div in div_elements:
    a_tags = div.find_elements(By.TAG_NAME, 'a')
    for a in a_tags:
        href = a.get_attribute('href')
        if href and 'instagram.com/p/' in href and href not in post_links:
            post_links.append(href)

print(f'Found {len(post_links)} posts.')

path = os.path.join(os.getcwd(), "Posts_" + u_name)
os.makedirs(path, exist_ok=True)

pdf_filename = "posts_" + u_name + ".pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4
margin = 30

c.setFont("Times-Roman", 36)
c.drawCentredString(width / 2, height - 100, "POSTS")
text_width = c.stringWidth("POSTS", "Times-Roman", 36)
underline_x_start = (width - text_width) / 2
underline_y = height - 105
c.setLineWidth(1)
c.line(underline_x_start, underline_y, underline_x_start + text_width, underline_y)
c.line(underline_x_start, underline_y - 3, underline_x_start + text_width, underline_y - 3)
c.setFont("Times-Roman", 32)
c.drawCentredString(width / 2, height - 140, f"{u_name}")
c.showPage()

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

for counter, post_link in enumerate(post_links, start=1):
    try:
        driver.get(post_link)
        time.sleep(3)

        screenshot_path = os.path.join(path, f"post_{counter}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved for post {counter}.")

        img = Image.open(screenshot_path)
        img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
        x = (width - img_pdf_width) / 2
        y = (height - img_pdf_height) / 2
        c.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
        c.showPage()

        while True:
            try:
                next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Next"]')))
                next_button.click()
                time.sleep(2)

                screenshot_path = os.path.join(path, f"post_{counter}_next.png")
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved for post {counter} (next).")

                img = Image.open(screenshot_path)
                img_pdf_width, img_pdf_height = scale_image(img, width - 2 * margin, height - 2 * margin)
                c.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
                c.showPage()

            except Exception:
                break

    except Exception as e:
        print(f"Error processing post {counter}: {e}")
        continue

c.save()
driver.quit()

