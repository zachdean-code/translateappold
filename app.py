from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status":"API running"})


@app.route("/translate", methods=["POST"])
def translate():

    data=request.get_json(silent=True) or {}

    input_text=data.get("text","").strip()

    target_language=data.get("targetLanguage","American English")

    if not input_text:
        return jsonify({"output":"","pronunciation":""})

    headers={
        "Authorization":f"Bearer {OPENAI_API_KEY}",
        "Content-Type":"application/json"
    }

    payload={

        "model":"gpt-4o-mini",

        "messages":[

            {
                "role":"system",

                "content":(
                    "You are a translation engine. "
                    "Translate the user's text into the requested target language or dialect. "
                    "Then generate a pronunciation guide for the translated sentence. "
                    "The pronunciation should help a speaker of the SOURCE language say the TRANSLATED sentence. "
                    "Use simple phonetic spelling. Do not use IPA. "
                    "Return only JSON in this format: "
                    '{"translation":"...","pronunciation":"..."}'
                )
            },

            {
                "role":"user",
                "content":f"Target language: {target_language}\n\nText:\n{input_text}"
            }

        ]

    }

    response=requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code!=200:
        return jsonify({"output":response.text,"pronunciation":""})

    result=response.json()

    content=result["choices"][0]["message"]["content"]

    try:

        parsed=json.loads(content)

        translation=parsed.get("translation","")

        pronunciation=parsed.get("pronunciation","")

    except:

        translation=content

        pronunciation=""

    return jsonify({
        "output":translation,
        "pronunciation":pronunciation
    })


if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
