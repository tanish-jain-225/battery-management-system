# ML Server - EV Battery Health Prediction

Machine learning server for real-time battery thermal runaway prediction and health classification.

## 🎯 Overview

The ML Server provides AI-powered battery health predictions using trained classification models. It analyzes sensor data (temperature, voltage, current, humidity, etc.) to predict potential thermal runaway events and recommend preventive actions.

## ✨ Features

- **Real-time Predictions**: Instant battery health classification
- **Multi-class Detection**: Runaway, Alarm, Warning, Watch, Normal
- **Confidence Scoring**: Probability distribution for all classes
- **Batch Processing**: Analyze multiple readings at once
- **RESTful API**: Easy integration with any client
- **Vercel Ready**: Serverless deployment configuration included
- **Pre-trained Models**: Ready-to-use trained models included

## 🏗️ Model Architecture

- **Algorithm**: Ensemble classification (Random Forest/Gradient Boosting)
- **Features**: 15+ engineered features from raw sensor data
- **Classes**: 5 severity levels (Runaway, Alarm, Warning, Watch, Normal)
- **Accuracy**: ~84-86% on test data
- **Input**: Battery sensor readings (voltage, current, temperature, etc.)
- **Output**: Prediction with confidence score and recommended action

## 📡 API Endpoints

### Health Check
```bash
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "scaler_loaded": true
}
```

### Single Prediction
```bash
POST /api/predict
Content-Type: application/json
```
**Request Body:**
```json
{
  "PackVoltage_V": 370.0,
  "MaxTemp_C": 45.0,
  "MinTemp_C": 25.0,
  "AmbientTemp_C": 25.0,
  "ChargeCurrent_A": 25.0,
  "SOC_%": 75,
  "StateOfHealth_%": 95,
  "InternalResistance_mOhm": 50,
  "DemandVoltage_V": 370.0,
  "DemandCurrent_A": 25.0,
  "ChargePower_kW": 9.25,
  "Humidity_%": 50,
  "VibrationLevel_mg": 5,
  "MoistureDetected": 0,
  "CoolingSystem": "Active"
}
```
**Response:**
```json
{
  "status": "success",
  "prediction": "Watch",
  "solution": {
    "emoji": "✅",
    "severity": "LOW",
    "action": "System stable. Continue standard monitoring procedures.",
    "color": "#16a34a"
  },
  "confidence": 92.5,
  "reliability": "HIGH",
  "probabilities": {
    "Normal": 85.2,
    "Watch": 92.5,
    "Warning": 3.1,
    "Alarm": 1.0,
    "Runaway": 0.2
  },
  "model_accuracy": 0.84
}
```

### Batch Predictions
```bash
POST /api/predict/batch
Content-Type: application/json
```
**Request Body:**
```json
[
  { /* sensor reading 1 */ },
  { /* sensor reading 2 */ },
  { /* sensor reading 3 */ }
]
```

### Training Data Statistics
```bash
GET /api/stats
```
Returns comprehensive statistics about the training dataset.

### Model Information
```bash
GET /api/model/info
```
Returns model metadata, accuracy, and feature importance.

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Run the Server**:
   ```bash
   python app.py
   ```
   Server starts at `http://localhost:8000`

4. **Test the API**:
   ```bash
   curl http://localhost:8000/api/health
   ```

### Vercel Deployment

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Test Deployment**:
   ```bash
   curl https://your-ml-server.vercel.app/api/health
   ```

## 🔧 Environment Variables

Create a `.env` file (see `.env.example`):

```env
# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=False

# CORS Configuration
CORS_ORIGINS=*
```

## 🧪 Model Training

To retrain the model with your own data:

1. **Prepare Dataset**: 
   - Format: CSV with required columns
   - Include `EventFlag` column (target variable)

2. **Run Training Script**:
   ```bash
   python train.py
   ```

