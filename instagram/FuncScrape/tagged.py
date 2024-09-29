from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from FuncScrape.pdf_utils import create_title_page
from FuncScrape.pdf_utils import scale_image
def fetch_tagged_posts(driver, pdf_report, u_name):
    """Fetches tagged posts of a user and adds them to the PDF report."""
    tagged_posts_url = f"https://www.instagram.com/{u_name}/tagged/"
    driver.get(tagged_posts_url)
    time.sleep(6)

    # Scroll the page to load more posts
    n_scrolls = 2
    for _ in range(n_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    time.sleep(4)

    # Find and collect post links
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

    print(f'Found {len(post_links)} tagged posts.')

    # Prepare folder for saving screenshots
    path = os.path.join("./instagram/Data", f"Data_{u_name}", "Tagged_Posts")
    os.makedirs(path, exist_ok=True)

    # Create title page
    create_title_page(pdf_report, "TAGGED POSTS")

    # Iterate over each post link and take screenshots
    for counter, post_link in enumerate(post_links, start=1):
        try:
            driver.get(post_link)
            time.sleep(3)

            # Save screenshot
            screenshot_path = os.path.join(path, f"post_{counter}.png")
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved for tagged post {counter}.")

            # Open the image and scale it to fit the PDF
            img = Image.open(screenshot_path)
            img_pdf_width, img_pdf_height = scale_image(img, A4[0] - 2 * 30, A4[1] - 2 * 30)
            x = (A4[0] - img_pdf_width) / 2
            y = (A4[1] - img_pdf_height) / 2
            pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
            pdf_report.showPage()
            i=2
            # Handle carousel posts (multiple images in one post)
            while True:
                try:
                    next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Next"]')))
                    next_button.click()
                    time.sleep(2)

                    screenshot_path = os.path.join(path, f"post_{counter}_{i}.png")
                    driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved for tagged post {counter} (next).")

                    img = Image.open(screenshot_path)
                    img_pdf_width, img_pdf_height = scale_image(img, A4[0] - 2 * 30, A4[1] - 2 * 30)
                    pdf_report.drawImage(screenshot_path, x, y, width=img_pdf_width, height=img_pdf_height)
                    pdf_report.showPage()
                    i+=1
                except Exception:
                    break

        except Exception as e:
            print(f"Error processing tagged post {counter}: {e}")
            continue
