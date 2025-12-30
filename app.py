import os
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from google import genai
from google.genai import types
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# ------------------- 1. App Configuration -------------------
app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Temporary in-memory history (resets when server restarts)
diagnosis_history = []

# ------------------- 2. AI Model Loading (Keras) -------------------
MODEL_PATH = 'models/skin_model1.h5'
model = None
labels = ['Acne', 'Rash', 'Allergy']

try:
    if os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
        print("✅ Keras AI Model loaded successfully.")
    else:
        print(f"❌ Model file not found at {MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# ------------------- 3. Gemini 2.5 Configuration -------------------
# Pulls from Render Environment Variables first; falls back to your verified key locally
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAWPtlUB4l7eYPIw741HidrtnAjmaMuE_0")
client = genai.Client(api_key=GEMINI_API_KEY)

# ------------------- 4. General Routes -------------------
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

# ------------------- 5. AI Prediction Logic (Keras) -------------------
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file and model:
        # Save image
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Preprocess for Keras Model
        img = image.load_img(filepath, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0 

        # Run Prediction
        predictions = model.predict(img_array)
        pred_class_index = np.argmax(predictions, axis=1)[0]
        raw_confidence = np.max(predictions)
        
        detected_condition = labels[pred_class_index]
        confidence_text = f"{raw_confidence * 100:.1f}%"
        result_text = f"Detected: {detected_condition} ({confidence_text} confidence)"

        # Calculate Clarity Score for UI progress bar
        clarity_score = int(100 - (raw_confidence * 100))
        if clarity_score < 20: clarity_score = 25 

        # Save to Dashboard History
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

# ------------------- 6. Chatbot Logic (Gemini 2.5 Flash) -------------------
@app.route('/ask_dermagpt', methods=['POST'])
def ask_dermagpt():
    data = request.get_json(silent=True) or {}
    user_message = data.get('message') or request.form.get('message')
    
    if not user_message:
        return jsonify({'reply': "No message received."})

    try:
        # Using Gemini 2.5 Flash as verified in your test_app.py
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are DermaGPT, a world-class AI dermatology assistant. "
                    "Provide helpful, educational information about skin concerns. "
                    "Always include a disclaimer that you are an AI and not a doctor."
                ),
                temperature=0.5
            )
        )
        return jsonify({'reply': response.text})
        
    except Exception as e:
        print(f"DEBUG ERROR: {e}") 
        return jsonify({'reply': "I encountered an error. Please try again or check the terminal logs."})

# ------------------- 7. Deployment -------------------
if __name__ == "__main__":
    # Uses Render's dynamic port or 5022 for local testing
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)