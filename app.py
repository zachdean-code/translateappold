from flask import Flask,request,jsonify
from openai import OpenAI
import os

app=Flask(__name__)
client=OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/translate",methods=["POST"])
def translate():
 data=request.get_json()
 text=data.get("text","")
 target=data.get("target","English")

 prompt=f"Translate to {target}: {text}"

 res=client.chat.completions.create(
 model="gpt-4o-mini",
 messages=[
 {"role":"system","content":"You are a translator"},
 {"role":"user","content":prompt}
 ]
 )

 translated=res.choices[0].message.content.strip()

 return jsonify({"output":translated})

if __name__=="__main__":
 app.run(host="0.0.0.0",port=5000)
