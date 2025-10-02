from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import json
from product_database import get_product_info, add_product, search_products as search_db_products
from playwright.sync_api import sync_playwright
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests from your mobile app

def fetch_product_data(barcode):
    """
    Fetch product data using database lookup and web scraping fallback
    
    Args:
        barcode (str): The barcode number to search
        
    Returns:
        dict: Product data containing barcode, name, and MRP
    """
    try:
        print(f"🔍 Looking up barcode: {barcode}")
        
        # First, try to get from our product database
        product_info = get_product_info(barcode)
        if product_info:
            print(f"✅ Found in database: {product_info['name']} - ₹{product_info['mrp']}")
            return {
                'barcode': barcode,
                'name': product_info['name'],
                'mrp': product_info['mrp'],
                'category': product_info.get('category', ''),
                'brand': product_info.get('brand', ''),
                'status': 'success'
            }
        
        # If not in database, try automatic scraping with JavaScript rendering
        print("🔍 Not in database, attempting automatic scraping with JavaScript rendering...")
        
        url = f"https://smartconsumer-beta.org/01/{barcode}"
        
        try:
            with sync_playwright() as p:
                # Launch browser in headless mode
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                print(f"🌐 Loading page: {url}")
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load (wait for h1 or give it a few seconds)
                try:
                    page.wait_for_selector('h1', timeout=10000)
                    print("✅ Page content loaded")
                except:
                    print("⚠️ H1 not found, continuing anyway...")
                
                # Extra wait for dynamic content
                time.sleep(2)
                
                # Get the rendered HTML
                html_content = page.content()
                browser.close()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract product data
                product_name = None
                product_mrp = None
                
                # Try to find product name from H1
                h1_elements = soup.find_all('h1')
                for h1 in h1_elements:
                    text = h1.get_text(strip=True)
                    if text and len(text) > 2 and 'smart consumer' not in text.lower():
                        product_name = text
                        print(f"✅ Found product name: {product_name}")
                        break
                
                # Try to find product description from p tag
                if not product_name:
                    p_elements = soup.find_all('p', class_=re.compile('text-lg|product', re.I))
                    for p in p_elements:
                        text = p.get_text(strip=True)
                        if text and len(text) > 5:
                            product_name = text
                            print(f"✅ Found product name in p: {product_name}")
                            break
                
                # Try to find MRP from spans
                spans = soup.find_all('span')
                for span in spans:
                    text = span.get_text(strip=True)
                    # Look for price patterns
                    if re.search(r'₹\s*\d+', text):
                        price_match = re.search(r'₹\s*(\d+(?:\.\d{2})?)', text)
                        if price_match:
                            product_mrp = price_match.group(1)
                            print(f"✅ Found MRP: ₹{product_mrp}")
                            break
                    # Check for "View MRP" text
                    if 'view mrp' in text.lower():
                        product_mrp = 'View MRP (requires click)'
                        print(f"⚠️ Found 'View MRP' button")
                
                # If we found product data, return it
                if product_name:
                    # Auto-add to database for future use
                    if product_mrp and product_mrp != 'View MRP (requires click)':
                        add_product(barcode, product_name, product_mrp, "General", "Unknown")
                        print(f"💾 Auto-added to database: {product_name}")
                    
                    return {
                        'barcode': barcode,
                        'name': product_name,
                        'mrp': product_mrp if product_mrp else 'N/A',
                        'category': 'General',
                        'brand': 'Unknown',
                        'status': 'success'
                    }
                else:
                    print("❌ No product data found on page")
                    return {
                        'barcode': barcode,
                        'name': None,
                        'mrp': None,
                        'category': None,
                        'brand': None,
                        'status': 'error',
                        'message': 'Product not found on smartconsumer website'
                    }
                    
        except Exception as e:
            print(f"❌ Error during automatic scraping: {e}")
            return {
                'barcode': barcode,
                'name': None,
                'mrp': None,
                'category': None,
                'brand': None,
                'status': 'error',
                'message': f'Failed to scrape product: {str(e)}'
            }
        
    except Exception as e:
        return {
            'barcode': barcode,
            'name': None,
            'mrp': None,
            'status': 'error',
            'message': f'Error: {str(e)}'
        }

@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': 'Barcode API Server',
        'version': '1.0',
        'endpoints': {
            'GET /api/barcode/<barcode>': 'Fetch product data by barcode',
            'POST /api/barcode': 'Fetch product data by barcode (JSON body)'
        }
    })

@app.route('/api/barcode/<barcode>', methods=['GET'])
def get_barcode_data_get(barcode):
    """
    GET endpoint to fetch product data by barcode
    
    Example: GET /api/barcode/8906007289085
    """
    if not barcode or not barcode.isdigit():
        return jsonify({
            'status': 'error',
            'message': 'Invalid barcode. Barcode must be numeric.'
        }), 400
    
    product_data = fetch_product_data(barcode)
    
    if product_data['status'] == 'error':
        return jsonify(product_data), 404  # Not Found
    
    return jsonify(product_data)

@app.route('/api/barcode', methods=['POST'])
def get_barcode_data_post():
    """
    POST endpoint to fetch product data by barcode
    
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
    
    product_data = fetch_product_data(barcode)
    
    if product_data['status'] == 'error':
        return jsonify(product_data), 404  # Not Found
    
    return jsonify(product_data)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })

@app.route('/api/search', methods=['GET'])
def search_products():
    """Search products by name or brand"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({
            'status': 'error',
            'message': 'Query parameter "q" is required'
        }), 400
    
    results = search_db_products(query)
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results),
        'status': 'success'
    })

@app.route('/api/products', methods=['POST'])
def add_new_product():
    """Add new product to database"""
    data = request.get_json()
    
    if not data or 'barcode' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing barcode in request body'
        }), 400
    
    barcode = str(data['barcode'])
    name = data.get('name', f'Product {barcode}')
    mrp = data.get('mrp', '0.00')
    category = data.get('category', 'General')
    brand = data.get('brand', 'Unknown')
    
    add_product(barcode, name, mrp, category, brand)
    
    return jsonify({
        'barcode': barcode,
        'name': name,
        'mrp': mrp,
        'category': category,
        'brand': brand,
        'status': 'success',
        'message': 'Product added successfully'
    })

if __name__ == '__main__':
    # Run the Flask app
    # For production, use a proper WSGI server like gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)

