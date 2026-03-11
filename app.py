from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API running"})


@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json() or {}

        text = data.get("text", "").strip()
        target = data.get("target", "").strip()
        source = data.get("source", "").strip()

        if not text:
            return jsonify({"error": "No text provided"}), 400

        system_prompt = """
You are a professional cross-cultural translator.

You must return a JSON object with exactly these fields:

translation_text
usage_note
pronunciation_guide
show_usage_note
show_pronunciation

Rules:

1. translation_text
- Only the translated sentence.
- No explanations.
- No labels.
- No quotation marks.

2. usage_note
- Optional.
- Maximum two sentences.
- Explain slang, cultural meaning, dialect shifts, or potential offense.
- Must be written in the INPUT language.

3. pronunciation_guide
- A learner-friendly pronunciation of translation_text.
- Use simplified respelling only.
- No IPA.
- No random capitalization.

4. show_usage_note
- true only if explanation is necessary.

5. show_pronunciation
- true only when pronunciation guidance would help a learner.

Return valid JSON only.
"""

        user_prompt = f"""
Input text:
{text}

Translate into:
{target}

If source dialect is relevant:
{source}
"""

        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=300
        )

        raw = res.choices[0].message.content.strip()

        try:
            structured = json.loads(raw)
        except Exception:
            structured = {
                "translation_text": raw,
                "usage_note": "",
                "pronunciation_guide": "",
                "show_usage_note": False,
                "show_pronunciation": False
            }

        return jsonify(structured)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
