import os
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request
from google.cloud import secretmanager
import json
from dotenv import load_dotenv
import re
import google.generativeai as genai
from flask_cors import CORS


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
credentials_json = get_secret("GOOGLE_APPLICATION_CREDENTIALS")

# Parse file JSON
credentials = json.loads(credentials_json)

KEY_API = credentials['key_api']
CHATBOT = credentials['chatbot']


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

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction=CHATBOT,
)

chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                "berikan summary nya ",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Tentu, berikut adalah ringkasan singkat tentang Rizky Yanuar Kristianto:\n\nRizky adalah seorang mahasiswa S1 Data Science berusia 21 tahun di Surabaya, dengan IPK 3,47. Ia memiliki pengalaman sebagai ketua penelitian dan anggota staf divisi advokasi mahasiswa. Rizky memiliki keahlian teknis dalam Python, Tableau, Microsoft Office, dan TensorFlow, serta keahlian tambahan di Data Mining, Deep Learning, Data Visualization, dan Manajemen Proyek. Ia juga memiliki beberapa proyek penting, termasuk prediksi depresi dari data ucapan, analisis sentimen penerima KIPK berdasarkan tweet, dan pengembangan aplikasi pelacak jejak karbon makanan NV-Bite. Rizky memiliki kemampuan analisis yang kuat dan antusiasme dalam bidang data science.\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "berikan project projectnya ",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Rizky Yanuar Kristianto memiliki beberapa proyek penting, yaitu:\n1.  **Prediksi Depresi dari Data Ucapan**: Mengembangkan model prediktif untuk mengidentifikasi indikator depresi dari data ucapan, yang dipresentasikan pada simposium penelitian universitas.\n2.  **Analisis Sentimen Penerima KIPK Berdasarkan Tweet di Platform X**: Menganalisis sentimen tweet terkait penerima KIPK menggunakan NLP dan memvisualisasikan hasilnya.\n3.  **NV-Bite: Aplikasi Pelacak Jejak Karbon Makanan**: Membangun model pembelajaran mesin untuk pengenalan makanan dan estimasi jejak karbon, berkolaborasi dengan tim cloud dan mobile untuk integrasi aplikasi.\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "summary cvnya",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Rizky Yanuar Kristianto adalah mahasiswa S1 Data Science di Surabaya dengan IPK 3,47, memiliki pengalaman sebagai ketua penelitian dan aktif dalam organisasi mahasiswa. Ia memiliki keahlian teknis seperti Python, Tableau, dan TensorFlow, serta keahlian tambahan dalam Data Mining dan Deep Learning. Rizky juga memiliki pengalaman proyek dalam analisis data dan pengembangan aplikasi, menunjukkan kemampuan analisis dan pemecahan masalah yang kuat.\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "berikan dalam perpoin",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Baik, berikut adalah poin-poin ringkasan CV Rizky Yanuar Kristianto:\n\n*   **Identitas:**\n    *   Nama: Rizky Yanuar Kristianto\n    *   Usia: 21 tahun\n    *   Domisili: Surabaya\n    *   Pendidikan: Mahasiswa S1 Data Science, Universitas Negeri Surabaya (IPK: 3,47/4,0)\n*   **Pengalaman:**\n    *   Ketua Penelitian, Fakultas Matematika dan Ilmu Pengetahuan Alam, Universitas Negeri Surabaya\n    *   Anggota Staf, Divisi Advokasi dan Kesejahteraan Mahasiswa, Himpunan Mahasiswa Data Science, Universitas Negeri Surabaya\n*   **Proyek:**\n    *   Prediksi Depresi dari Data Ucapan\n    *   Analisis Sentimen Penerima KIPK Berdasarkan Tweet di Platform X\n    *   NV-Bite: Aplikasi Pelacak Jejak Karbon Makanan\n*   **Keahlian:**\n    *   Teknis: Python, Tableau, Microsoft Office, TensorFlow\n    *   Tambahan: Data Mining, Deep Learning, Data Visualization, Manajemen Proyek\n*   **Deskripsi Singkat:**\n    *   Mahasiswa S1 Data Science dengan keterampilan analisis yang kuat, kemampuan pemecahan masalah berbasis data, dan pemikiran kritis.\n    *   Berfokus pada penerapan pengetahuan akademik untuk menyelesaikan tantangan berbasis data.\n    *   Memiliki antusiasme tinggi dalam berkontribusi pada proyek-proyek berdampak, sambil terus mengembangkan keahlian di bidang data science.\n",
            ],
        },
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
