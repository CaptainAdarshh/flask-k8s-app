from flask import Flask, jsonify
import redis
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis-service')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))

def get_redis_connection():
    
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=2)

@app.route('/')
def home():
    
    return jsonify({
        "message": "Hello from Flask v2 on Kubernetes!",
        "status": "running",
        "redis_host": REDIS_HOST
    })

@app.route('/health')
def health():
    
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