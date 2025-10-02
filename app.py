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
        
        # Try to find product name and MRP based on smartconsumer-beta.org structure
        
        # For product name - look for main heading or product title
        name_elem = (
            soup.find('h1') or 
            soup.find('h2') or
            soup.find('div', class_=re.compile('product.*name|product.*title', re.I)) or
            soup.find('span', class_=re.compile('product.*name|product.*title', re.I)) or
            soup.find('div', class_=re.compile('title|heading', re.I))
        )
        
        if name_elem:
            product_data['name'] = name_elem.get_text(strip=True)
        
        # For MRP - smartconsumer shows "View MRP" button, need to handle this
        mrp_elem = None
        
        # Look for actual price display
        price_patterns = [
            soup.find(string=re.compile(r'₹\s*\d+', re.I)),
            soup.find('span', class_=re.compile('price|mrp|cost', re.I)),
            soup.find('div', class_=re.compile('price|mrp|cost', re.I)),
            soup.find(string=re.compile('MRP.*₹', re.I))
        ]
        
        for pattern in price_patterns:
            if pattern:
                mrp_elem = pattern
                break
        
        if mrp_elem:
            if isinstance(mrp_elem, str):
                # If we found a text node, get the parent and extract price
                try:
                    parent = soup.find(string=re.compile(r'₹\s*\d+', re.I)).parent
                    mrp_text = parent.get_text(strip=True)
                except:
                    mrp_text = mrp_elem
            else:
                mrp_text = mrp_elem.get_text(strip=True)
            
            # Extract numeric value from price text
            price_match = re.search(r'₹?\s*(\d+(?:\.\d{2})?)', mrp_text)
            if price_match:
                product_data['mrp'] = price_match.group(1)
        
        # If MRP not found but "View MRP" exists, note this
        if not product_data['mrp'] and soup.find(string=re.compile('View MRP', re.I)):
            product_data['mrp'] = 'View MRP (click required)'
        
        # If we couldn't find data with specific selectors, try to extract all text
        if not product_data['name'] or not product_data['mrp']:
            page_text = soup.get_text()
            
            # Try to find any price-like pattern if MRP not found
            if not product_data['mrp']:
                price_patterns = re.findall(r'₹?\s*(\d+(?:\.\d{2})?)', page_text)
                if price_patterns:
                    product_data['mrp'] = price_patterns[0]
        
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

