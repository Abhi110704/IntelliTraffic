# Import necessary libraries for the backend
from flask import Flask, request, jsonify
import os
from PIL import Image
import numpy as np
import random
from ultralytics import YOLO
import requests
from flask_cors import CORS

# Create the Flask web application
app = Flask(__name__)
CORS(app)  # Allow requests from other origins (for frontend-backend connection)

# Get the path of the current folder where this script is located
BASE_PATH = os.path.dirname(os.path.realpath(__file__))
# Name of the YOLOv8 model file we want to use
MODEL_FILENAME = 'yolov8n.pt'
# Full path to the model file
MODEL_PATH = os.path.join(BASE_PATH, 'models', MODEL_FILENAME)

# Make sure the 'models' folder exists, create it if it doesn't
os.makedirs(os.path.join(BASE_PATH, 'models'), exist_ok=True)

# Official download link for the YOLOv8n model
YOLOV8_URL = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"

# Download the YOLOv8 model if it's not already present in the models folder
def download_model_if_needed(model_path):
    if not os.path.exists(model_path):
        print(f"Model file not found at {model_path}. Downloading YOLOv8n model...")
        response = requests.get(YOLOV8_URL, stream=True)
        if response.status_code == 200:
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Model downloaded successfully.")
        else:
            raise Exception(f"Failed to download model. Status code: {response.status_code}")

download_model_if_needed(MODEL_PATH)

# Some example dummy data sets for testing or when no image is provided
SAMPLE_DUMMY_DATA = [
    {
        "lane_A": {"vehicle_count": 0, "signal": "GREEN", "time_left": 25},
        "lane_B": {"vehicle_count": 0, "signal": "RED", "time_left": 40},
        "lane_C": {"vehicle_count": 2, "signal": "YELLOW", "time_left": 10},
        "lane_D": {"vehicle_count": 4, "signal": "GREEN", "time_left": 30}
    },
    {
        "lane_A": {"vehicle_count": 3, "signal": "RED", "time_left": 50},
        "lane_B": {"vehicle_count": 5, "signal": "GREEN", "time_left": 20},
        "lane_C": {"vehicle_count": 1, "signal": "YELLOW", "time_left": 15},
        "lane_D": {"vehicle_count": 2, "signal": "RED", "time_left": 60}
    },
    {
        "lane_A": {"vehicle_count": 6, "signal": "YELLOW", "time_left": 12},
        "lane_B": {"vehicle_count": 2, "signal": "RED", "time_left": 35},
        "lane_C": {"vehicle_count": 4, "signal": "GREEN", "time_left": 28},
        "lane_D": {"vehicle_count": 0, "signal": "GREEN", "time_left": 30}
    },
    {
        "lane_A": {"vehicle_count": 1, "signal": "GREEN", "time_left": 40},
        "lane_B": {"vehicle_count": 3, "signal": "YELLOW", "time_left": 18},
        "lane_C": {"vehicle_count": 5, "signal": "RED", "time_left": 55},
        "lane_D": {"vehicle_count": 2, "signal": "GREEN", "time_left": 25}
    }
]

# This function creates a random but realistic traffic scenario for all lanes
# It is used when no image is provided, so the frontend can still show data
# The vehicle counts are kept within a realistic range
# It also assigns signals (RED, YELLOW, GREEN) based on which lanes have the most vehicles
# Returns both the lane data and the total object counts

def generate_random_sample():
    vehicle_types = ['car', 'bus', 'truck', 'motorcycle', 'person']
    lane_counts = []
    lane_objects = []
    for _ in range(4):
        lane_obj = {}
        total = 0
        for vtype in vehicle_types:
            count = random.randint(0, 20)  # up to 20 of each type per lane for realistic values
            lane_obj[vtype] = count
            total += count
        lane_counts.append(total)
        lane_objects.append(lane_obj)
    times = [random.randint(10, 60) for _ in range(4)]
    sample = {
        "lane_A": {"vehicle_count": lane_counts[0], "signal": "RED", "time_left": times[0]},
        "lane_B": {"vehicle_count": lane_counts[1], "signal": "RED", "time_left": times[1]},
        "lane_C": {"vehicle_count": lane_counts[2], "signal": "RED", "time_left": times[2]},
        "lane_D": {"vehicle_count": lane_counts[3], "signal": "RED", "time_left": times[3]}
    }
    # Decide which lanes get GREEN and YELLOW signals based on vehicle counts
    lane_counts_with_index = list(enumerate(lane_counts))
    sorted_lanes = sorted(lane_counts_with_index, key=lambda x: x[1], reverse=True)
    signals = ['RED'] * 4
    if sorted_lanes[0][1] > 0:
        signals[sorted_lanes[0][0]] = 'GREEN'
    if sorted_lanes[1][1] > 0:
        signals[sorted_lanes[1][0]] = 'YELLOW'
    sample['lane_A']['signal'] = signals[0]
    sample['lane_B']['signal'] = signals[1]
    sample['lane_C']['signal'] = signals[2]
    sample['lane_D']['signal'] = signals[3]
    # Calculate total object counts for all lanes
    object_counts = {vtype: sum(lane[vtype] for lane in lane_objects) for vtype in vehicle_types}
    return sample, object_counts

