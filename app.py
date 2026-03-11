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
          if not text:
        return jsonify({"error": "No text provided"}), 400

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise translator. "
                    "Return only the final translated text in the requested target language or dialect. "
                    "Do not add introductions, labels, quotation marks, explanations, warnings, notes, or context. "
                    "Do not say things like 'In American English, that would be' or include dialect names before the translation. "
                    "Do not wrap the translation in quotation marks. "
                    "Output only the translated wording the user should copy and paste."
                )
            },
            {
                "role": "user",
                "content": f"Translate this into {target}: {text}"
            }
        ]
    )

    translated = res.choices[0].message.content.strip()

    return jsonify({"output": translated})

res = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a precise translator. "
                "Return only the final translated text in the requested target language or dialect. "
                "Do not add introductions, labels, quotation marks, explanations, warnings, notes, or context. "
                "Do not say things like 'In American English, that would be' or include dialect names before the translation. "
                "Output only the translated wording the user should copy and paste."
            )
        },
        {
            "role": "user",
            "content": f"Translate this into {target}: {text}"
        }
    ]
)

        translated = res.choices[0].message.content.strip()

        return jsonify({"output": translated})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
