import json
import datetime
import http.server
import http.client
from http import HTTPStatus
import socketserver
import mysql.connector
import decimal
# import bcrypt
from urllib.parse import urlparse, parse_qs


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        # elif isinstance(obj, decimal.Decimal):
        #     return str(obj)  # Convert Decimal to string
        return super().default(obj)

# Database Configuration(replace with your database settings)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'stock'
}

# Create a MySQL database connection
db_connection = mysql.connector.connect(**db_config)

# Create a cursor object to execute SQL queries
db_cursor = db_connection.cursor()

# CRUD OPERATIONS
# This class deals with CORS functionality
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path == '/':
            # Serve the index.html file
            # self.path = 'index.html_url'
            pass
        elif path == '/api/productManagement':
            if 'product_id' in query_params:
                # Get a specific product by ID
                product_id = query_params['product_id'][0]
                db_cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
                result = db_cursor.fetchone()

                if result:
                    product = {
                        'product_id' : result[0],
                        'product_name' : result[1],
                        'description' : result[2],
                        'category' : result[3],
                        'unit_price' : float(result[4]),
                        'quantity' : result[5],
                        'created_at' : result[6].isoformat(),
                        'updated_at' : result[7].isoformat()
                    }

                    self.send_response(200)
                    self.send_cors_headers()
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(product, cls=CustomJSONEncoder).encode())
                else:
                    self.send_response(404)
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Product not found'}).encode())
            else:
                # List all products
                db_cursor.execute("SELECT * FROM products")
                results = db_cursor.fetchall()
                # for row in results:
                products = [{
                    'product_id' : row[0],
                    'product_name' : row[1],
                    'description' : row[2],
                    'category' : row[3],
                    'unit_price' : float(row[4]),
                    'quantity' : row[5],
                    'created_at' : row[6].isoformat(),
                    'updated_at' : row[7].isoformat()
                } for row in results]

                self.send_response(200)
                self.send_cors_headers()
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(products).encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/productManagement':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = json.loads(post_data.decode())

            print(post_data)

            # Create a product
            db_cursor.execute("INSERT INTO products (product_name, description, category, unit_price, quantity) VALUES(%s, %s, %s, %s, %s)",
                              (post_data['product_name'], post_data['description'], post_data['category'], post_data['unit_price'], post_data['quantity']))
            db_connection.commit()

            product_id = db_cursor.lastrowid
            self.send_response(201)
            self.send_cors_headers()
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response_data = {"code": 201, "message": "Product created successfully", "product_id": product_id}
            self.wfile.write(json.dumps(response_data).encode())

        else:
            super().do_POST()

# Define the host and port for the server
host = 'localhost'
port = 8080

# Create and start the server
with socketserver.TCPServer((host, port), MyHandler) as server:
    print(f'Starting server on http://{host}:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Server Stopped')
