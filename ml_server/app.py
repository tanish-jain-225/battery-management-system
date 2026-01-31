from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import joblib
import pandas as pd
import numpy as np
import os
import json

# Load environment variables
load_dotenv()

# Global Configuration Variables
PORT = int(os.getenv('PORT', 8000))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": CORS_ORIGINS}})

# Path setup to find files in the same directory as app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(
    BASE_DIR, 'EV_Battery_Charging_5000_Extended.csv')

# Load model artifacts
model = joblib.load(os.path.join(BASE_DIR, 'battery_model.pkl'))
le = joblib.load(os.path.join(BASE_DIR, 'label_encoder.pkl'))
model_columns = joblib.load(os.path.join(BASE_DIR, 'model_columns.pkl'))
scaler = joblib.load(os.path.join(BASE_DIR, 'scaler.pkl'))

# Load metadata if available
try:
    metadata = joblib.load(os.path.join(BASE_DIR, 'model_metadata.pkl'))
except:
    metadata = {'accuracy': 0.84, 'f1_score': 0.84}


def get_solution(prediction):
    """Get recommended action based on prediction."""
    solutions = {
        "Runaway": {
            "emoji": "🚨",
            "severity": "CRITICAL",
            "action": "EMERGENCY: STOP CHARGING IMMEDIATELY. Isolate vehicle and evacuate area.",
            "color": "#dc2626"
        },
        "Alarm": {
            "emoji": "⚠️",
            "severity": "HIGH",
            "action": "Severe overheating detected. Check cooling systems and reduce charge rate.",
            "color": "#ea580c"
        },
        "Warning": {
            "emoji": "🟡",
            "severity": "MEDIUM",
            "action": "Anomaly detected. Inspect for moisture, loose connections, or cell imbalance.",
            "color": "#ca8a04"
        },
        "Watch": {
            "emoji": "✅",
            "severity": "LOW",
            "action": "System stable. Continue standard monitoring procedures.",
            "color": "#16a34a"
        }
    }
    return solutions.get(prediction, {"emoji": "❓", "severity": "UNKNOWN", "action": "Unknown state.", "color": "#6b7280"})


