# Sensor Server - Automated Battery Data Generator

Automated sensor data generation system for EV battery monitoring. Simulates real-time battery sensor readings for testing and demonstration purposes.

## 🎯 Overview

The Sensor Server generates realistic battery sensor data and stores it in MongoDB. It's designed to simulate a continuous stream of sensor readings when physical hardware is not available. Perfect for development, testing, and demonstration.

## ✨ Features

- **Continuous Data Generation**: Automatically posts sensor readings every second
- **Realistic Data**: Random values within typical battery sensor ranges
- **MongoDB Integration**: Direct insertion to MongoDB Atlas or local instance
- **Dual Mode Operation**: 
  - Local: Continuous generation (1 reading/second)
  - Vercel: Cron-based generation (60 readings/minute)
- **Status Endpoint**: Monitor generation statistics
- **Manual Trigger**: Generate data on-demand via API
- **Thread-Safe**: Background generation doesn't block server
- **Vercel Ready**: Serverless deployment with cron jobs

## 📊 Generated Data Format

Each sensor reading includes:

```json
{
  "sensor_id": "battery_001",
  "humidity": 45.2,
  "temperature": 35.5,
  "heat_index": 40.1,
  "battery_location": "cell_pack_2",
  "ambient_temp": 25.0,
  "surface_temp": 35.0,
  "core_temp": 40.0,
  "voltage": 3.8,
  "current": 2.5,
  "soc": 75,
  "timestamp": "2026-01-31T10:30:00.123Z"
}
```

## 🔢 Data Generation Ranges

| Parameter | Range | Unit | Description |
|-----------|-------|------|-------------|
| **Humidity** | 30 - 70 | % | Relative humidity |
| **Temperature** | 20 - 50 | °C | General temperature |
| **Heat Index** | 22 - 55 | - | Calculated heat stress index |
| **Ambient Temp** | 18 - 28 | °C | Surrounding temperature |
| **Surface Temp** | 25 - 45 | °C | Battery surface temperature |
| **Core Temp** | 30 - 50 | °C | Battery core temperature |
| **Voltage** | 3.0 - 4.2 | V | Cell voltage |
| **Current** | 0.5 - 3.5 | A | Charge/discharge current |
| **SOC** | 0 - 100 | % | State of Charge |
| **Sensor ID** | battery_001-010 | - | 10 different sensor IDs |
| **Location** | cell_pack_1-4 | - | 4 battery pack locations |

## 📡 API Endpoints

### Server Status
```bash
GET /
```
**Response:**
```json
{
  "server": "EV Battery Sensor Data Generator",
  "status": "running",
  "port": 5500,
  "uptime": "3600 seconds",
  "database": {
    "uri": "mongodb+srv://...",
    "database": "ev_battery_monitoring",
    "collection": "battery_sensors"
  },
  "statistics": {
    "total_posted": 3600,
    "interval": "1 second(s)",
    "last_posted": {
      "sensor_id": "battery_005",
      "humidity": 52.3,
      "temperature": 38.7,
      "core_temp": 42.1,
      "soc": 68,
      "timestamp": "2026-01-31T10:30:00Z"
    }
  }
}
```

### Health Check (Vercel)
```bash
GET /api/status
```
Returns server health and MongoDB connection status.

### Manual Data Generation (Vercel)
```bash
POST /api/generate
Content-Type: application/json

{
  "count": 10
}
```
**Response:**
```json
{
  "success": true,
  "message": "Successfully inserted 10 sensor readings",
  "count": 10
}
```
*Note: Maximum 100 readings per request*

### Cron Endpoint (Vercel Only)
```bash
GET /api/cron
```
Automatically triggered by Vercel every minute. Generates 60 readings per execution.

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB URI
   ```

3. **Set Environment Variables**:
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
   DATABASE_NAME=ev_battery_monitoring
   COLLECTION_NAME=battery_sensors
   PORT=5500
   HOST=0.0.0.0
   DEBUG=False
   INTERVAL=1
   ```