# Load the YOLOv8 model only once when the app starts, so it's fast for every request
# If loading fails, print the error and return None

def load_model():
    try:
        model = YOLO(MODEL_PATH)
        print("YOLOv8 model loaded successfully.")
        return model
    except Exception as e:
        print(f"Error loading YOLOv8 model: {e}")
        return None

model = load_model()  # Load the model once when the app starts

# This is the main API endpoint for processing traffic images
# It accepts a POST request with an image file (key: 'image')
# If an image is provided, it runs YOLOv8 detection and assigns signals
# If no image is provided, it returns random sample data
# The response includes lane info, detected objects, and emergency vehicle info if found

@app.route('/api/traffic', methods=['POST'])
def process_frame():
    try:
        file = request.files.get('image')
        if file and model is not None:
            img = Image.open(file.stream)
            results = model(img, conf=0.25)
            if isinstance(results, list) and len(results) > 0:
                result = results[0]
                if hasattr(result, 'pandas') and hasattr(result.pandas(), 'xyxy'):
                    df = result.pandas().xyxy[0]
                else:
                    df = None
            else:
                df = None
            width = img.width if hasattr(img, 'width') else 640
            lane_counts = [0, 0, 0, 0]
            if df is not None:
                for _, row in df.iterrows():
                    x_center = (row['xmin'] + row['xmax']) / 2
                    # Divide the image into 4 vertical lanes and count objects in each
                    if x_center < width * 0.25:
                        lane_counts[0] += 1
                    elif x_center < width * 0.5:
                        lane_counts[1] += 1
                    elif x_center < width * 0.75:
                        lane_counts[2] += 1
                    else:
                        lane_counts[3] += 1
            else:
                lane_counts = [0, 0, 0, 0]
            # Assign signals based on which lanes have the most vehicles
            lane_counts_with_index = list(enumerate(lane_counts))
            sorted_lanes = sorted(lane_counts_with_index, key=lambda x: x[1], reverse=True)
            signals = ['RED'] * 4
            if sorted_lanes[0][1] > 0:
                signals[sorted_lanes[0][0]] = 'GREEN'
            if sorted_lanes[1][1] > 0:
                signals[sorted_lanes[1][0]] = 'YELLOW'
            times = [30, 45, 20, 25]  # Example time left for each lane
            avg_confidence = 0.0
            if df is not None and not df.empty and 'confidence' in df.columns:
                avg_confidence = float(df['confidence'].mean())
            # Check for emergency vehicles in the detected objects
            emergency_detected = False
            emergency_lane = None
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    if row['name'] in ['ambulance', 'police car', 'fire truck']:
                        emergency_detected = True
                        # Find which lane the emergency vehicle is in
                        x_center = (row['xmin'] + row['xmax']) / 2
                        if x_center < width * 0.25:
                            emergency_lane = 'A'
                        elif x_center < width * 0.5:
                            emergency_lane = 'B'
                        elif x_center < width * 0.75:
                            emergency_lane = 'C'
                        else:
                            emergency_lane = 'D'
                        break
            # Count how many of each object type were detected
            object_counts = {}
            if df is not None and not df.empty and 'name' in df.columns:
                for obj_name in df['name']:
                    object_counts[obj_name] = object_counts.get(obj_name, 0) + 1
            print("Object counts to frontend:", object_counts)
            return jsonify({
                "lane_A": {"vehicle_count": lane_counts[0], "signal": signals[0], "time_left": times[0]},
                "lane_B": {"vehicle_count": lane_counts[1], "signal": signals[1], "time_left": times[1]},
                "lane_C": {"vehicle_count": lane_counts[2], "signal": signals[2], "time_left": times[2]},
                "lane_D": {"vehicle_count": lane_counts[3], "signal": signals[3], "time_left": times[3]},
                "accuracy_rate": avg_confidence,
                "emergency_detected": emergency_detected,
                "emergency_lane": emergency_lane,
                "object_counts": object_counts
            })
        elif not file and model is not None:
            # If no image is sent, return a random sample for testing or demo
            sample, object_counts = generate_random_sample()
            print("Using sample data:", sample)
            print("Object counts to frontend:", object_counts)
            return jsonify({**sample, "object_counts": object_counts})
        else:
            # If the model didn't load or something else went wrong
            return jsonify({"error": "Model not loaded or image not provided."}), 400
    except Exception as e:
        print(f"Error in /api/traffic: {e}")
        return jsonify({"error": str(e)}), 500

# A simple route to show a welcome message or link to the app
@app.route('/')
def serve_index():
    return 'Go to <a href="http://127.0.0.1:5000">http://127.0.0.1:5000</a> to see the app'

# Start the Flask app in debug mode when running this script directly
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