def engineer_features(df):
    """Apply same feature engineering as training."""
    df = df.copy()
    df['TempRange'] = df['MaxTemp_C'] - df['MinTemp_C']
    df['TempDelta'] = df['MaxTemp_C'] - df['AmbientTemp_C']
    df['VoltageDiff'] = abs(df['PackVoltage_V'] - df['DemandVoltage_V'])
    df['CurrentDiff'] = abs(df['ChargeCurrent_A'] - df['DemandCurrent_A'])
    df['PowerDensity'] = df['ChargePower_kW'] / (df['SOC_%'] + 1)
    df['ThermalRisk'] = df['MaxTemp_C'] * df['InternalResistance_mOhm'] / 100
    df['HealthRisk'] = (100 - df['StateOfHealth_%']) * \
        df['VibrationLevel_mg'] / 100
    return df


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "ML Server is running",
        "model_loaded": True
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict battery status from sensor data."""
    try:
        data = request.get_json()
        df_input = pd.DataFrame([data])

        if 'MoistureDetected' in df_input.columns:
            df_input['MoistureDetected'] = df_input['MoistureDetected'].astype(
                int)

        # Apply feature engineering
        df_input = engineer_features(df_input)

        # One-hot encode and align columns
        df_input = pd.get_dummies(df_input).reindex(
            columns=model_columns, fill_value=0)

        # Scale features
        df_scaled = scaler.transform(df_input)

        # Get prediction and confidence
        pred_num = model.predict(df_scaled)[0]
        prediction = le.inverse_transform([pred_num])[0]

        # Get prediction probabilities for all classes
        probabilities = model.predict_proba(df_scaled)[0]
        confidence = float(max(probabilities) * 100)

        # Map probabilities to class names
        class_probabilities = {
            le.classes_[i]: round(float(prob * 100), 2)
            for i, prob in enumerate(probabilities)
        }

        # Reliability based on confidence
        reliability = "HIGH" if confidence > 80 else "MEDIUM" if confidence > 60 else "LOW"

        solution = get_solution(prediction)

        return jsonify({
            "status": "success",
            "prediction": prediction,
            "solution": solution,
            "confidence": round(confidence, 2),
            "reliability": reliability,
            "probabilities": class_probabilities,
            "model_accuracy": metadata.get('accuracy', 0.84),
            "input_data": data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/api/predict/batch', methods=['POST'])
def predict_batch():
    """Predict multiple battery readings at once."""
    try:
        data_list = request.get_json()
        if not isinstance(data_list, list):
            return jsonify({"status": "error", "message": "Expected array of readings"})

        results = []
        for data in data_list:
            df_input = pd.DataFrame([data])

            if 'MoistureDetected' in df_input.columns:
                df_input['MoistureDetected'] = df_input['MoistureDetected'].astype(
                    int)

            df_input = engineer_features(df_input)
            df_input = pd.get_dummies(df_input).reindex(
                columns=model_columns, fill_value=0)
            df_scaled = scaler.transform(df_input)

            pred_num = model.predict(df_scaled)[0]
            prediction = le.inverse_transform([pred_num])[0]
            probabilities = model.predict_proba(df_scaled)[0]
            confidence = float(max(probabilities) * 100)

            results.append({
                "prediction": prediction,
                "confidence": round(confidence, 2),
                "solution": get_solution(prediction)
            })

        return jsonify({
            "status": "success",
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/api/data', methods=['GET'])
def get_data():
    """Fetch all battery data with pagination and filtering."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        event_filter = request.args.get('event', None)
        sort_by = request.args.get('sort_by', 'Timestamp')
        order = request.args.get('order', 'desc')

        df = pd.read_csv(DATA_FILE)

        # Apply event filter
        if event_filter and event_filter in df['EventFlag'].unique():
            df = df[df['EventFlag'] == event_filter]

        # Sort
        if sort_by in df.columns:
            df = df.sort_values(sort_by, ascending=(order == 'asc'))

        # Pagination
        total_records = len(df)
        total_pages = (total_records + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        paginated_df = df.iloc[start_idx:end_idx]

        return jsonify({
            "status": "success",
            "data": paginated_df.to_dict(orient='records'),
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_records": total_records,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/api/data/<int:record_id>', methods=['GET'])
def get_record(record_id):
    """Get a single record by index."""
    try:
        df = pd.read_csv(DATA_FILE)
        if record_id < 0 or record_id >= len(df):
            return jsonify({"status": "error", "message": "Record not found"}), 404

        record = df.iloc[record_id].to_dict()
        return jsonify({"status": "success", "data": record})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get comprehensive statistics for dashboard."""
    try:
        df = pd.read_csv(DATA_FILE)

        return jsonify({
            "status": "success",
            "total_records": int(len(df)),
            "event_distribution": df['EventFlag'].value_counts().to_dict(),
            "event_percentages": (df['EventFlag'].value_counts(normalize=True) * 100).round(2).to_dict(),
            "temperature": {
                "max": {"mean": round(float(df['MaxTemp_C'].mean()), 2), "max": round(float(df['MaxTemp_C'].max()), 2), "min": round(float(df['MaxTemp_C'].min()), 2)},
                "avg": {"mean": round(float(df['AvgTemp_C'].mean()), 2), "max": round(float(df['AvgTemp_C'].max()), 2), "min": round(float(df['AvgTemp_C'].min()), 2)}
            },
            "soc": {"mean": round(float(df['SOC_%'].mean()), 2), "max": round(float(df['SOC_%'].max()), 2), "min": round(float(df['SOC_%'].min()), 2)},
            "health": {"mean": round(float(df['StateOfHealth_%'].mean()), 2), "min": round(float(df['StateOfHealth_%'].min()), 2)},
            "critical_count": int(len(df[df['EventFlag'].isin(['Runaway', 'Alarm'])])),
            "moisture_detected_count": int(df['MoistureDetected'].sum())
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/model/info', methods=['GET'])
def get_model_info():
    """Get model metadata and performance info."""
    try:
        return jsonify({
            "status": "success",
            "model_type": metadata.get('model_type', 'Unknown'),
            "accuracy": metadata.get('accuracy', 0),
            "f1_score": metadata.get('f1_score', 0),
            "n_features": metadata.get('n_features', 0),
            "classes": metadata.get('classes', []),
            "trained_at": metadata.get('trained_at', 'Unknown'),
            "top_features": metadata.get('top_features', [])
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None
    })


@app.route('/', methods=['GET'])
@app.route('/api', methods=['GET'])
def index():
    """API documentation endpoint."""
    return jsonify({
        "name": "EV Battery Thermal Runaway Prediction API",
        "version": "2.0",
        "status": "online",
        "model_loaded": model is not None,
        "endpoints": {
            "POST /api/predict": "Predict battery status from sensor data",
            "POST /api/predict/batch": "Batch predict multiple readings",
            "GET /api/data": "Get paginated battery data",
            "GET /api/data/<id>": "Get single record by ID",
            "GET /api/stats": "Get dashboard statistics",
            "GET /api/model/info": "Get model information",
            "GET /api/health": "Health check"
        }
    })


if __name__ == '__main__':
    print("="*60)
    print("ML Server - EV Battery Health Prediction")
    print("="*60)
    print(f"Port: {PORT}")
    print(f"CORS Origins: {CORS_ORIGINS}")
    print(f"Model Accuracy: {metadata.get('accuracy', 0.84) * 100:.1f}%")
    print(f"API Endpoint: http://localhost:{PORT}/api/predict")
    print(f"Health Check: http://localhost:{PORT}/api/health")
    print("="*60)
    print()
    print("✓ Model loaded successfully!")
    print()
    app.run(port=PORT, debug=True)
