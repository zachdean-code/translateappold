from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API running"})


@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(silent=True) or {}
    input_text = data.get("text", "")
    target_language = data.get("targetLanguage", "American English")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a translation engine. Translate only the user's text. "
                    f"Translate it into {target_language}. "
                    "Match the requested dialect or regional variety naturally when specified. "
                    "Do not add greetings, explanations, follow-up questions, or extra words. "
                    "Return only the translated text."
                )
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
