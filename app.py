from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Vernex API LIVE 🚀"

@app.route("/api/numinfo")
def numinfo():
    key = request.args.get("key")
    num = request.args.get("num")

    if key != "Anonymous":
        return jsonify({
            "status": "error",
            "message": "Invalid API key"
        })

    external_url = "https://cyber-osint-num-infos.vercel.app/api/numinfo"

    try:
        res = requests.get(external_url, params={
            "key": "Anonymous",
            "num": num
        }, timeout=10)

        data = res.json()

        # ✅ Clean + forward response
        if data.get("status") == "success":
            return jsonify({
                "status": "success",
                "data": data.get("data"),
                "powered_by": "Vernex API ⚡"
            })

        else:
            return jsonify({
                "status": data.get("status"),
                "message": data.get("message"),
                "powered_by": "Vernex API ⚡"
            })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "External API failed",
            "powered_by": "Vernex API ⚡"
        })
