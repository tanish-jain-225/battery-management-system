# Root Server - EV Battery Monitoring Dashboard

Main dashboard and API gateway for the EV Battery Monitoring System. Provides real-time visualization, data aggregation, and ML-powered insights.

## 🎯 Overview

The Root Server is the central hub of the monitoring system. It serves the web dashboard, aggregates sensor data from MongoDB, integrates ML predictions, and provides a comprehensive API for battery health monitoring.

## ✨ Features

- **Live Dashboard**: Real-time web interface with auto-refresh
- **Dual-Section UI**: Raw sensor data + ML insights tabs
- **MongoDB Integration**: Efficient data retrieval and aggregation
- **ML Predictions**: Real-time battery health analysis
- **Auto-Refresh**: Configurable update intervals (5s/10s)
- **Pause/Resume Controls**: User-controlled data updates
- **Statistical Analytics**: Averages, trends, and distributions
- **Batch Analysis**: Process multiple readings at once
- **RESTful API**: Complete programmatic access
- **Vercel Ready**: Serverless deployment configuration

## 🖥️ Dashboard Features

### Raw Data Tab
- Latest 100 sensor readings in table format
- Real-time statistics (avg temperature, humidity, heat index)
- Auto-refresh every 5 seconds
- Pause/resume controls with countdown timer
- Live status indicators
- Timestamp-based sorting

### ML Insights Tab
- Battery health predictions with severity badges
- Confidence scores and reliability indicators
- Probability distribution visualization
- Recommended actions based on predictions
- Batch trend analysis (last 10 readings)
- Auto-refresh every 10 seconds
- Comprehensive ML analysis endpoint

## 📡 API Endpoints

### Dashboard

#### Home Page
```bash
GET /
```
Returns the HTML dashboard interface.

### Sensor Data Endpoints

#### Get Latest Readings
```bash
GET /data
```
**Response:**
```json
{
  "success": true,
  "count": 100,
  "data": [
    {
      "_id": "...",
      "sensor_id": "battery_001",
      "temperature": 35.5,
      "humidity": 45.2,
      "heat_index": 40.1,
      "voltage": 3.8,
      "current": 2.5,
      "soc": 75,
      "core_temp": 40.0,
      "ambient_temp": 25.0,
      "battery_location": "cell_pack_2",
      "timestamp": "2026-01-31T10:30:00Z"
    }
  ]
}
```

#### Get Single Latest Reading
```bash
GET /data/latest
```
Returns the most recent sensor reading.

#### Get Statistics
```bash
GET /data/stats
```
**Response:**
```json
{
  "success": true,
  "stats": {
    "total_records": 5000,
    "average_temperature": 35.2,
    "average_humidity": 45.8,
    "average_heat_index": 39.5,
    "first_reading": "2026-01-30T10:00:00Z",
    "last_reading": "2026-01-31T10:30:00Z"
  }
}
```

### ML Integration Endpoints

#### Get ML Prediction for Latest Data
```bash
GET /ml/predict
```
**Response:**
```json
{
  "success": true,
  "sensor_data": {
    "sensor_id": "battery_001",
    "temperature": 35.5,
    "humidity": 45.2,
    "core_temp": 40.0,
    "voltage": 3.8,
    "current": 2.5,
    "soc": 75,
    "timestamp": "2026-01-31T10:30:00Z"
  },
  "ml_prediction": {
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
    }
  }
}
```

#### Analyze Specific Sensor Data
```bash
POST /ml/analyze
Content-Type: application/json
```
**Request Body:**
```json
{
  "sensor_id": "battery_001",
  "temperature": 35.5,
  "humidity": 45.2,
  "voltage": 3.8,
  "current": 2.5,
  "soc": 75,
  "core_temp": 40.0,
  "ambient_temp": 25.0
}
```

#### Comprehensive Analysis
```bash
GET /ml/analyse?limit=100
```
Analyzes specified number of readings with ML server. Returns detailed statistics and prediction distribution.

