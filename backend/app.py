from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency')

@app.route('/products')
def get_products():
    REQUEST_COUNT.labels(method='GET', endpoint='/products').inc()
    start = time.time()
    products = [
        {'id': 1, 'name': 'Laptop',   'price': 75000},
        {'id': 2, 'name': 'Mouse',    'price': 800},
        {'id': 3, 'name': 'Keyboard', 'price': 1500}
    ]
    REQUEST_LATENCY.observe(time.time() - start)
    return jsonify(products)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
