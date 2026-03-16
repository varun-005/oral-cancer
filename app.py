from flask import Flask, render_template, request, session, redirect, url_for
import gc
import os
import uuid
from tensorflow.keras import backend as keras_backend
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from PIL import UnidentifiedImageError
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'oral_cancer_secret_2025')

MOBILENET_MODEL_PATH = "model/mobilenet_oral_cancer.h5"
RESNET_MODEL_PATH    = "model/resnet152v2_oral_cancer.h5"

IMG_SIZE = (224, 224)

def env_flag(name, default='0'):
    value = os.getenv(name, default)
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}

def predict_with_model(model_path, image_array):
    model = load_model(model_path, compile=False)
    try:
        return float(model.predict(image_array, verbose=0)[0][0])
    finally:
        del model
        keras_backend.clear_session()
        gc.collect()

def predict_risk(image_array):
    predictions = [predict_with_model(MOBILENET_MODEL_PATH, image_array)]

    if env_flag('USE_RESNET', '1'):
        predictions.append(predict_with_model(RESNET_MODEL_PATH, image_array))

    return round(sum(predictions) / len(predictions) * 100, 1)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files.get('image')
    if not file or file.filename == '':
        return render_template('index.html', error="No file selected.")

    try:
        filename        = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_folder   = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        upload_path     = os.path.join(upload_folder, unique_filename)
        file.save(upload_path)

        image_array = preprocess_image(upload_path)
        risk_pct    = predict_risk(image_array)

        stage_data  = get_stage_info(risk_pct)
        confidences = [0.0, 0.0, 0.0, 0.0]
        confidences[stage_data['stage_idx']] = 100.0

        session['prediction'] = {
            'image_filename': unique_filename,
            'risk_pct':       risk_pct,
            'confidences':    confidences,
            **stage_data
        }
        return redirect(url_for('result'))

    except UnidentifiedImageError:
        return render_template('index.html', error="Invalid file. Please upload a valid JPG or PNG image.")
    except Exception as e:
        print(f"Error: {e}")
        return render_template('index.html', error="An unexpected error occurred. Please try again.")

@app.route('/result')
def result():
    prediction = session.get('prediction')
    if not prediction:
        return redirect(url_for('index'))
    return render_template('result.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', '0') == '1')