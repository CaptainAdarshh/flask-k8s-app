from flask import Flask, jsonify
import redis
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis-service')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))

def get_redis_connection():
    """Creates a connection to Redis database"""
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=2)

@app.route('/')
def home():
    """Main endpoint - just says hello"""
    return jsonify({
        "message": "Hello from Flask running on Kubernetes!",
        "status": "running",
        "redis_host": REDIS_HOST
    })

@app.route('/health')
def health():
    """
    Health check endpoint.
    Kubernetes uses this to know if the app is working properly.
    If this returns an error, Kubernetes will restart the container.
    """
    try:
        r = get_redis_connection()
        r.ping()  
        return jsonify({"status": "healthy", "redis": "connected"}), 200
    except Exception as e:
        logging.error(f"Health check failed - cannot reach Redis at {REDIS_HOST}: {e}")
        return jsonify({
            "status": "unhealthy",
            "redis": "disconnected",
            "error": str(e),
            "redis_host": REDIS_HOST
        }), 500

@app.route('/count')
def count():
    """Counts how many times this page was visited, stored in Redis"""
    try:
        r = get_redis_connection()
        visits = r.incr('page_visits')  
        return jsonify({
            "visits": int(visits),
            "message": f"This page has been visited {visits} times!"
        })
    except Exception as e:
        return jsonify({"error": "Could not reach the database", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)