4. **Run the Server**:
   ```bash
   python app.py
   ```
   
   Output:
   ```
   ============================================================
   EV Battery Sensor Data Generator
   ============================================================
   Host: 0.0.0.0
   Port: 5500
   Debug Mode: False
   Generation Interval: 1 second(s)
   Server URL: http://0.0.0.0:5500
   MongoDB: ev_battery_monitoring.battery_sensors
   ============================================================

   ✓ MongoDB connection successful!

   Starting continuous sensor data generation...
   [10:30:01] Posting Data:
     {'sensor_id': 'battery_003', 'humidity': 45.2, ...}
     ✓ Successfully posted to MongoDB
   ```

5. **Check Status**:
   ```bash
   curl http://localhost:5500/
   ```

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
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

4. **Verify Cron Job**:
   - Go to Vercel Dashboard
   - Navigate to your project → Functions → Cron Jobs
   - Verify `/api/cron` is scheduled to run every minute

5. **Manual Test** (optional):
   ```bash
   curl -X POST https://your-sensor-server.vercel.app/api/generate \
     -H "Content-Type: application/json" \
     -d '{"count": 10}'
   ```

## 🔧 Environment Variables

Create a `.env` file (see `.env.example`):

```env
# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=ev_battery_monitoring
COLLECTION_NAME=battery_sensors

# Server Configuration
PORT=5500
HOST=0.0.0.0
DEBUG=False

# Data Generation Configuration
INTERVAL=1
```

### Environment Variable Details

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/` | Yes |
| `DATABASE_NAME` | Database name | `ev_battery_monitoring` | Yes |
| `COLLECTION_NAME` | Collection name | `battery_sensors` | Yes |
| `PORT` | Server port | `5500` | No |
| `HOST` | Server host | `0.0.0.0` | No |
| `DEBUG` | Debug mode | `False` | No |
| `INTERVAL` | Generation interval (seconds) | `1` | No |

## ⏱️ Operation Modes

### Local Development Mode
```
Continuous Generation
    ↓
Every 1 second (configurable via INTERVAL)
    ↓
Generate 1 random sensor reading
    ↓
Insert into MongoDB
    ↓
Log to console
    ↓
Repeat infinitely
```

**Data Rate**: 60 readings/minute, 3,600 readings/hour

### Vercel Production Mode
```
Vercel Cron Scheduler
    ↓
Triggered every 1 minute
    ↓
Generate 60 readings (batch)
    ↓
Bulk insert into MongoDB
    ↓
Return success response
    ↓
Wait for next cron trigger
```

**Data Rate**: 60 readings/minute, 3,600 readings/hour (same as local)

## 🧪 Testing

### Test Local Server
```bash
# Start server
python app.py

# In another terminal, check status
curl http://localhost:5500/

# Verify data in MongoDB
mongosh "your-connection-string"
> use ev_battery_monitoring
> db.battery_sensors.count()
> db.battery_sensors.find().limit(5)
```

### Test Vercel Deployment

#### Check Status
```bash
curl https://your-sensor-server.vercel.app/api/status
```

#### Manual Generation
```bash
curl -X POST https://your-sensor-server.vercel.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 5}'
```

#### Verify Cron Job
1. Wait 1-2 minutes after deployment
2. Check MongoDB for new data
3. View Vercel logs: `vercel logs`

## 📁 Project Structure

```
sensor_server/
├── app.py                   # Main Flask app (local mode)
├── requirements.txt         # Python dependencies
├── vercel.json             # Vercel config with cron
├── .env.example            # Environment variables template
├── .vercelignore           # Files excluded from deployment
└── api/
    └── index.py           # Vercel serverless entry point
```

## 🛠️ Tech Stack

- **Framework**: Flask 3.0+
- **Database**: MongoDB (PyMongo 4.6+)
- **Threading**: Python threading (local mode)
- **Deployment**: Vercel with Cron Jobs
- **Data Generation**: Python random module

## 🔄 Data Flow

### Local Mode
```
Python Thread (Background)
    ↓
generate_sensor_data()
    ↓
Random values within ranges
    ↓
MongoDB insert_one()
    ↓
Console logging
    ↓
Sleep(INTERVAL)
    ↓
Repeat
```

### Vercel Mode
```
Vercel Cron Trigger
    ↓
/api/cron endpoint
    ↓
Generate 60 readings
    ↓
MongoDB insert_many() (bulk)
    ↓
