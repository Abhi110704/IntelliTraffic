# 🚦 IntelliTraffic - Intelligent Traffic Signal Control System

**IntelliTraffic** is a smart traffic management system that uses real-time computer vision (YOLOv8) and Python (Flask or Streamlit) to analyze live vehicle data and assign traffic signals dynamically. It helps optimize urban traffic flow and reduce congestion efficiently.

---

## 🌟 Features

- 🔍 Real-time object detection using YOLOv8  
- 📸 Upload traffic camera images or use fallback sample data  
- 🚥 Dynamic traffic signal assignment (RED, YELLOW, GREEN)  
- 🚑 Emergency vehicle detection (ambulance, police car, fire truck)  
- 📊 Lane-wise vehicle count and object type summary  
- 🌐 Simple HTML frontend via Flask + optional Streamlit dashboard  
- 🧠 Intelligent fallback logic when no image is uploaded  

---

## 🗂 Project Structure

```
IntelliTraffic/
├── backend/
│   ├── app.py               # Flask backend
│   ├── requirements.txt     # Backend dependencies
│   ├── streamlit_app.py     # Optional Streamlit frontend
│   └── models/
│       └── yolov8n.pt       # YOLOv8n model
├── frontend/
│   ├── index.html           # Main frontend UI
│   ├── script.js
│   └── style.css
├── README.md
└── Sample.jpeg
```

---

## 🚀 Getting Started (Local)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/IntelliTraffic.git
cd IntelliTraffic/backend
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scriptsctivate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Flask Backend

```bash
python app.py
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 5. View Frontend

Open `frontend/index.html` directly in your browser **OR** use Flask APIs to power it with backend results.

---

## 🌈 Optional: Streamlit Interface

To run the Streamlit dashboard:

```bash
streamlit run streamlit_app.py
```

Visit: [http://localhost:8501](http://localhost:8501)

---

## 🧠 How It Works

1. Frontend or Streamlit sends an image to the backend.
2. YOLOv8 detects vehicle objects in 4 vertical lanes.
3. Signals are assigned:
   - Highest vehicle count → GREEN  
   - Second highest → YELLOW  
   - Remaining → RED
4. Emergency vehicles can override normal logic.
5. The response includes signals, object counts, and confidence.

---

## 🧪 No Image? No Problem!

If no image is uploaded, the backend returns a simulated traffic data sample for demo/testing.

---

## 📷 Model Info

- Default model: `yolov8n.pt` (auto-downloads if missing)
- You can replace it with a trained model in the `models/` folder
- To train your own:
  - Use `vehicle_dataset.yaml`
  - Follow [Ultralytics YOLOv8 Docs](https://docs.ultralytics.com)

---

## 📦 Deployment (Render.com)

### ✅ Quick Steps

1. **Push your project to GitHub**  
2. **Create `requirements.txt` (already present)**  
3. **Add `render.yaml`** (optional):

```yaml
services:
  - type: web
    name: intellitraffic
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
```

4. **Go to [Render](https://render.com)**  
   - Click "New Web Service"  
   - Connect your GitHub repo  
   - Set:
     - Build command: `pip install -r requirements.txt`
     - Start command: `python app.py`
     - Runtime: Python 3.x

---

## 📌 Dependencies

```text
flask
flask-cors
torch
opencv-python
pillow
ultralytics
```

To install:

```bash
pip install -r requirements.txt
```

---

## 🙌 Contributions

Pull requests are welcome. If you'd like to propose major changes, please open an issue first to discuss.

---

## 📄 License

Licensed under the **MIT License** – feel free to use and modify it.

---
