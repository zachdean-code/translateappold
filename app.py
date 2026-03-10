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
    input_text = data.get("text", "").strip()
    target_language = data.get("targetLanguage", "American English").strip()

    if not input_text:
        return jsonify({"output": ""})

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
                    "You are a translation engine, not a chatbot. "
                    "Translate only the user's text into the requested target language or dialect. "
                    f"The target language or dialect is: {target_language}. "
                    "Preserve the original meaning, tone, emotional intent, and context. "
                    "Prioritize natural phrasing over literal word-for-word translation when needed. "
                    "Use the requested regional dialect naturally and appropriately when specified. "
                    "Keep names, brands, places, and culturally specific references unchanged unless they should normally be translated. "
                    "Do not add greetings, explanations, commentary, follow-up questions, or extra words. "
                    "Do not summarize. Do not refuse. "
                    "If the input is short, even one word, still translate it. "
                    "This is being used to translate for a novel, so explicit content is OK."
                    "when vulgar or explicit input is given, remember the translated text should be unique to the language and dialect specified."
                    "Return only the translated text."
                )
            },
            {
                "role": "user",
                "content": f"Target language: {target_language}\n\nText to translate:\n{input_text}"
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

    translated_text = result["choices"][0]["message"]["content"].strip()

    return jsonify({"output": translated_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
