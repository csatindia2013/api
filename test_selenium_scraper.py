"""
Test Selenium scraping locally
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def test_selenium_scrape(barcode):
    driver = None
    try:
        url = f"https://smartconsumer-beta.org/01/{barcode}"
        
        print(f"🔍 Testing Selenium scraping for: {url}")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Initialize driver
        print("🚀 Starting ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Load page
        print("🌐 Loading page...")
        driver.get(url)
        
        # Wait for content
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            print("✅ H1 element found")
        except:
            print("⚠️ H1 not found, continuing...")
        
        # Wait for JavaScript
        time.sleep(3)
        
        # Get page source
        html = driver.page_source
        print(f"📄 Page size: {len(html)} bytes")
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find product name
        print("\n" + "="*60)
        print("PRODUCT NAME")
        print("="*60)
        
        h1_elements = soup.find_all('h1')
        for i, h1 in enumerate(h1_elements):
            text = h1.get_text(strip=True)
            classes = h1.get('class', [])
            print(f"H1 {i+1}: '{text}' (classes: {classes})")
        
        # Find MRP
        print("\n" + "="*60)
        print("MRP/PRICE")
        print("="*60)
        
        spans = soup.find_all('span')
        for span in spans:
            text = span.get_text(strip=True)
            if 'mrp' in text.lower() or '₹' in text or 'view' in text.lower():
                classes = span.get('class', [])
                print(f"Span: '{text}' (classes: {classes})")
        
        driver.quit()
        print("\n✅ Test complete!")
        
    except Exception as e:
        if driver:
            driver.quit()
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test with Majirel 3
    test_selenium_scrape("8901526400485")

