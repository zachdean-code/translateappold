from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/translate", methods=["POST"])
def translate():

    data = request.get_json()

    text = data.get("text", "")

    target = data.get("target", "")

    if not text:
        return jsonify({"error":"No text provided"}),400


    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a professional translator."},
                {"role":"user","content":f"Translate this text to {target}: {text}"}
            ]
        )

        translated = response.choices[0].message.content

        return jsonify({
            "translation": translated
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }),500


if __name__ == "__main__":
    app.run()