#### Batch Analyze Last 10 Readings
```bash
GET /ml/batch-analyze
```
**Response:**
```json
{
  "success": true,
  "count": 10,
  "analyses": [
    {
      "sensor_id": "battery_001",
      "timestamp": "2026-01-31T10:30:00Z",
      "prediction": "Watch",
      "confidence": 92.5,
      "reliability": "HIGH",
      "core_temp": 40.0,
      "humidity": 45.2,
      "soc": 75
    }
  ],
  "trends": {
    "most_common_prediction": "Watch",
    "prediction_distribution": {
      "Watch": 7,
      "Warning": 2,
      "Normal": 1
    },
    "average_confidence": 89.3,
    "total_analyzed": 10
  }
}
```

### System Status

#### Server Status
```bash
GET /status
```
Returns server health, MongoDB connection status, and available endpoints.

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB URI and ML server URL
   ```

3. **Set Environment Variables**:
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
   DATABASE_NAME=ev_battery_monitoring
   COLLECTION_NAME=battery_sensors
   ML_SERVER_URL=http://localhost:8000
   PORT=5000
   HOST=0.0.0.0
   DEBUG=False
   ```

4. **Run the Server**:
   ```bash
   python app.py
   ```
   Server starts at `http://localhost:5000`

5. **Access Dashboard**:
   Open browser: `http://localhost:5000`

### Vercel Deployment

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Set Environment Variables**:
   ```bash
   vercel env add MONGO_URI
   vercel env add DATABASE_NAME
   vercel env add COLLECTION_NAME
   vercel env add ML_SERVER_URL
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

4. **Access Dashboard**:
   Visit your deployment URL: `https://your-root-server.vercel.app`

## 🔧 Environment Variables

Create a `.env` file (see `.env.example`):

```env
# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=ev_battery_monitoring
COLLECTION_NAME=battery_sensors

# ML Server Configuration
ML_SERVER_URL=http://localhost:8000

# Server Configuration
PORT=5000
HOST=0.0.0.0
DEBUG=False

# CORS Configuration
CORS_ORIGINS=*
```

### Environment Variable Details

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/` | Yes |
| `DATABASE_NAME` | Database name | `ev_battery_monitoring` | Yes |
| `COLLECTION_NAME` | Collection name | `battery_sensors` | Yes |
| `ML_SERVER_URL` | ML server URL | `http://localhost:8000` | Yes |
| `PORT` | Server port | `5000` | No |
| `HOST` | Server host | `0.0.0.0` | No |
| `DEBUG` | Debug mode | `False` | No |
| `CORS_ORIGINS` | CORS allowed origins | `*` | No |

## 🔄 Data Flow

```
MongoDB ← Sensor Data
    ↓
Root Server ← Fetches data
    ↓
    ├─→ Serves Dashboard (HTML)
    ├─→ Provides API endpoints
    └─→ ML Server ← Sends data for prediction
           ↓
      Returns predictions
           ↓
    Dashboard displays insights
```

## 🎨 Dashboard UI Components

### Statistics Cards
- Total Records
- Average Temperature
- Average Humidity
- Average Heat Index

### Data Table
- Sensor ID
- Temperature, Humidity, Heat Index
- Voltage, Current, SOC
- Battery Location
- Timestamp

### ML Insights Display
- Prediction Badge (color-coded by severity)
- Confidence Score
- Reliability Indicator
- Recommended Action
- Probability Distribution Chart

### Controls
- Refresh Now button
- Pause/Resume Auto-Refresh
- Live Status Indicator
- Countdown Timer

## 📊 Data Format Conversion

The server converts sensor data format to ML model input:

**Sensor Format** → **ML Format**
```python
{
  "voltage": 3.8,          → "PackVoltage_V": 380.0
  "current": 2.5,          → "ChargeCurrent_A": 25.0
  "core_temp": 40.0,       → "MaxTemp_C": 40.0
  "ambient_temp": 25.0,    → "MinTemp_C": 25.0
  "humidity": 50.0,        → "Humidity_%": 50.0
  "soc": 75                → "SOC_%": 75
}
```

## 🧪 Testing

