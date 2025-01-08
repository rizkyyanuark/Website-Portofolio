import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from google.cloud import secretmanager
import json
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
import vertexai

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

# Configure Vertex AI
PROJECT_ID = credentials['project_id']
print(f"Project ID: {PROJECT_ID}")
LOCATION = credentials['location']
MODEL_ID = credentials['model_id']

instruction = credentials['chatbot']

generation_config = {
    "max_output_tokens": 8000,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]


@app.route("/", methods=["GET"])
def index():
    return send_from_directory('templates', 'index.html')


@app.route("/predict", methods=["POST"])
def predict_text():
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
    answer = generate_text(message)
    print(f"Generated Text: {answer}")
    message = {"answer": answer}
    return jsonify(message)


def generate_text(input_text):
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=instruction,
    )
    responses = model.generate_content(
        [input_text],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )
    generated_text = ""
    for response in responses:
        generated_text += response.text
    return generated_text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
