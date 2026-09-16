from flask import Flask, render_template, request, jsonify
import requests
import time

app = Flask(__name__)

BASE_URL = "https://fmi.34306.lol"

def get_fmi_data(query):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": f"{BASE_URL}/",
        "Origin": BASE_URL,
    }

    try:
        # Step 1: Get Session Token
        r_session = session.get(f"{BASE_URL}/api/session", headers=headers, timeout=15)
        r_session.raise_for_status()
        token = r_session.json().get("token")
        
        if not token:
            return {"error": "Failed to obtain session token"}, 400

        # Step 2: Submit Check Request
        check_headers = headers.copy()
        check_headers["X-FMI-Browser"] = token
        
        r_check = session.post(
            f"{BASE_URL}/api/check", 
            headers=check_headers, 
            json={"query": query},
            timeout=15
        )
        
        if r_check.status_code not in [200, 202]:
            return {"error": r_check.json().get("detail", "Submission failed")}, r_check.status_code

        job_id = r_check.json().get("job_id")
        if not job_id:
            return {"error": "No job ID returned"}, 400

        # Step 3: Poll for Result
        max_attempts = 30
        for i in range(max_attempts):
            r_poll = session.get(
                f"{BASE_URL}/api/jobs/{job_id}", 
                headers=check_headers, 
                timeout=15
            )
            r_poll.raise_for_status()
            data = r_poll.json()
            status = data.get("status")
            
            if status == "done":
                return data, 200
            elif status == "error":
                return {"error": data.get("error", "Job failed on server")}, 500
            
            time.sleep(2)
            
        return {"error": "Request timed out after polling"}, 504

    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_fmi():
    data = request.json
    query = data.get('device_id')
    
    if not query:
        return jsonify({"error": "Please provide SN or IMEI"}), 400

    result, status_code = get_fmi_data(query)
    return jsonify(result), status_code

if __name__ == '__main__':
    app.run(debug=True, port=5000)
