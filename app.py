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
        return jsonify({"output": "", "pronunciation": ""})

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
                    "Preserve the original meaning, tone, emotional intent, slang level, and context. "
                    "Prioritize natural phrasing over literal word-for-word translation when needed. "
                    "Use the requested regional dialect naturally and appropriately when specified. "
                    "Do not add greetings, explanations, commentary, follow-up questions, refusals, or extra words. "
                    "If the input is short, even one word, still translate it. "
                    "Then create a pronunciation guide for the translated text. "
                    "The pronunciation guide must help a speaker of the SOURCE language read the TRANSLATED text aloud naturally. "
                    "Do not use IPA. Use simple phonetic spelling based on how the source-language speaker would sound out the translated text. "
                    "Return only valid JSON in this exact format: "
                    '{"translation":"...","pronunciation":"..."}'
                )
            },
            {
                "role": "user",
                "content": (
                    f"Target language: {target_language}\n\n"
                    f"Text to translate:\n{input_text}"
                )
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
            "output": f"OpenAI error {response.status_code}: {response.text}",
            "pronunciation": ""
        }), 500

    try:
        result = response.json()
    except Exception:
        return jsonify({
            "output": f"Non-JSON response from OpenAI: {response.text}",
            "pronunciation": ""
        }), 500

    raw_content = result["choices"][0]["message"]["content"].strip()

    try:
        parsed = __import__("json").loads(raw_content)
        translation = parsed.get("translation", "").strip()
        pronunciation = parsed.get("pronunciation", "").strip()
    except Exception:
        translation = raw_content
        pronunciation = ""

    return jsonify({
        "output": translation,
        "pronunciation": pronunciation
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
