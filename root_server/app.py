# Importing Required Libraries
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import requests

# Standard Libraries
import os

# Load environment variables
load_dotenv()

# Global Configuration Variables
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'ev_battery_monitoring')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'battery_sensors')
ML_SERVER_URL = os.getenv('ML_SERVER_URL', 'http://localhost:8000')
PORT = int(os.getenv('PORT', 5000))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

# Flask App
app = Flask(__name__)
CORS(app, origins=CORS_ORIGINS)

# Global MongoDB Connection with timeout
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    sensor_collection = db[COLLECTION_NAME]
    # Test connection
    client.server_info()
    print("✓ MongoDB connection successful!")
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")
    raise


@app.route('/', methods=['GET'])
def home():
    """Serve the main HTML page"""
    return render_template('index.html')


@app.route('/test', methods=['GET'])
def test():
    """Serve the ML test page"""
    return render_template('test_ml.html')


@app.route('/data', methods=['GET'])
def get_sensor_data():
    """
    Fetch all sensor data posted by sensor_server
    Returns latest 100 records by default
    """
    try:
        # Fetch latest 100 sensor readings from MongoDB - 100 at a time and keeps on updating with latest data
        data = list(sensor_collection.find().sort('timestamp', -1).limit(100))

        # Convert ObjectId to string and format timestamps
        for item in data:
            item['_id'] = str(item['_id'])
            if 'timestamp' in item and isinstance(item['timestamp'], datetime):
                item['timestamp'] = item['timestamp'].isoformat()

        return jsonify({
            'success': True,
            'count': len(data),
            'data': data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/data/latest', methods=['GET'])
def get_latest_data():
    """Fetch the most recent sensor reading"""
    try:
        latest = sensor_collection.find_one(sort=[('timestamp', -1)])

        if latest:
            latest['_id'] = str(latest['_id'])
            if 'timestamp' in latest and isinstance(latest['timestamp'], datetime):
                latest['timestamp'] = latest['timestamp'].isoformat()

            return jsonify({
                'success': True,
                'data': latest
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No data found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/data/stats', methods=['GET'])
def get_stats():
    """Get statistics about the sensor data"""
    try:
        total_count = sensor_collection.count_documents({})

        if total_count == 0:
            return jsonify({
                'success': True,
                'stats': {
                    'total_records': 0,
                    'avg_voltage': 0,
                    'avg_current': 0,
                    'avg_temperature': 0,
                    'avg_core_temp': 0,
                    'avg_surface_temp': 0,
                    'avg_soc': 0,
                    'avg_humidity': 0,
                    'avg_heat_index': 0,
                    'avg_ambient_temp': 0,
                    'first_reading': None,
                    'last_reading': None
                }
            }), 200

        # Get first and last readings
        first = sensor_collection.find_one(sort=[('timestamp', 1)])
        last = sensor_collection.find_one(sort=[('timestamp', -1)])

        # Calculate averages using aggregation
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'avg_voltage': {'$avg': '$voltage'},
                    'avg_current': {'$avg': '$current'},
                    'avg_temp': {'$avg': '$temperature'},
                    'avg_core_temp': {'$avg': '$core_temp'},
                    'avg_surface_temp': {'$avg': '$surface_temp'},
                    'avg_soc': {'$avg': '$soc'},
                    'avg_humidity': {'$avg': '$humidity'},
                    'avg_heat_index': {'$avg': '$heat_index'},
                    'avg_ambient_temp': {'$avg': '$ambient_temp'}
                }
            }
        ]

        aggregation_result = list(sensor_collection.aggregate(pipeline))
        averages = aggregation_result[0] if aggregation_result else {}

        stats = {
            'total_records': total_count,
            'avg_voltage': round(averages.get('avg_voltage', 0), 2),
            'avg_current': round(averages.get('avg_current', 0), 2),
            'avg_temperature': round(averages.get('avg_temp', 0), 2),
            'avg_core_temp': round(averages.get('avg_core_temp', 0), 2),
            'avg_surface_temp': round(averages.get('avg_surface_temp', 0), 2),
            'avg_soc': round(averages.get('avg_soc', 0), 2),
            'avg_humidity': round(averages.get('avg_humidity', 0), 2),
            'avg_heat_index': round(averages.get('avg_heat_index', 0), 2),
            'avg_ambient_temp': round(averages.get('avg_ambient_temp', 0), 2),
            'first_reading': first['timestamp'].isoformat() if first and 'timestamp' in first else None,
            'last_reading': last['timestamp'].isoformat() if last and 'timestamp' in last else None
        }

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/status', methods=['GET'])
def status():
    """Server status endpoint"""
    try:
        # Test MongoDB connection
        client.admin.command('ping')
        db_status = 'connected'
    except:
        db_status = 'disconnected'

    return jsonify({
        'server': 'Root Server - EV Battery Data API',
        'port': PORT,
        'database': {
            'status': db_status,
            'database': DATABASE_NAME,
            'collection': COLLECTION_NAME
        },
        'endpoints': {
            'GET /': 'Home page',
            'GET /data': 'Fetch all sensor data (latest 100)',
            'GET /data/latest': 'Fetch latest sensor reading',
            'GET /data/stats': 'Get statistics',
            'GET /ml/predict': 'Get ML prediction for latest data',
            'GET /ml/analyse': 'Analyze all MongoDB data with ML server (with ?limit=N)',
            'POST /ml/analyze': 'Analyze specific sensor data with ML',
            'GET /ml/batch-analyze': 'Batch analyze last 10 readings',
            'GET /status': 'Server status'
        }
    })


def convert_sensor_to_ml_format(sensor_data):
    """Convert sensor data format to ML model input format"""
    return {
        # Scale voltage
        "PackVoltage_V": sensor_data.get('voltage', 3.7) * 100,
        "MaxTemp_C": sensor_data.get('core_temp', 35),
        "MinTemp_C": sensor_data.get('ambient_temp', 25),
        "AmbientTemp_C": sensor_data.get('ambient_temp', 25),
        # Scale current
        "ChargeCurrent_A": sensor_data.get('current', 2.0) * 10,
        "SOC_%": sensor_data.get('soc', 50),
        "StateOfHealth_%": 95,  # Default value
        "InternalResistance_mOhm": 50,  # Default value
        "DemandVoltage_V": sensor_data.get('voltage', 3.7) * 100,
        "DemandCurrent_A": sensor_data.get('current', 2.0) * 10,
        "ChargePower_kW": (sensor_data.get('voltage', 3.7) * sensor_data.get('current', 2.0) * 100) / 1000,
        "Humidity_%": sensor_data.get('humidity', 50),
        "VibrationLevel_mg": 5,  # Default value
        "MoistureDetected": 1 if sensor_data.get('humidity', 50) > 60 else 0,
        "CoolingSystem": "Active"
    }


@app.route('/ml/predict', methods=['GET'])
def get_ml_prediction():
    """Get ML prediction for the latest sensor data"""
    try:
        # Fetch latest sensor reading
        latest = sensor_collection.find_one(sort=[('timestamp', -1)])

        if not latest:
            return jsonify({
                'success': True,
                'empty_database': True,
                'message': 'Database is empty. Start the sensor server to generate data.',
                'ml_prediction': None,
                'sensor_data': None
            }), 200

        # Convert sensor data to ML format
        ml_input = convert_sensor_to_ml_format(latest)

        # Call ML server for prediction
        response = requests.post(
            f'{ML_SERVER_URL}/api/predict', json=ml_input, timeout=5)

        if response.status_code == 200:
            ml_result = response.json()

            # Format response to match frontend expectations
            return jsonify({
                'success': True,
                'sensor_data': {
                    'sensor_id': latest.get('sensor_id'),
                    'humidity': latest.get('humidity'),
                    'temperature': latest.get('temperature'),
                    'core_temp': latest.get('core_temp'),
                    'voltage': latest.get('voltage'),
                    'current': latest.get('current'),
                    'soc': latest.get('soc'),
                    'timestamp': latest.get('timestamp').isoformat() if isinstance(latest.get('timestamp'), datetime) else latest.get('timestamp')
                },
                'ml_prediction': {
                    'prediction': ml_result.get('prediction'),
                    'solution': ml_result.get('solution'),
                    'confidence': ml_result.get('confidence'),
                    'reliability': ml_result.get('reliability'),
                    'probabilities': ml_result.get('probabilities', {}),
                    'model_accuracy': ml_result.get('model_accuracy', 0.84)
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'ML server returned error'
            }), 500

    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': True,
            'ml_server_error': True,
            'message': 'ML server is not running. Please start it on port 8000.',
            'ml_prediction': None,
            'sensor_data': latest if latest else None
        }), 200
    except Exception as e:
        return jsonify({
            'success': True,
            'error': True,
            'message': f'Unexpected error: {str(e)}',
            'ml_prediction': None,
            'sensor_data': None
        }), 200


