from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/api/numinfo")
def numinfo():
    num = request.args.get("num")
    key = request.args.get("key")

    if key != "Anonymous":
        return jsonify({
            "status": "error",
            "message": "Invalid API key"
        })

    res = requests.get(
        "https://cyber-osint-num-infos.vercel.app/api/numinfo",
        params={"key": "Anonymous", "num": num},
        timeout=10
    )

    data = res.json()

    # ✅ ONLY REMOVE THESE TWO KEYS
    data.pop("Owner", None)
    data.pop("Dm to buy access", None)

    # ✅ ADD YOUR NAME ONLY
    data["powered_by"] = "Vernex API ⚡"

    return jsonify(data)
