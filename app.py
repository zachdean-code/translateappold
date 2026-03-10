from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    input_text = data.get('text', '')
    OPENAI_API_KEY="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"
    translated_text = "Translated text from OpenAI"
    return jsonify({"output": translated_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
