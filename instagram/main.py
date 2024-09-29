from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


from saved import fetch_saved_posts
from tagged import fetch_tagged_posts
from posts import fetch_posts
from comments import fetch_comments
from likes import fetch_likes
from chats import fetch_chats

def create_title_page(username, pdf_report):
    """Creates a title page in the PDF report."""
    width, height = A4
    pdf_report.setFont("Times-Roman", 50)
    title_y = height / 2 + 50
    pdf_report.drawCentredString(width / 2, title_y, "Instagram Report")
    
    text_width = pdf_report.stringWidth("Instagram Report", "Times-Roman", 50)
    underline_x_start = (width - text_width) / 2
    underline_y = title_y - 5
    pdf_report.setLineWidth(1)
    pdf_report.line(underline_x_start, underline_y, underline_x_start + text_width, underline_y)
    pdf_report.line(underline_x_start, underline_y - 3, underline_x_start + text_width, underline_y - 3)
    
    pdf_report.setFont("Times-Roman", 32)
    username_y = title_y - 50
    pdf_report.drawCentredString(width / 2, username_y, f"Username: {username}")
    pdf_report.showPage()

def login_instagram(driver, username, password):
    """Logs into Instagram and returns the logged-in driver session."""
    driver.get("http://www.instagram.com")
    time.sleep(6)
    
    # Login
    user_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    pass_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
    
    user_input.clear()
    pass_input.clear()
    user_input.send_keys(username)
    pass_input.send_keys(password)
    
    time.sleep(2)
    
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login_button.click()
    
    time.sleep(8)  # Wait for the page to load after login
    print(f"Logged in as {username}")

def compile_report(username, password):
    """Combines all scraped data into a single PDF report."""
    report_filename = f"Instagram_Report_{username}.pdf"
    pdf_report = canvas.Canvas(report_filename, pagesize=A4)
    
    # Create the title page
    create_title_page(username, pdf_report)
    
    # Open the browser session and login
    service = Service("C:/Users/katik/Desktop/insta-to-pdf/py/chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # Perform Instagram login
    login_instagram(driver, username, password)

    # Call the scraping functions (passing the driver)
    fetch_posts(driver, pdf_report, username)
    fetch_chats(driver, pdf_report, username)
    fetch_comments(driver, pdf_report, username)
    fetch_likes(driver, pdf_report, username)
    fetch_saved_posts(driver, pdf_report, username)
    fetch_tagged_posts(driver, pdf_report, username)
    
    # Save the final report
    pdf_report.save()
    print(f"Instagram report saved as: {report_filename}")

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    u_name = input("Enter Instagram username: ")
    passw = input("Enter Instagram password: ")
    compile_report(u_name, passw)
