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
# 🔑 KEY STORAGE
# =========================
KEYS_FILE = "keys.json"

if not os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, "w") as f:
        json.dump({}, f)

def load_keys():
    with open(KEYS_FILE, "r") as f:
        return json.load(f)

def save_keys(data):
    with open(KEYS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# 🔐 GENERATE KEY
# =========================
def generate_key():
    return "VERNEX-" + ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=10)
    )

# =========================
# 🌐 HOME
# =========================
@app.route("/")
def home():
    return jsonify({
        "owner": "VERNEX",
        "status": "RUNNING"
    })

# =========================
# 🔑 GENERATE API KEY
# =========================
@app.route("/generate")
def generate():

    days = request.args.get("days")

    if not days:
        return jsonify({
            "error": "Missing days"
        }), 400

    try:
        days = int(days)
    except:
        return jsonify({
            "error": "Invalid days"
        }), 400

    key = generate_key()

    expiry = int(time.time()) + (days * 86400)

    keys = load_keys()

    keys[key] = {
        "expiry": expiry,
        "days": days
    }

    save_keys(keys)

    return jsonify({
        "owner": "VERNEX",
        "key": key,
        "validity_days": days,
        "expires_at": expiry
    })

# =========================
# 📞 FRONT API
# =========================
@app.route("/api/numinfo")
def numinfo():

    num = request.args.get("num")
    key = request.args.get("key")

    if not num:
        return jsonify({
            "error": "Missing num"
        }), 400

    if not key:
        return jsonify({
            "error": "Missing API key"
        }), 401

    keys = load_keys()

    if key not in keys:
        return jsonify({
            "error": "Invalid API key"
        }), 403

    if int(time.time()) > keys[key]["expiry"]:
        return jsonify({
            "error": "API key expired"
        }), 403

    try:

        response = requests.get(
            BACKEND_API,
            params={
                "key": BACKEND_KEY,
                "num": num
            },
            timeout=30
        )

        data = response.json()

        # ❌ Remove backend branding
        if isinstance(data, dict):
            data.pop("by", None)
            data.pop("channel", None)

        # ✅ Your branding
        return jsonify({
            "owner": "VERNEX",
            "powered_by": "VERNEX API",
            "success": True,
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
