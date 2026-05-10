from flask import Flask, request, jsonify
import requests
import json
import time
import random
import string
import os

app = Flask(__name__)

# =========================
# 🔗 BACKEND API
# =========================
BACKEND_API = "https://ft-osint-api.duckdns.org/api/number"
BACKEND_KEY = "ft-rahun2m"

# =========================
# 📁 DATABASE FILE
# =========================
KEYS_FILE = "keys.json"

# Create file if missing
if not os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, "w") as f:
        json.dump({}, f)

# =========================
# 📖 LOAD KEYS
# =========================
def load_keys():
    try:
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# =========================
# 💾 SAVE KEYS
# =========================
def save_keys(data):
    with open(KEYS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# 🔑 GENERATE KEY
# =========================
def generate_key():
    return "VERNEX-" + ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=12
        )
    )

# =========================
# 🌐 HOME
# =========================
@app.route("/")
def home():
    return jsonify({
        "owner": "VERNEX",
        "status": "RUNNING",
        "message": "VERNEX API ACTIVE"
    })

# =========================
# 🔑 GENERATE API KEY
# =========================
@app.route("/generate")
def generate():

    days = request.args.get("days")

    if not days:
        return jsonify({
            "success": False,
            "error": "Missing days parameter"
        }), 400

    try:
        days = int(days)
    except:
        return jsonify({
            "success": False,
            "error": "Invalid days"
        }), 400

    if days <= 0:
        return jsonify({
            "success": False,
            "error": "Days must be greater than 0"
        }), 400

    # Current timestamp
    current_time = int(time.time())

    # REAL expiry
    expiry_time = current_time + (days * 24 * 60 * 60)

    # Generate API key
    api_key = generate_key()

    # Load old keys
    keys = load_keys()

    # Save new key
    keys[api_key] = {
        "created_at": current_time,
        "expiry": expiry_time,
        "days": days
    }

    save_keys(keys)

    return jsonify({
        "owner": "VERNEX",
        "success": True,
        "key": api_key,
        "validity_days": days,
        "created_at": current_time,
        "expires_at": expiry_time
    })

# =========================
# 📞 FRONT API
# =========================
@app.route("/api/numinfo")
def numinfo():

    number = request.args.get("num")
    api_key = request.args.get("key")

    # Check number
    if not number:
        return jsonify({
            "success": False,
            "error": "Missing number"
        }), 400

    # Check key
    if not api_key:
        return jsonify({
            "success": False,
            "error": "Missing API key"
        }), 401

    # Load keys
    keys = load_keys()

    # Invalid key
    if api_key not in keys:
        return jsonify({
            "success": False,
            "error": "Invalid API key"
        }), 403

    # Current time
    current_time = int(time.time())

    # Expiry
    expiry_time = keys[api_key]["expiry"]

    # REAL expiry validation
    if current_time >= expiry_time:
        return jsonify({
            "success": False,
            "error": "API key expired"
        }), 403

    try:

        # Backend request
        response = requests.get(
            BACKEND_API,
            params={
                "key": BACKEND_KEY,
                "num": number
            },
            timeout=30
        )

        data = response.json()

        # Remove backend branding
        if isinstance(data, dict):
            data.pop("by", None)
            data.pop("channel", None)

        return jsonify({
            "owner": "VERNEX",
            "powered_by": "VERNEX API",
            "success": True,
            "key_valid": True,
            "valid_until": expiry_time,
            "result": data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =========================
# ▶️ RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
