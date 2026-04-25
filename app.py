from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Vernex API LIVE 🚀"

@app.route("/api/numinfo")
def numinfo():
    num = request.args.get("num")
    key = request.args.get("key")

    # Your API key check
    if key != "Anonymous":
        return jsonify({
            "status": "error",
            "message": "Invalid API key"
        })

    external_url = "https://cyber-osint-num-infos.vercel.app/api/numinfo"

    try:
        # 🔗 Call external API
        res = requests.get(external_url, params={
            "key": "Anonymous",
            "num": num
        }, timeout=10)

        data = res.json()

        # ✅ FULL RESPONSE (no change)
        # just add your name
        data["powered_by"] = "Vernex API ⚡"

        return jsonify(data)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "External API failed",
            "error": str(e)
        })
