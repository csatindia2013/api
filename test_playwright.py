"""
Test Playwright automatic scraping
"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time

def test_playwright_scraping():
    barcode = "8901526400485"  # Majirel 3
    url = f"https://smartconsumer-beta.org/01/{barcode}"
    
    print(f"🔍 Testing automatic scraping for: {url}")
    
    try:
        with sync_playwright() as p:
            print("🌐 Launching browser...")
            browser = p.chromium.launch(headless=False)  # Visible browser for testing
            page = browser.new_page()
            
            print(f"📄 Navigating to: {url}")
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            print("⏳ Waiting for content to load...")
            try:
                page.wait_for_selector('h1', timeout=10000)
                print("✅ H1 element found")
            except:
                print("⚠️ H1 not found after 10s")
            
            # Extra wait for dynamic content
            time.sleep(3)
            
            # Get rendered HTML
            html_content = page.content()
            print(f"📋 Page size: {len(html_content)} bytes")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract product name
            print("\n" + "="*60)
            print("🔍 SEARCHING FOR PRODUCT NAME")
            print("="*60)
            
            h1_elements = soup.find_all('h1')
            print(f"Found {len(h1_elements)} H1 elements:")
            for i, h1 in enumerate(h1_elements):
                text = h1.get_text(strip=True)
                classes = h1.get('class', [])
                print(f"  H1 {i+1}: '{text}' (classes: {classes})")
            
            # Extract MRP
            print("\n" + "="*60)
            print("🔍 SEARCHING FOR MRP/PRICE")
            print("="*60)
            
            spans = soup.find_all('span')
            print(f"Found {len(spans)} span elements")
            for span in spans:
                text = span.get_text(strip=True)
                if 'mrp' in text.lower() or '₹' in text or re.search(r'\d{2,5}', text):
                    classes = span.get('class', [])
                    print(f"  Span: '{text}' (classes: {classes})")
            
            # Take screenshot for debugging
            screenshot_path = "screenshot.png"
            page.screenshot(path=screenshot_path)
            print(f"\n📸 Screenshot saved: {screenshot_path}")
            
            browser.close()
            print("\n✅ Test complete!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_playwright_scraping()
