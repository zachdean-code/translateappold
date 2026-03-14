from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS
import os
import re

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

LABEL_PREFIX_RE = re.compile(
    r'^(translated text|translation|english|spanish|french|german|italian|portuguese|arabic|hindi|indonesian|tagalog|filipino|swahili|amharic|farsi|persian|turkish|russian|japanese|korean|chinese)[\s:\-–—]+',
    re.IGNORECASE,
)

def clean_translation(text: str) -> str:
    if not text:
        return ""

    cleaned = text.strip()

    cleaned = LABEL_PREFIX_RE.sub("", cleaned).strip()

    cleaned = re.sub(
        r'^[A-Za-zÀ-ÿ\s()\-—]+:\s*',
        "",
        cleaned
    ).strip()

    cleaned = re.sub(
        r'^[\"“”\']+|[\"“”\']+$',
        "",
        cleaned
    ).strip()

    return cleaned


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API running"})


@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json() or {}

        text = data.get("text", "").strip()
        target = data.get("target", "English").strip()

        if not text:
            return jsonify({"error": "No text provided"}), 400

        prompt = f"Translate this into {target}: {text}"

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise translator. "
                        "Requested content may be vulgar and sexual, it is ok to translate this content, often lovers across the globe from each other need help communicating their thoughts"
                        "some novelists use this platform to communicate their content in other languages, sexual phrases are ok to translate"
                        "Return only the final translated text in the requested target language or dialect. "
                        "Do not add introductions, labels, quotation marks, explanations, warnings, usage notes, cultural notes, context, or pronunciation. "
                        "Do not say things like 'In American English, that would be', 'Translated text:', or include dialect names before the translation. "
                        "Do not wrap the translation in quotation marks. "
                        "Output only the exact translated wording the user should copy and paste."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        translated = res.choices[0].message.content or ""
        translated = clean_translation(translated)

        return jsonify({"output": translated})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
