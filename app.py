from flask import Flask, request, jsonify
import requests
import json
import time
import random
import string
import os
from datetime import datetime

app = Flask(__name__)

# =========================================
# ⚡ VERNEX CONFIG
# =========================================
OWNER = "VERNEX"
POWERED = "VERNEX API"

# =========================================
# 🌐 BACKEND API
# =========================================
BACKEND_API = "https://ft-osint-api.duckdns.org/api/number"
BACKEND_KEY = "ft-rahun2m"

# =========================================
# 📁 DATABASE
# =========================================
KEYS_FILE = "keys.json"

if not os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, "w") as f:
        json.dump({}, f)

# =========================================
# 📖 LOAD KEYS
# =========================================
def load_keys():
    try:
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# =========================================
# 💾 SAVE KEYS
# =========================================
def save_keys(data):
    with open(KEYS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================================
# 🔑 GENERATE KEY
# =========================================
def generate_key():
    return "VERNEX-" + ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=12
        )
    )

# =========================================
# 📅 FORMAT TIME
# =========================================
def format_time(ts):
    return datetime.fromtimestamp(ts).strftime(
        "%d-%m-%Y %I:%M:%S %p"
    )

# =========================================
# 🌐 HOME
# =========================================
@app.route("/")
def home():
    return jsonify({
        "owner": OWNER,
        "powered_by": POWERED,
        "status": "RUNNING",
        "message": "VERNEX NUMBER API ACTIVE"
    })

# =========================================
# 🔑 GENERATE API KEY
# =========================================
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
            "error": "Days must be number"
        }), 400

    if days <= 0:
        return jsonify({
            "success": False,
            "error": "Days must be greater than 0"
        }), 400

    current_time = int(time.time())

    # ✅ REAL EXPIRY
    expires_at = current_time + (days * 86400)

    api_key = generate_key()

    keys = load_keys()

    keys[api_key] = {
        "created_at": current_time,
        "expires_at": expires_at,
        "days": days
    }

    save_keys(keys)

    return jsonify({
        "owner": OWNER,
        "powered_by": POWERED,
        "success": True,
        "key": api_key,
        "validity_days": days,
        "created_at": format_time(current_time),
        "expires_at": format_time(expires_at)
    })

# =========================================
# 🔒 VALIDATE KEY
# =========================================
def validate_key(api_key):

    keys = load_keys()

    if api_key not in keys:
        return False, {
            "success": False,
            "error": "Invalid API key"
        }

    key_data = keys[api_key]

    current_time = int(time.time())

    expires_at = key_data["expires_at"]

    # ❌ EXPIRED
    if current_time >= expires_at:

        del keys[api_key]
        save_keys(keys)

        return False, {
            "success": False,
            "error": "API key expired",
            "expired_at": format_time(expires_at)
        }

    return True, key_data

# =========================================
# 📞 NUMBER INFO API
# =========================================
@app.route("/api/numinfo")
def numinfo():

    number = request.args.get("num")
    api_key = request.args.get("key")

    # Missing number
    if not number:
        return jsonify({
            "success": False,
            "error": "Missing number"
        }), 400

    # Missing key
    if not api_key:
        return jsonify({
            "success": False,
            "error": "Missing API key"
        }), 401

    # Validate
    valid, data = validate_key(api_key)

    if not valid:
        return jsonify(data), 403

    try:

        # =========================================
        # 🌐 BACKEND REQUEST
        # =========================================
        response = requests.get(
            BACKEND_API,
            params={
                "key": BACKEND_KEY,
                "num": number
            },
            timeout=30
        )

        backend_data = response.json()

        # =========================================
        # ❌ REMOVE BACKEND BRANDING
        # =========================================
        if isinstance(backend_data, dict):
            backend_data.pop("by", None)
            backend_data.pop("channel", None)

        current_time = int(time.time())

        remaining = data["expires_at"] - current_time

        # =========================================
        # ✅ FINAL RESPONSE
        # =========================================
        return jsonify({
            "owner": OWNER,
            "powered_by": POWERED,
            "success": True,

            "api_key": {
                "valid": True,
                "days": data["days"],
                "created_at": format_time(
                    data["created_at"]
                ),
                "expires_at": format_time(
                    data["expires_at"]
                ),
                "remaining_seconds": remaining
            },

            "result": backend_data
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =========================================
# ▶️ RUN
# =========================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
