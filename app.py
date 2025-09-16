from flask import Flask, request, jsonify
import requests
import json
import threading
from byte import Encrypt_ID, encrypt_api  # Make sure this is correctly implemented

app = Flask(__name__)

# Load tokens from bd.json
def load_tokens():
    try:
        with open("bd.json", "r") as file:
            data = json.load(file)
        # bd.json format: [ { "token": "xxx" }, { "token": "yyy" } ]
        return [item["token"] for item in data]
    except Exception as e:
        print(f"Error loading tokens from bd.json: {e}")
        return []

# Function to send one friend request
def send_friend_request(uid, token, results):
    encrypted_id = Encrypt_ID(uid)
    payload = f"08a7c4839f1e10{encrypted_id}1801"
    encrypted_payload = encrypt_api(payload)

    region = "ind"  # Fixed region (can change if needed)
    url = f"https://client.{region}.freefiremobile.com/RequestAddingFriend"
    headers = {
        "Expect": "100-continue",
        "Authorization": f"Bearer {token}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB50",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "16",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-N975F Build/PI)",
        "Host": f"client.{region}.freefiremobile.com",
        "Connection": "close",
        "Accept-Encoding": "gzip, deflate, br"
    }

    try:
        response = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload))
        if response.status_code == 200:
            results["success"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"Error sending request with token {token}: {e}")
        results["failed"] += 1

# API endpoint
@app.route("/send_requests", methods=["GET"])
def send_requests():
    uid = request.args.get("uid")

    if not uid:
        return jsonify({"error": "uid parameter is required"}), 400

    tokens = load_tokens()
    if not tokens:
        return jsonify({"error": "No tokens found in bd.json"}), 500

    results = {"success": 0, "failed": 0}
    threads = []

    # Send using up to 100 tokens
    for token in tokens[:100]:
        thread = threading.Thread(target=send_friend_request, args=(uid, token, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    status = 1 if results["success"] != 0 else 2 

    return jsonify({
        "success_count": results["success"],
        "failed_count": results["failed"],
        "status": status
    })

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
