from flask import Flask, render_template, request, session, redirect, url_for
import os
import uuid
from dotenv import load_dotenv
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from PIL import UnidentifiedImageError
from werkzeug.utils import secure_filename

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'a-default-fallback-secret-key')

MOBILENET_MODEL_PATH = "model/mobilenet_oral_cancer.h5"
RESNET_MODEL_PATH   = "model/resnet152v2_oral_cancer.h5" # Re-enabled

mobilenet_model = None
resnet_model    = None # Re-enabled

IMG_SIZE = (224, 224)

def load_models_lazily():
    """Load models on first request to save memory at startup."""
    global mobilenet_model, resnet_model
    if mobilenet_model is None:
        print("Lazy loading MobileNet model...")
        mobilenet_model = load_model(MOBILENET_MODEL_PATH)
        print("Lazy loading ResNet model...") # Re-enabled
        resnet_model    = load_model(RESNET_MODEL_PATH) # Re-enabled

def preprocess_image(image_path):
    image = load_img(image_path, target_size=IMG_SIZE)
    image_array = img_to_array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

def get_stage_info(risk_pct):
    if risk_pct < 25:
        return {
            'stage': 'Normal',
            'action': 'Maintain good oral hygiene. Schedule regular dental check-ups every 6 months.',
            'diet': 'Eat a balanced diet rich in fresh fruits, vegetables, and whole grains.',
            'stage_idx': 0
        }
    elif risk_pct < 50:
        return {
            'stage': 'Pre-Cancerous Stage I',
            'action': 'Avoid tobacco, alcohol, and spicy food. Consult a dentist for oral screening.',
            'diet': 'Include antioxidants: turmeric milk, green tea, carrots, beetroot, and citrus fruits.',
            'stage_idx': 1
        }
    elif risk_pct < 75:
        return {
            'stage': 'Pre-Cancerous Stage II',
            'action': 'Seek immediate medical consultation. Biopsy and further tests may be required.',
            'diet': 'Focus on anti-inflammatory foods: ginger, garlic, leafy greens, and omega-3 rich foods.',
            'stage_idx': 2
        }
    else:
        return {
            'stage': 'Cancerous Stage',
            'action': 'Urgent oncologist consultation required. Do not delay treatment.',
            'diet': 'High-protein, nutrient-dense diet. Consult a nutritionist for personalized advice.',
            'stage_idx': 3
        }

def _get_model_prediction(image_array):
    """Runs the models and returns the averaged risk percentage."""
    load_models_lazily()  # Ensure models are loaded
    mobilenet_pred = float(mobilenet_model.predict(image_array)[0][0])
    resnet_pred = float(resnet_model.predict(image_array)[0][0])
    avg_score = (mobilenet_pred + resnet_pred) / 2
    return round(avg_score * 100, 1)

def _save_uploaded_image(file):
    """Saves the uploaded file to a unique path and returns the filename and full path."""
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    upload_folder = os.path.join('static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    upload_path = os.path.join(upload_folder, unique_filename)
    file.save(upload_path)
    return unique_filename, upload_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files.get('image')
    if not file or file.filename == '':
        return render_template('index.html', error="No file selected.")

    try:
        unique_filename, upload_path = _save_uploaded_image(file)
        image_array = preprocess_image(upload_path)
        risk_pct = _get_model_prediction(image_array)

        stage_data = get_stage_info(risk_pct)

        confidences = [0.0, 0.0, 0.0, 0.0]
        confidences[stage_data['stage_idx']] = 100.0

        session['prediction'] = { # Combine dictionaries using unpacking
            'image_filename': unique_filename,
            'risk_pct':   risk_pct,
            'confidences': confidences,
            **stage_data
        }
        return redirect(url_for('result'))
    except UnidentifiedImageError:
        print("An UnidentifiedImageError occurred: The file is not a valid image.")
        return render_template('index.html', error="Invalid file format. Please upload a valid JPG, PNG, or other image file.")
    except Exception as e:
        # Log the error for debugging and show a user-friendly message
        print(f"An error occurred: {e}")
        return render_template('index.html', error="An unexpected error occurred during prediction.")

@app.route('/result')
def result():
    prediction = session.get('prediction')
    if not prediction:
        return redirect(url_for('index'))
    return render_template('result.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)