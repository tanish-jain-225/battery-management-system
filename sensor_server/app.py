# Importing Required Libraries
from flask import Flask, jsonify
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Standard Libraries
import os
import random
import time
import threading

# Load environment variables
load_dotenv()

# Global Configuration Variables
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'ev_battery_monitoring')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'battery_sensors')
PORT = int(os.getenv('PORT', 5500))
INTERVAL = int(os.getenv('INTERVAL', 1))  # Interval in seconds

# Flask App
app = Flask(__name__)

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

# Global stats
stats = {
    'total_posted': 0,
    'start_time': None,
    'last_posted': None,
    'status': 'running'
}


def generate_sensor_data():
    """
    Generate a single random sensor data reading
    Returns: Single sensor data object
    """
    return {
        "sensor_id": f"battery_{random.randint(1, 10):03d}",
        "humidity": round(random.uniform(30, 70), 2),
        "temperature": round(random.uniform(20, 50), 2),
        "heat_index": round(random.uniform(22, 55), 2),
        "battery_location": f"cell_pack_{random.randint(1, 4)}",
        "ambient_temp": round(random.uniform(18, 28), 2),
        "surface_temp": round(random.uniform(25, 45), 2),
        "core_temp": round(random.uniform(30, 50), 2),
        "voltage": round(random.uniform(3.0, 4.2), 2),
        "current": round(random.uniform(0.5, 3.5), 2),
        "soc": random.randint(0, 100),
        "timestamp": datetime.utcnow()
    }


def auto_sensor_data_system():
    """
    Continuously generates sensor data one by one and posts to MongoDB every second.
    """
    global stats
    stats['start_time'] = datetime.utcnow()

    print("="*60)
    print("EV Battery Sensor Data Generator")
    print("="*60)
    print(f"MongoDB URI: {MONGO_URI}")
    print(f"Database: {DATABASE_NAME}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Interval: {INTERVAL} second(s)")
    print("="*60)
    print("Starting continuous sensor data generation (one per second)...")
    print()

    while True:
        try:
            # Generate single sensor data
            sensor_data = generate_sensor_data()

            # Print data being posted
            timestamp = datetime.utcnow().strftime('%H:%M:%S')
            print(f"[{timestamp}] Posting Data:")
            print(f"  {sensor_data}")

            # Insert into MongoDB
            result = sensor_collection.insert_one(sensor_data)

            # Update stats
            stats['total_posted'] += 1
            stats['last_posted'] = sensor_data

            # Confirm insertion
            print(
                f"  ✓ Successfully posted to MongoDB - ID: {result.inserted_id}")
            print()

        except Exception as e:
            print(f"[ERROR] Failed to post data: {e}")
            print()

        # Wait 1 second before next insertion
        time.sleep(INTERVAL)


@app.route('/', methods=['GET'])
def server_status():
    """Show server status and statistics"""
    uptime = None
    if stats['start_time']:
        uptime_seconds = (datetime.utcnow() -
                          stats['start_time']).total_seconds()
        uptime = f"{int(uptime_seconds)} seconds"

    last_data = None
    if stats['last_posted']:
        last_data = {
            'sensor_id': stats['last_posted']['sensor_id'],
            'humidity': stats['last_posted']['humidity'],
            'temperature': stats['last_posted']['temperature'],
            'core_temp': stats['last_posted']['core_temp'],
            'soc': stats['last_posted']['soc'],
            'timestamp': stats['last_posted']['timestamp'].isoformat()
        }

    return jsonify({
        'server': 'EV Battery Sensor Data Generator',
        'status': stats['status'],
        'port': PORT,
        'uptime': uptime,
        'database': {
            'uri': MONGO_URI,
            'database': DATABASE_NAME,
            'collection': COLLECTION_NAME
        },
        'statistics': {
            'total_posted': stats['total_posted'],
            'interval': f"{INTERVAL} second(s)",
            'last_posted': last_data
        }
    })


if __name__ == '__main__':
    print("="*60)
    print("EV Battery Sensor Data Generator")
    print("="*60)
    print(f"Port: {PORT}")
    print(f"Generation Interval: {INTERVAL} second(s)")
    print(f"Server URL: http://localhost:{PORT}")
    print(f"MongoDB: {DATABASE_NAME}.{COLLECTION_NAME}")
    print("="*60)
    print()

    # Test MongoDB connection
    try:
        client.admin.command('ping')
        print("✓ MongoDB connection successful!")
        print()
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("Please check your MONGO_URI in .env file")
        exit(1)

    # Start sensor data generation in background thread
    sensor_thread = threading.Thread(
        target=auto_sensor_data_system, daemon=True)
    sensor_thread.start()

    # Start Flask server
    try:
        app.run(port=PORT, debug=True)
    except KeyboardInterrupt:
        print("\n" + "="*60)
        print("Sensor data generation stopped by user")
        print("="*60)