3. **Generated Files**:
   - `battery_model.pkl` - Trained classifier
   - `label_encoder.pkl` - Class label encoder
   - `model_columns.pkl` - Feature columns
   - `scaler.pkl` - Feature scaler
   - `model_metadata.pkl` - Model performance metrics

## 📊 Prediction Classes

| Class | Severity | Description | Action Required |
|-------|----------|-------------|-----------------|
| **Runaway** | CRITICAL | Thermal runaway imminent | EMERGENCY: Stop charging, evacuate |
| **Alarm** | HIGH | Severe overheating | Check cooling, reduce charge rate |
| **Warning** | MEDIUM | Anomaly detected | Inspect for issues |
| **Watch** | LOW | Minor concerns | Continue monitoring |
| **Normal** | NORMAL | Optimal health | Standard operation |

## 📦 Model Files

The following pre-trained model files are included:

- `battery_model.pkl` - Main classification model (10-15 MB)
- `label_encoder.pkl` - Class label encoder
- `model_columns.pkl` - Expected feature columns
- `scaler.pkl` - Feature normalization scaler
- `model_metadata.pkl` - Model performance metrics (optional)

## 🔍 Testing

### Test Health Endpoint
```bash
curl http://localhost:8000/api/health
```

### Test Prediction with Sample Data
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "PackVoltage_V": 370.0,
    "MaxTemp_C": 45.0,
    "MinTemp_C": 25.0,
    "AmbientTemp_C": 25.0,
    "ChargeCurrent_A": 25.0,
    "SOC_%": 75,
    "StateOfHealth_%": 95,
    "InternalResistance_mOhm": 50,
    "DemandVoltage_V": 370.0,
    "DemandCurrent_A": 25.0,
    "ChargePower_kW": 9.25,
    "Humidity_%": 50,
    "VibrationLevel_mg": 5,
    "MoistureDetected": 0,
    "CoolingSystem": "Active"
  }'
```

## 📁 Project Structure

```
ml_server/
├── app.py                    # Main Flask application
├── train.py                  # Model training script
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment config
├── .env.example             # Environment variables template
├── api/
│   └── index.py            # Vercel serverless entry point
├── *.pkl                    # Trained model files
└── *.csv                    # Training datasets
```

## 🛠️ Tech Stack

- **Framework**: Flask 3.0+
- **ML Library**: Scikit-learn
- **Data Processing**: Pandas, NumPy
- **Model Serialization**: Joblib
- **Deployment**: Vercel (Serverless)

## 🔐 Security Considerations

- Models are loaded once at startup (cached in memory)
- No authentication required (add if needed for production)
- CORS configurable via environment variables
- Input validation performed on all predictions
- No sensitive data stored in models

## 📈 Performance

- **Prediction Time**: <50ms per request
- **Batch Processing**: Up to 100 readings per request
- **Memory Usage**: ~100-150 MB (models in memory)
- **Concurrent Requests**: Supports multiple simultaneous predictions

## 🐛 Troubleshooting

### Model Not Loading
```
Error: No such file or directory: 'battery_model.pkl'
```
**Solution**: Ensure all `.pkl` files are in the same directory as `app.py`

### Import Errors
```
ModuleNotFoundError: No module named 'sklearn'
```
**Solution**: Install dependencies: `pip install -r requirements.txt`

### Memory Issues on Vercel
**Solution**: Vercel has 1024 MB limit. Optimize model size or upgrade plan.

## 📚 Additional Resources

- **Main Project**: [Root README](../README.md)
- **Deployment Guide**: [Vercel Deployment](../VERCEL_DEPLOYMENT.md)
- **Architecture**: [System Architecture](../ARCHITECTURE.md)

## 🤝 Integration

This ML server is designed to work with:
- **Root Server**: Dashboard and API gateway
- **Sensor Server**: Data generation (or real hardware)
- **MongoDB**: Data persistence layer

See the main project README for complete system setup.

## 📝 License

Part of the EV Battery Monitoring System project.

---

**Status**: Production Ready ✅  
**Last Updated**: January 2026 