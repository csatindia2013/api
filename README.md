# Barcode API Server

A Flask-based API server that fetches product information (Barcode, Name, MRP) from smartconsumer-beta.org for your BillDesk app.

## Features

- ✅ Receives barcode requests from mobile app
- ✅ Fetches product data from smartconsumer-beta.org
- ✅ Returns structured JSON response
- ✅ CORS enabled for cross-origin requests
- ✅ Multiple endpoint options (GET and POST)
- ✅ Error handling and validation

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

### Development Mode
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Production Mode (using gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### 1. Home
- **URL:** `/`
- **Method:** GET
- **Description:** API information and available endpoints

### 2. Get Product Data (GET)
- **URL:** `/api/barcode/<barcode>`
- **Method:** GET
- **Example:** `GET http://localhost:5000/api/barcode/8906007289085`
- **Response:**
```json
{
  "barcode": "8906007289085",
  "name": "Product Name",
  "mrp": "99.00",
  "status": "success"
}
```

### 3. Get Product Data (POST)
- **URL:** `/api/barcode`
- **Method:** POST
- **Content-Type:** application/json
- **Body:**
```json
{
  "barcode": "8906007289085"
}
```
- **Response:**
```json
{
  "barcode": "8906007289085",
  "name": "Product Name",
  "mrp": "99.00",
  "status": "success"
}
```

### 4. Health Check
- **URL:** `/health`
- **Method:** GET
- **Description:** Check if API is running

## Integration with Flutter App

### Using http package

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<Map<String, dynamic>> fetchBarcodeData(String barcode) async {
  final response = await http.get(
    Uri.parse('http://your-server-ip:5000/api/barcode/$barcode'),
  );

  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('Failed to load product data');
  }
}
```

### Using POST method

```dart
Future<Map<String, dynamic>> fetchBarcodeData(String barcode) async {
  final response = await http.post(
    Uri.parse('http://your-server-ip:5000/api/barcode'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({'barcode': barcode}),
  );

  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('Failed to load product data');
  }
}
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid barcode)
- `500`: Server Error (failed to fetch or parse data)

Error response format:
```json
{
  "barcode": "8906007289085",
  "name": null,
  "mrp": null,
  "status": "error",
  "message": "Error description"
}
```

## Notes

- The web scraping selectors may need adjustment based on the actual HTML structure of smartconsumer-beta.org
- For production deployment, consider using a proper WSGI server like gunicorn
- Add rate limiting if needed to prevent abuse
- Consider caching frequently requested barcodes to improve performance

## Deployment Options

### Local Network
Run the server on your local machine and access it from your mobile device using your computer's IP address.

### Cloud Deployment

#### Render (Recommended - Free Tier Available)
1. Push code to GitHub
2. Connect your GitHub repository to Render
3. Render will automatically detect `render.yaml` and deploy
4. Your API will be live at `https://your-app-name.onrender.com`

#### Other Options
- **Heroku:** Easy deployment with Procfile
- **AWS EC2:** Full control over server
- **Google Cloud Run:** Serverless option
- **Railway:** Similar to Render
- **PythonAnywhere:** Simple Python hosting

## License

MIT

