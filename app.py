from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS
import os
import re
import json

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

# TEMP TEST — force response
return jsonify({
    "output": "Let's go have a smoke.",
    "additional_information": "TEST BACKEND HIT"
})
        prompt = f"Translate this into {target}: {text}"

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a cross-cultural translator.

Always return JSON in this exact format:

{
  "output": "...translated text...",
  "additional_information": "...only include if cultural nuance, slang, tone difference, or risk exists, otherwise empty string..."
}

Rules:
- If a word has different meanings across dialects, explain it
- If something could be offensive in another region, explain it
- If slang is used, explain it
- If no additional context is needed, return an empty string
- Do NOT include anything outside of JSON
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw = res.choices[0].message.content or ""

        try:
            parsed = json.loads(raw)
        except:
            parsed = {
                "output": clean_translation(raw),
                "additional_information": ""
            }

        parsed["output"] = clean_translation(parsed.get("output", ""))

        return jsonify(parsed)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
