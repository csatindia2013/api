from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests from your mobile app

def scrape_product_with_selenium(barcode):
    """
    Scrape product data from smartconsumer using Selenium for JavaScript rendering
    
    Args:
        barcode (str): The barcode number to search
        
    Returns:
        dict: Product data containing barcode, name, and MRP
    """
    driver = None
    try:
        url = f"https://smartconsumer-beta.org/01/{barcode}"
        
        print(f"🔍 Scraping: {url}")
        
        # Setup Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Initialize Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Load the page
        print("🌐 Loading page...")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        
        # Wait for content to load (h1 element)
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            print("✅ Content loaded")
        except:
            print("⚠️ Timeout waiting for H1")
        
        # Give extra time for JavaScript to fully render
        time.sleep(3)
        
        # Get page source after JavaScript rendering
        page_source = driver.page_source
        print(f"📄 Page size after rendering: {len(page_source)} bytes")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract product data
        product_data = {
            'barcode': barcode,
            'name': None,
            'mrp': None,
            'status': 'success'
        }
        
        # Extract product name from H1
        h1_elements = soup.find_all('h1')
        print(f"Found {len(h1_elements)} H1 elements")
        
        for h1 in h1_elements:
            text = h1.get_text(strip=True)
            if text and len(text) > 2 and 'smart consumer' not in text.lower():
                product_data['name'] = text
                print(f"✅ Product name: {text}")
                break
        
        # If no H1, try P tag
        if not product_data['name']:
            p_elements = soup.find_all('p')
            for p in p_elements:
                text = p.get_text(strip=True)
                classes = p.get('class', [])
                # Look for product description paragraphs
                if text and len(text) > 10 and len(text) < 100:
                    if any('text-lg' in str(c) for c in classes):
                        product_data['name'] = text
                        print(f"✅ Product name from P: {text}")
                        break
        
        # Extract MRP from spans
        spans = soup.find_all('span')
        for span in spans:
            text = span.get_text(strip=True)
            
            # Look for actual price with ₹ symbol
            if re.search(r'₹\s*\d+', text):
                price_match = re.search(r'₹\s*(\d+(?:\.\d{2})?)', text)
                if price_match:
                    product_data['mrp'] = price_match.group(1)
                    print(f"✅ MRP: ₹{product_data['mrp']}")
                    break
            
            # Check for "View MRP" text (fallback)
            if 'view mrp' in text.lower() and not product_data['mrp']:
                product_data['mrp'] = 'N/A'
                print(f"⚠️ MRP requires click - setting as N/A")
        
        # Close browser
        driver.quit()
        
        # Check if we found product data
        if product_data['name']:
            return product_data
        else:
            return {
                'barcode': barcode,
                'name': None,
                'mrp': None,
                'status': 'error',
                'message': 'Product not found on smartconsumer website'
            }
        
    except Exception as e:
        if driver:
            driver.quit()
        
        print(f"❌ Selenium error: {str(e)}")
        return {
            'barcode': barcode,
            'name': None,
            'mrp': None,
            'status': 'error',
            'message': f'Scraping failed: {str(e)}'
        }

@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': 'Barcode API Server with Selenium Scraping',
        'version': '2.0',
        'endpoints': {
            'GET /api/barcode/<barcode>': 'Fetch product data by barcode',
            'POST /api/barcode': 'Fetch product data by barcode (JSON body)',
            'GET /health': 'Health check'
        }
    })

@app.route('/api/barcode/<barcode>', methods=['GET'])
def get_barcode_data_get(barcode):
    """
    GET endpoint to fetch product data by barcode using Selenium scraping
    
    Example: GET /api/barcode/8906007289085
    """
    if not barcode or not barcode.isdigit():
        return jsonify({
            'status': 'error',
            'message': 'Invalid barcode. Barcode must be numeric.'
        }), 400
    
    product_data = scrape_product_with_selenium(barcode)
    
    if product_data['status'] == 'error':
        return jsonify(product_data), 404
    
    return jsonify(product_data)

@app.route('/api/barcode', methods=['POST'])
def get_barcode_data_post():
    """
    POST endpoint to fetch product data by barcode using Selenium scraping
    
    Expected JSON body:
    {
        "barcode": "8906007289085"
    }
    """
    data = request.get_json()
    
    if not data or 'barcode' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing barcode in request body'
        }), 400
    
    barcode = str(data['barcode'])
    
    if not barcode.isdigit():
        return jsonify({
            'status': 'error',
            'message': 'Invalid barcode. Barcode must be numeric.'
        }), 400
    
    product_data = scrape_product_with_selenium(barcode)
    
    if product_data['status'] == 'error':
        return jsonify(product_data), 404
    
    return jsonify(product_data)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Selenium Scraper API is running'
    })

if __name__ == '__main__':
    # Run the Flask app
    print("🚀 Starting Flask app with Selenium scraper...")
    print("⚠️  Note: Selenium requires ChromeDriver. Installing automatically...")
    app.run(host='0.0.0.0', port=5000, debug=True)
