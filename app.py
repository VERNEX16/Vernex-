from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

VALID_KEYS = ["Anonymous"]

@app.route("/")
def home():
    return "Vernex API LIVE 🚀"

@app.route("/api/numinfo")
def numinfo():
    num = request.args.get("num")
    key = request.args.get("key")

    if key not in VALID_KEYS:
        return jsonify({
            "status": "error",
            "message": "Invalid API key"
        })

    if not num:
        return jsonify({
            "status": "error",
            "message": "Missing 'num'"
        })

    external_url = "https://cyber-osint-num-infos.vercel.app/api/numinfo"

    try:
        res = requests.get(external_url, params={
            "key": "Anonymous",
            "num": num
        }, timeout=10)

        data = res.json()

        # 🔥 REMOVE EXACT KEYS (TOP LEVEL)
        data.pop("Owner", None)
        data.pop("Dm to buy access", None)

        # 🔥 CLEAN INSIDE RESULTS (if any unwanted keys exist)
        if "results" in data:
            for item in data["results"]:
                item.pop("Owner", None)
                item.pop("Dm to buy access", None)

        # ✅ ADD YOUR BRAND
        data["powered_by"] = "Vernex API ⚡"

        return jsonify(data)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "API failed",
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)
