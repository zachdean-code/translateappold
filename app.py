from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API running"})


@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json() or {}

    text = data.get("text", "").strip()
    target = data.get("target", "English").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        prompt = f"Translate to {target}: {text}"

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a translator"},
                {"role": "user", "content": prompt}
            ]
        )

        translated = res.choices[0].message.content.strip()

        return jsonify({"output": translated})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
