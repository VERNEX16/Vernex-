from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BASE_URL = "https://yash-code-with-ai.alphamovies.workers.dev/"

# 🔥 recursive cleaner
def clean_data(data):
    remove_keys = [
        "branding",
        "developer",
        "processed_by",
        "owner_contact",
        "owner",
        "dm"
    ]

    if isinstance(data, dict):
        return {
            k: clean_data(v)
            for k, v in data.items()
            if k not in remove_keys
        }

    elif isinstance(data, list):
        return [clean_data(i) for i in data]

    return data


@app.route("/")
def home():
    return "Vernex API LIVE 🚀"

@app.route("/api/numinfo")
def numinfo():
    num = request.args.get("num")

    if not num:
        return jsonify({"error": "Number is required"})

    try:
        res = requests.get(BASE_URL, params={
            "num": num,
            "key": "7189814021"
        }, timeout=10)

        raw_data = res.json()

        # 🔥 deep clean
        data = clean_data(raw_data)

        # ✅ add your branding
        data["powered_by"] = "Vernex API ⚡"

        return jsonify(data)

    except Exception as e:
        return jsonify({
            "error": "API failed",
            "details": str(e)
        })


if __name__ == "__main__":
    app.run()
