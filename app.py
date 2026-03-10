from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = "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"


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API running"})


@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(silent=True) or {}
    input_text = data.get("text", "")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional translator. Translate the user's text accurately into natural English."
            },
            {
                "role": "user",
                "content": input_text
            }
        ]
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        return jsonify({
            "output": f"OpenAI error {response.status_code}: {response.text}"
        }), 500

    try:
        result = response.json()
    except Exception:
        return jsonify({
            "output": f"Non-JSON response from OpenAI: {response.text}"
        }), 500

    translated_text = result["choices"][0]["message"]["content"]

    return jsonify({"output": translated_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
