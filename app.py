import os
from flask import Flask, jsonify, request
from google.cloud import secretmanager
import json
from dotenv import load_dotenv
import re
import google.generativeai as genai
from flask_cors import CORS
import datetime


app = Flask(__name__)
CORS(app)

load_dotenv()


def get_secret(secret_name, project_id=None):
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv('PROJECT_ID')
    if not project_id:
        raise ValueError("PROJECT_ID environment variable is not set.")
    secret_version = f'projects/{project_id}/secrets/{secret_name}/versions/latest'
    response = client.access_secret_version(name=secret_version)
    return response.payload.data.decode('UTF-8')


# Get credentials from Secret Manager
credentials_json = get_secret("personal-data")

# Parse file JSON
credentials = json.loads(credentials_json)

KEY_API = os.getenv('KEY_API')
CHATBOT = credentials
MODEL = os.getenv('MODEL')


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": {
            "code": 200,
            "message": "Welcome to web chatbot API",
        },
        "data": None
    }), 200


genai.configure(api_key=KEY_API)


knowledge_base_content = CHATBOT

# Dapatkan bulan dan tahun sekarang
now = datetime.datetime.now()
formatted_date = now.strftime("%B %Y")

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name=MODEL,
    generation_config=generation_config,
    system_instruction=f"""
            Anda adalah chatbot virtual assistant yang menggantikan Kiki untuk menjawab pertanyaan dari orang lain. 
            Rizky lebih menyukai jawaban yang singkat, padat, jelas, namun tetap ramah. Berikut adalah beberapa aturan penting yang harus Anda ikuti:
            
            1. Jawablah berdasarkan informasi yang tersedia di knowledge base berikut:
               \n\n{knowledge_base_content}
            2. Jika tidak mengetahui jawaban, katakan dengan sopan: "Maaf, saya tidak tahu."
            3. Jika pertanyaan bersifat terlalu pribadi, sensitif, atau toxic, balas dengan: "Maaf, saya tidak bisa menjawab pertanyaan seperti itu."
            4. Semua jawaban harus dalam format markdown.
    
            Informasi tambahan untuk konteks waktu saat ini:
            Tanggal: {formatted_date}
            
            Pastikan Anda menyapa pengguna dengan hangat di awal, memberikan jawaban yang membantu, dan menutup percakapan dengan ramah.
        """,
)
chat_session = model.start_chat(
    history=[
    ]
)


@app.route("/chatbot", methods=["POST"])
def predict_website():
    data = request.get_json()
    message = data.get('message')
    print(f"Message: {message}")
    if not message:
        return jsonify({
            "status": {
                "code": 400,
                "message": "No message provided",
            },
            "data": None
        }), 400

    # Generate text using Vertex AI
    answer = chatbot(message)
    print(f"Generated Text: {answer}")
    message = {"answer": answer}
    return jsonify(message)


def chatbot(input_text):
    response = chat_session.send_message(input_text)
    generated_text = response.text
    generated_text = re.sub(
        r'^(#{1})\s*(.*?)$', r'<h1>\2</h1>', generated_text, flags=re.MULTILINE)
    generated_text = re.sub(
        r'^(#{2})\s*(.*?)$', r'<h2>\2</h2>', generated_text, flags=re.MULTILINE)
    generated_text = re.sub(
        r'^(#{3})\s*(.*?)$', r'<h3>\2</h3>', generated_text, flags=re.MULTILINE)
    generated_text = re.sub(
        r'\*\*(.*?)\*\*', r'<strong>\1</strong>', generated_text)
    generated_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', generated_text)
    generated_text = re.sub(
        r'^[\*\-]\s+(.*)$', r'<ul><li>\1</li></ul>', generated_text, flags=re.MULTILINE)
    generated_text = re.sub(
        r'^\s{2,}[\*\-]\s+(.*)$', r'<ul><li>\1</li></ul>', generated_text, flags=re.MULTILINE)
    generated_text = re.sub(r'\[(.*?)\]\((.*?)\)',
                            r'<a href="\2">\1</a>', generated_text)
    generated_text = re.sub(
        r'^>\s*(.*)$', r'<blockquote>\1</blockquote>', generated_text, flags=re.MULTILINE)
    generated_text = re.sub(r'(^|\n)([^\n]+)', r'<p>\2</p>', generated_text)
    return generated_text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
