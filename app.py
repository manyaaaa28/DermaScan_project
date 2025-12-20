import os
import numpy as np
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

app = Flask(__name__)

# ------------------- Configuration & Storage -------------------
# Render uses a temporary file system; uploads will persist only while the instance is awake
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# List to store diagnosis history (Reset when app spins down on Free Tier)
diagnosis_history = []

# ------------------- Load AI Model -------------------
MODEL_PATH = 'models/skin_model1.h5'
model = None

try:
    # Check if the model file exists before trying to load it
    if os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
        print("✅ AI Model loaded successfully.")
    else:
        print(f"❌ Model file not found at {MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# Diagnosis categories
labels = ['Acne', 'Rash', 'Allergy']

# ------------------- Routes -------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/online-consultation')
def onl_app():
    return render_template('onl_app.html')

@app.route('/offline-appointment')
def off_app():
    return render_template('off_app.html')

@app.route('/appointment')
def appointment():
    return render_template('appointment.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', history=diagnosis_history)

# ------------------- AI Prediction & History Logic -------------------
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file and model:
        # 1. Save the file
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # 2. Preprocess the image
        img = image.load_img(filepath, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0 

        # 3. Run prediction
        predictions = model.predict(img_array)
        pred_class_index = np.argmax(predictions, axis=1)[0]
        raw_confidence = np.max(predictions)
        confidence_pct = raw_confidence * 100
        
        detected_condition = labels[pred_class_index]
        confidence_text = f"{confidence_pct:.1f}%"
        result_text = f"Detected: {detected_condition} ({confidence_text} confidence)"

        # 4. Calculate Dynamic Clarity Score (Logic for Progress Bar)
        clarity_score = int(100 - (raw_confidence * 100))
        if clarity_score < 20: clarity_score = 25 

        # 5. Save to History
        history_entry = {
            "date": datetime.now().strftime("%B %d, %Y | %I:%M %p"),
            "result": detected_condition,
            "confidence": confidence_text,
            "image": filename,
            "clarity": clarity_score
        }
        diagnosis_history.insert(0, history_entry)

        return render_template('index.html', result=result_text, uploaded_image=filename)
    
    return redirect(url_for('index'))

# ------------------- Chatbot Logic -------------------
@app.route('/ask_dermagpt', methods=['POST'])
def ask_dermagpt():
    user_message = request.form.get('message') or request.json.get('message')
    if not user_message:
        return jsonify({'reply': "No message received."})

    try:
        url = "https://free.churchless.tech/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful dermatology assistant."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        reply = response_json.get("choices", [{}])[0].get("message", {}).get("content", "Error generating response.")
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f"Error: {str(e)}"})

# ------------------- Deployment Configuration -------------------
if __name__ == "__main__":
    # Render assigns a dynamic port; this line captures it.
    # Defaulting to 5022 for local testing if no port is assigned by the server.
    port = int(os.environ.get("PORT", 5022))
    app.run(host='0.0.0.0', port=port)