Return JSON response
```

## 🔐 Security Considerations

- MongoDB URI stored in environment variables
- No authentication on endpoints (add if needed)
- Rate limiting via Vercel (1 minute minimum interval)
- MongoDB connection timeout (5 seconds)
- Bulk insert limits (max 100 per request)

## 📈 Performance

- **Local Mode**: 1 insertion/second, minimal CPU usage
- **Vercel Mode**: 60 insertions/minute (bulk), <2 second execution time
- **Memory Usage**: ~50-100 MB (local), <256 MB (Vercel)
- **MongoDB Load**: Light write operations, indexed by timestamp

## 🐛 Troubleshooting

### MongoDB Connection Failed
```
✗ MongoDB connection failed
```
**Solutions**:
- Verify `MONGO_URI` in `.env` file
- Check MongoDB Atlas network access (whitelist IP)
- For Vercel, allow `0.0.0.0/0` (all IPs)
- Test connection string with `mongosh`

### No Data Appearing
**Solutions**:
- Wait 1-2 minutes for initial data (Vercel cron)
- Check Vercel logs: `vercel logs [deployment-url]`
- Manually trigger: `POST /api/generate`
- Verify collection name matches root server

### Cron Job Not Running (Vercel)
**Solutions**:
- Check Vercel Dashboard → Functions → Cron Jobs
- Verify `vercel.json` has correct cron configuration
- Cron jobs only work on production deployments
- Check Vercel plan supports cron jobs

### Data Generation Too Slow/Fast
**Solution** (Local):
- Adjust `INTERVAL` in `.env` file
- Example: `INTERVAL=2` for slower generation

### Memory/Timeout Issues (Vercel)
**Solutions**:
- Reduce batch size in `api/index.py`
- Optimize bulk insert operations
- Upgrade Vercel plan if needed

## 🔗 Integration

This sensor server integrates with:

| Component | Purpose | Communication |
|-----------|---------|---------------|
| **MongoDB** | Data storage | Direct PyMongo insertion |
| **Root Server** | Data consumer | Via MongoDB (indirect) |
| **ML Server** | Prediction input | Via Root Server (indirect) |

## 💡 Real Hardware Replacement

When you have physical sensors, replace this server with:

### Option 1: Microcontroller (Raspberry Pi, ESP32)
```python
import sensor_library
from pymongo import MongoClient

# Read from physical sensors
temperature = dht_sensor.read_temperature()
humidity = dht_sensor.read_humidity()

# Use same MongoDB connection and format
client.db.collection.insert_one({
    "temperature": temperature,
    "humidity": humidity,
    ...
})
```

### Option 2: FPGA + Microcontroller
```
Sensors → FPGA (signal processing) → MCU → MongoDB
```

### Option 3: Industrial Gateway
```
Sensors → Modbus/CAN → Gateway → MQTT/HTTP → MongoDB
```

## 📚 Additional Resources

- **Main Project**: [Root README](../README.md)
- **Deployment Guide**: [Vercel Deployment](../VERCEL_DEPLOYMENT.md)
- **Architecture**: [System Architecture](../ARCHITECTURE.md)
- **Root Server**: [Root Server README](../root_server/README.md)
- **ML Server**: [ML Server README](../ml_server/README.md)

## ⚠️ Important Notes

### For Testing/Demo Only
This server generates **random data** and is intended for:
- Development and testing
- System demonstrations
- Load testing
- Integration testing

### Not for Production Monitoring
For actual battery monitoring:
- Replace with real sensor hardware
- Implement proper data acquisition
- Add sensor calibration
- Include error handling for sensor failures

### MongoDB Storage
- **Data Volume**: 3,600 readings/hour = ~86,400/day
- **Storage**: ~100-200 KB per 1,000 readings
- **Retention**: Consider implementing data cleanup/archival
- **Indexing**: Add index on `timestamp` for performance

## 🎯 Use Cases

- **Development**: Test root server and ML integration
- **Demonstration**: Show system capabilities without hardware
- **Load Testing**: Generate large datasets quickly
- **Algorithm Testing**: Test ML models with varied data
- **UI Testing**: Populate dashboard with data

## 📝 License

Part of the EV Battery Monitoring System project.

---

**Status**: Production Ready ✅  
**Mode**: Dual (Local + Vercel Cron)  
**Last Updated**: January 2026  
**Data Rate**: 60 readings/minute