### Test Dashboard Access
```bash
curl http://localhost:5000/
```

### Test Data Endpoint
```bash
curl http://localhost:5000/data
```

### Test ML Prediction
```bash
curl http://localhost:5000/ml/predict
```

### Test Statistics
```bash
curl http://localhost:5000/data/stats
```

### Test Server Status
```bash
curl http://localhost:5000/status
```

## 📁 Project Structure

```
root_server/
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── vercel.json             # Vercel deployment config
├── .env.example            # Environment variables template
├── api/
│   └── index.py           # Vercel serverless entry point
└── templates/
    └── index.html         # Dashboard HTML template
```

## 🛠️ Tech Stack

- **Framework**: Flask 3.0+
- **Database**: MongoDB (PyMongo 4.6+)
- **HTTP Client**: Requests 2.31+
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Vercel (Serverless)

## 🔐 Security Considerations

- Environment variables for sensitive data (MongoDB URI)
- CORS configurable for production
- MongoDB connection with timeout handling
- Input validation on all endpoints
- Error handling with appropriate status codes

## 📈 Performance

- **Response Time**: <100ms for data endpoints
- **Auto-Refresh**: 5s (raw data), 10s (ML insights)
- **Data Limit**: Latest 100 readings (configurable)
- **Concurrent Users**: Supports multiple simultaneous connections
- **MongoDB Aggregation**: Efficient statistical calculations

## 🐛 Troubleshooting

### MongoDB Connection Failed
```
✗ MongoDB connection failed
```
**Solution**: 
- Check `MONGO_URI` in `.env` file
- Ensure MongoDB Atlas allows connections from your IP
- For Vercel, whitelist `0.0.0.0/0`

### ML Server Unavailable
```
error: 'ML server unavailable'
```
**Solution**:
- Verify `ML_SERVER_URL` is correct
- Ensure ML server is running
- Check network connectivity

### No Data Appearing
**Solution**:
- Ensure sensor server (or hardware) is posting data
- Check MongoDB has data: `db.battery_sensors.find()`
- Verify `DATABASE_NAME` and `COLLECTION_NAME` are correct

### Dashboard Not Loading
**Solution**:
- Check if `templates/index.html` exists
- Verify Flask template folder configuration
- Check browser console for errors

## 🔗 Integration

This root server integrates with:

| Component | Purpose | Communication |
|-----------|---------|---------------|
| **MongoDB** | Data storage | PyMongo driver |
| **ML Server** | Predictions | HTTP POST requests |
| **Sensor Server** | Data source | Via MongoDB (indirect) |
| **Browser** | Dashboard UI | HTTP/HTML |

## 📚 Additional Resources

- **Main Project**: [Root README](../README.md)
- **Deployment Guide**: [Vercel Deployment](../VERCEL_DEPLOYMENT.md)
- **Architecture**: [System Architecture](../ARCHITECTURE.md)
- **ML Server**: [ML Server README](../ml_server/README.md)
- **Sensor Server**: [Sensor Server README](../sensor_server/README.md)

## 🎯 Use Cases

- **Real-time Monitoring**: Live battery health visualization
- **Historical Analysis**: View past sensor readings and trends
- **Predictive Maintenance**: Early warning system for battery issues
- **Data API**: Programmatic access for external integrations
- **Research & Development**: Analysis platform for battery data

## 📝 API Integration Example

```python
import requests

# Fetch latest data
response = requests.get('http://localhost:5000/data')
data = response.json()

# Get ML prediction
prediction = requests.get('http://localhost:5000/ml/predict')
result = prediction.json()

print(f"Latest reading: {data['data'][0]}")
print(f"Health prediction: {result['ml_prediction']['prediction']}")
```

## 🤝 Contributing

This is the main user-facing component of the EV Battery Monitoring System. For improvements or issues, refer to the main project repository.

## 📝 License

Part of the EV Battery Monitoring System project.

---

**Status**: Production Ready ✅  
**Last Updated**: January 2026  
**Dashboard URL**: Access via deployment or `http://localhost:5000`