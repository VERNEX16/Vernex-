from flask import Flask, request, jsonify
import json
import time
import random
import string
import os
from datetime import datetime

app = Flask(__name__)

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
# 📅 FORMAT TIME
# =========================
def format_time(ts):
    return datetime.fromtimestamp(ts).strftime(
        "%d-%m-%Y %I:%M:%S %p"
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
# 🔑 GENERATE KEY
# =========================
@app.route("/generate")
def generate():

    days = request.args.get("days")

    if not days:
        return jsonify({
            "success": False,
            "error": "Missing days"
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
        "owner": "VERNEX",
        "success": True,
        "key": api_key,
        "validity_days": days,
        "created_at": format_time(current_time),
        "expires_at": format_time(expires_at)
    })

# =========================
# 🔒 PROTECTED API
# =========================
@app.route("/api/data")
def api_data():

    api_key = request.args.get("key")

    if not api_key:
        return jsonify({
            "success": False,
            "error": "Missing API key"
        }), 401

    keys = load_keys()

    # ❌ INVALID KEY
    if api_key not in keys:
        return jsonify({
            "success": False,
            "error": "Invalid API key"
        }), 403

    key_data = keys[api_key]

    current_time = int(time.time())

    expires_at = key_data["expires_at"]

    # ❌ EXPIRED
    if current_time >= expires_at:

        del keys[api_key]
        save_keys(keys)

        return jsonify({
            "success": False,
            "error": "API key expired",
            "expired_at": format_time(expires_at)
        }), 403

    remaining = expires_at - current_time

    # ✅ SUCCESS
    return jsonify({
        "owner": "VERNEX",
        "success": True,

        "api_key": {
            "valid": True,
            "days": key_data["days"],
            "created_at": format_time(
                key_data["created_at"]
            ),
            "expires_at": format_time(
                expires_at
            ),
            "remaining_seconds": remaining
        },

        "data": {
            "message": "Protected API working"
        }
    })

# =========================
# ▶️ RUN
# =========================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