@app.route('/ml/analyze', methods=['POST'])
def analyze_sensor_data():
    """Analyze specific sensor data with ML model"""
    try:
        sensor_data = request.get_json()

        if not sensor_data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Convert to ML format
        ml_input = convert_sensor_to_ml_format(sensor_data)

        # Call ML server
        response = requests.post(
            f'{ML_SERVER_URL}/api/predict', json=ml_input, timeout=5)

        if response.status_code == 200:
            ml_result = response.json()
            return jsonify({
                'success': True,
                'ml_prediction': ml_result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'ML prediction failed'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/ml/analyse', methods=['GET'])
def ml_analyse():
    """Analyze all MongoDB data with ML server and return comprehensive results"""
    try:
        # Get limit parameter (default 100)
        limit = request.args.get('limit', 100, type=int)

        # Fetch readings from MongoDB
        readings = list(sensor_collection.find().sort(
            'timestamp', -1).limit(limit))

        if not readings:
            return jsonify({
                'success': False,
                'message': 'No sensor data available in MongoDB'
            }), 404

        results = []
        predictions_count = {}
        total_confidence = 0
        failed_predictions = 0

        for reading in readings:
            ml_input = convert_sensor_to_ml_format(reading)

            try:
                # Post to ML server
                response = requests.post(
                    f'{ML_SERVER_URL}/api/predict', json=ml_input, timeout=10)

                if response.status_code == 200:
                    ml_result = response.json()
                    prediction = ml_result.get('prediction')
                    confidence = ml_result.get('confidence', 0)

                    # Count prediction types
                    predictions_count[prediction] = predictions_count.get(
                        prediction, 0) + 1
                    total_confidence += confidence

                    results.append({
                        'sensor_id': reading.get('sensor_id'),
                        'timestamp': reading.get('timestamp').isoformat() if isinstance(reading.get('timestamp'), datetime) else reading.get('timestamp'),
                        'sensor_data': {
                            'temperature': reading.get('temperature'),
                            'humidity': reading.get('humidity'),
                            'core_temp': reading.get('core_temp'),
                            'voltage': reading.get('voltage'),
                            'current': reading.get('current'),
                            'soc': reading.get('soc'),
                            'battery_location': reading.get('battery_location')
                        },
                        'ml_analysis': {
                            'prediction': prediction,
                            'solution': ml_result.get('solution'),
                            'confidence': confidence,
                            'reliability': ml_result.get('reliability'),
                            'probabilities': ml_result.get('probabilities', {})
                        }
                    })
                else:
                    failed_predictions += 1
            except Exception as e:
                failed_predictions += 1
                continue

        # Calculate comprehensive statistics
        successful_predictions = len(results)
        avg_confidence = total_confidence / \
            successful_predictions if successful_predictions > 0 else 0
        most_common_prediction = max(predictions_count.items(), key=lambda x: x[1])[
            0] if predictions_count else 'Unknown'

        return jsonify({
            'success': True,
            'summary': {
                'total_records_fetched': len(readings),
                'successful_predictions': successful_predictions,
                'failed_predictions': failed_predictions,
                'ml_server_url': ML_SERVER_URL
            },
            'statistics': {
                'most_common_prediction': most_common_prediction,
                'prediction_distribution': predictions_count,
                'average_confidence': round(avg_confidence, 2),
                'confidence_range': {
                    'min': round(min((r['ml_analysis']['confidence'] for r in results), default=0), 2),
                    'max': round(max((r['ml_analysis']['confidence'] for r in results), default=0), 2)
                }
            },
            'detailed_results': results
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/ml/batch-analyze', methods=['GET'])
def batch_analyze():
    """Analyze last 10 sensor readings and return ML insights with trends"""
    try:
        # Fetch last 10 readings
        readings = list(sensor_collection.find().sort(
            'timestamp', -1).limit(10))

        if not readings:
            return jsonify({
                'success': False,
                'message': 'No sensor data available'
            }), 404

        results = []
        predictions_count = {}

        for reading in readings:
            ml_input = convert_sensor_to_ml_format(reading)

            try:
                response = requests.post(
                    f'{ML_SERVER_URL}/api/predict', json=ml_input, timeout=5)
                if response.status_code == 200:
                    ml_result = response.json()
                    prediction = ml_result.get('prediction')

                    # Count prediction types
                    predictions_count[prediction] = predictions_count.get(
                        prediction, 0) + 1

                    results.append({
                        'sensor_id': reading.get('sensor_id'),
                        'timestamp': reading.get('timestamp').isoformat() if isinstance(reading.get('timestamp'), datetime) else reading.get('timestamp'),
                        'prediction': prediction,
                        'solution': ml_result.get('solution'),
                        'confidence': ml_result.get('confidence'),
                        'reliability': ml_result.get('reliability'),
                        'core_temp': reading.get('core_temp'),
                        'humidity': reading.get('humidity'),
                        'soc': reading.get('soc')
                    })
            except Exception as e:
                continue

        # Calculate trends
        avg_confidence = sum(r['confidence']
                             for r in results) / len(results) if results else 0
        most_common_prediction = max(predictions_count.items(), key=lambda x: x[1])[
            0] if predictions_count else 'Unknown'

        return jsonify({
            'success': True,
            'count': len(results),
            'analyses': results,
            'trends': {
                'most_common_prediction': most_common_prediction,
                'prediction_distribution': predictions_count,
                'average_confidence': round(avg_confidence, 2),
                'total_analyzed': len(readings)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("="*60)
    print("Root Server - EV Battery Monitoring Dashboard")
    print("="*60)
    print(f"Port: {PORT}")
    print(f"CORS Origins: {CORS_ORIGINS}")
    print(f"ML Server: {ML_SERVER_URL}")
    print(f"MongoDB: {DATABASE_NAME}.{COLLECTION_NAME}")
    print(f"Dashboard: http://localhost:{PORT}")
    print("="*60)
    print()

    # Test MongoDB connection
    try:
        client.admin.command('ping')
        print("✓ MongoDB connection successful!")
        print()
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("Please check your MongoDB connection")
        print()

    # Start Flask server
    app.run(port=PORT, debug=True)
