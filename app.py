from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# API KEY (change if needed)
VALID_KEYS = ["Anonymous"]

@app.route("/")
def home():
    return "Vernex API LIVE 🚀"

@app.route("/api/numinfo")
def numinfo():
    num = request.args.get("num")
    key = request.args.get("key")

    # ❌ Invalid key
    if key not in VALID_KEYS:
        return jsonify({
            "status": "error",
            "message": "Invalid API key"
        })

    # ❌ Missing number
    if not num:
        return jsonify({
            "status": "error",
            "message": "Missing 'num' parameter"
        })

    external_url = "https://cyber-osint-num-infos.vercel.app/api/numinfo"

    try:
        res = requests.get(external_url, params={
            "key": "Anonymous",
            "num": num
        }, timeout=10)

        if res.status_code != 200:
            return jsonify({
                "status": "error",
                "message": "External API error",
                "code": res.status_code
            })

        data = res.json()

        # 🔥 REMOVE unwanted fields
        data.pop("owner", None)
        data.pop("dm", None)
        data.pop("contact", None)

        # 🔥 Clean inside results
        if "results" in data:
            for item in data["results"]:
                item.pop("owner", None)
                item.pop("dm", None)
                item.pop("contact", None)

        # ✅ ADD YOUR NAME
        data["powered_by"] = "Vernex API ⚡"

        return jsonify(data)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "External API failed",
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)
