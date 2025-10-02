from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests from your mobile app

def fetch_product_data(barcode):
    """
    Fetch product data from smartconsumer-beta.org
    
    Args:
        barcode (str): The barcode number to search
        
    Returns:
        dict: Product data containing barcode, name, and MRP
    """
    try:
        url = f"https://smartconsumer-beta.org/01/{barcode}"
        
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product data (adjust selectors based on actual website structure)
        product_data = {
            'barcode': barcode,
            'name': None,
            'mrp': None,
            'status': 'success'
        }
        
        # Enhanced scraping for smartconsumer-beta.org structure
        
        # Get all text from the page for analysis
        page_text = soup.get_text()
        
        # For product name - try multiple strategies
        name_candidates = []
        
        # Strategy 1: Look for headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            heading_text = heading.get_text(strip=True)
            if heading_text and len(heading_text) > 3:
                name_candidates.append(heading_text)
        
        # Strategy 2: Look for text containing "Atta" or "Chakki" (from screenshot)
        lines = page_text.split('\n')
        for line in lines:
            line = line.strip()
            if ('atta' in line.lower() or 'chakki' in line.lower()) and len(line) > 5:
                name_candidates.append(line)
        
        # Strategy 3: Look for divs/spans with product-related classes
        for elem in soup.find_all(['div', 'span'], class_=re.compile('product|title|name|heading', re.I)):
            elem_text = elem.get_text(strip=True)
            if elem_text and len(elem_text) > 3:
                name_candidates.append(elem_text)
        
        # Strategy 4: Look for meta tags
        for meta in soup.find_all('meta'):
            content = meta.get('content', '')
            if content and ('atta' in content.lower() or 'chakki' in content.lower()):
                name_candidates.append(content)
        
        # Select the best candidate for product name
        if name_candidates:
            # Filter out very short or very long candidates
            filtered_candidates = [name for name in name_candidates if 5 <= len(name) <= 100]
            if filtered_candidates:
                # Prefer candidates that contain "Atta" or "Chakki"
                atta_candidates = [name for name in filtered_candidates if 'atta' in name.lower() or 'chakki' in name.lower()]
                if atta_candidates:
                    product_data['name'] = atta_candidates[0]
                else:
                    product_data['name'] = filtered_candidates[0]
        
        # For MRP - enhanced detection
        mrp_found = False
        
        # Strategy 1: Look for actual price with ₹ symbol
        price_pattern = re.search(r'₹\s*(\d+(?:\.\d{2})?)', page_text)
        if price_pattern:
            product_data['mrp'] = price_pattern.group(1)
            mrp_found = True
        
        # Strategy 2: Look for "View MRP" text
        if not mrp_found and re.search(r'View MRP', page_text, re.I):
            product_data['mrp'] = 'View MRP (click required)'
            mrp_found = True
        
        # Strategy 3: Look for any numeric price patterns
        if not mrp_found:
            price_patterns = re.findall(r'(\d+\.?\d*)\s*(?:Rs|₹|rupees?)', page_text, re.I)
            if price_patterns:
                product_data['mrp'] = price_patterns[0]
                mrp_found = True
        
        # Fallback strategies if primary methods didn't work
        if not product_data['name']:
            # Try to extract from page title
            title = soup.find('title')
            if title:
                title_text = title.get_text(strip=True)
                if title_text and 'smart consumer' not in title_text.lower():
                    product_data['name'] = title_text
            
            # Try to find any meaningful text that could be a product name
            if not product_data['name']:
                # Look for text that appears to be product names (capitalized, reasonable length)
                meaningful_texts = []
                for line in lines:
                    line = line.strip()
                    if (len(line) >= 10 and len(line) <= 50 and 
                        line[0].isupper() and 
                        not any(word in line.lower() for word in ['smart', 'consumer', 'search', 'view', 'click', 'mrp'])):
                        meaningful_texts.append(line)
                
                if meaningful_texts:
                    product_data['name'] = meaningful_texts[0]
        
        # Final fallback for MRP
        if not product_data['mrp']:
            # Look for any numeric patterns that could be prices
            all_numbers = re.findall(r'\b\d{2,5}(?:\.\d{2})?\b', page_text)
            if all_numbers:
                # Filter reasonable price ranges (10-10000)
                price_candidates = [num for num in all_numbers if 10 <= float(num) <= 10000]
                if price_candidates:
                    product_data['mrp'] = price_candidates[0]
        
        return product_data
        
    except requests.exceptions.RequestException as e:
        return {
            'barcode': barcode,
            'name': None,
            'mrp': None,
            'status': 'error',
            'message': f'Failed to fetch data: {str(e)}'
        }
    except Exception as e:
        return {
            'barcode': barcode,
            'name': None,
            'mrp': None,
            'status': 'error',
            'message': f'Error parsing data: {str(e)}'
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
        return jsonify(product_data), 500
    
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
        return jsonify(product_data), 500
    
    return jsonify(product_data)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })

if __name__ == '__main__':
    # Run the Flask app
    # For production, use a proper WSGI server like gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)

