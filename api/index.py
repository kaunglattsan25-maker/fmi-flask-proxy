from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Target Server
BASE_URL = "https://fmi.34306.lol"

# Browser-like headers to avoid 403 Forbidden
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://fmi.34306.lol/",
    "Origin": "https://fmi.34306.lol",
}

@app.route('/api/session', methods=['GET'])
def get_session():
    try:
        res = requests.get(f"{BASE_URL}/api/session", headers=DEFAULT_HEADERS, timeout=10)
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

        res = requests.post(f"{BASE_URL}/api/check", json={"query": query}, headers=headers, timeout=10)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/jobs/<job_id>', methods=['GET'])
def poll_job(job_id):
    try:
        token = request.headers.get('X-FMI-Browser')
        headers = DEFAULT_HEADERS.copy()
        headers['X-FMI-Browser'] = token

        res = requests.get(f"{BASE_URL}/api/jobs/{job_id}", headers=headers, timeout=10)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel requires the app object to be named 'app'