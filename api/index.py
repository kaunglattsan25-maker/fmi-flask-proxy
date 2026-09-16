from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # App ကနေ လှမ်းခေါ်ရင် CORS error မတက်အောင် လုပ်တာပါ

# Target Server
BASE_URL = "https://fmi.34306.lol"

# Browser-like headers (Exact mimicry)
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://fmi.34306.lol/",
    "Origin": "https://fmi.34306.lol",
    "Connection": "keep-alive",
}

# Create a global session to maintain cookies across requests
session = requests.Session()

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "FMI Flask Proxy is running!"})

@app.route('/api/session', methods=['GET'])
def get_session():
    try:
        # Session object’s get() will handle cookies automatically
        res = session.get(f"{BASE_URL}/api/session", headers=DEFAULT_HEADERS, timeout=15)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/check', methods=['POST'])
def submit_check():
    try:
        data = request.json
        query = data.get('query')
        token = request.headers.get('X-FMI-Browser')

        if not query or not token:
            return jsonify({"detail": "Missing query or token"}), 400

        headers = DEFAULT_HEADERS.copy()
        headers['X-FMI-Browser'] = token
        headers['Content-Type'] = 'application/json'

        # session.post maintains the same cookies as get_session
        res = session.post(f"{BASE_URL}/api/check", json={"query": query}, headers=headers, timeout=15)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/jobs/<job_id>', methods=['GET'])
def poll_job(job_id):
    try:
        token = request.headers.get('X-FMI-Browser')
        headers = DEFAULT_HEADERS.copy()
        headers['X-FMI-Browser'] = token

        res = session.get(f"{BASE_URL}/api/jobs/{job_id}", headers=headers, timeout=15)
        return jsonify(res.json()), res.//status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
