from flask import Flask, request, jsonify
import requests
import sqlite3
import time
import random
import string

app = Flask(__name__)

# 🔗 External API
BASE_URL = "https://vernex-1.onrender.com/api/numinfo"

# 🗄️ Database setup
def init_db():
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS keys (key TEXT, expiry REAL)")
    conn.commit()
    conn.close()

init_db()

# 🔑 Generate key
def generate_key(days):
    key = "VERNEX-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    expiry = time.time() + (days * 86400) if days != 0 else 9999999999

    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("INSERT INTO keys VALUES (?, ?)", (key, expiry))
    conn.commit()
    conn.close()

    return key

# ✅ Check key
def valid_key(key):
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("SELECT expiry FROM keys WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()

    if not row:
        return False

    return time.time() < row[0]

# 🌐 Home
@app.route("/")
def home():
    return "Vernex API + Key System LIVE 🚀"

# 🔑 Generate key API
@app.route("/generate")
def generate():
    days = int(request.args.get("days", 1))  # default 1 day
    key = generate_key(days)

    return jsonify({
        "key": key,
        "valid_days": days
    })

# 📞 Main API
@app.route("/api/numinfo")
def numinfo():
    num = request.args.get("num")
    key = request.args.get("key")

    if not valid_key(key):
        return jsonify({"error": "Invalid or expired key"})

    try:
        res = requests.get(BASE_URL, params={"num": num}, timeout=10)
        data = res.json()

        data["powered_by"] = "Vernex API ⚡"
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run()
