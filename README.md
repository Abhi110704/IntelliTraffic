# 🚦 IntelliTraffic - Intelligent Traffic Signal Control System

IntelliTraffic is a smart traffic management application that uses real-time computer vision (via YOLOv8) and Python (Flask) to analyze live vehicle data from traffic feeds and dynamically assign signal priorities across multiple lanes. This helps optimize traffic flow and reduce congestion, especially in urban settings.

---

## 🌟 Features

- 🔍 Real-time object detection using YOLOv8  
- 📸 Accepts uploaded traffic camera images  
- 🛑 Assigns RED, GREEN, YELLOW signals to each lane based on vehicle count  
- 🚑 Detects emergency vehicles (ambulance, police car, fire truck) and responds accordingly  
- 📊 Displays detected object types and counts  
- 🌐 Simple frontend interface connected via REST API  
- 🧪 Returns realistic sample data if no image is provided  

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/IntelliTraffic.git
cd IntelliTraffic
```

### 2. Install Python Dependencies

Make sure you have Python 3.8+ installed, then run:

```bash
pip install -r requirements.txt
```

### 3. Start the Backend Server

```bash
python app.py
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧠 How It Works

1. Frontend sends an image to the `/api/traffic` endpoint.  
2. YOLOv8 detects objects and assigns them to one of four lanes.  
3. Based on vehicle counts:
   - Most crowded → GREEN  
   - Second most → YELLOW  
   - Others → RED  
4. Emergency vehicles can override normal logic.  
5. Backend returns signal and object data for frontend display.  

---

## 🧪 Demo Without Image

If no image is provided, the backend returns realistic random traffic data to simulate real conditions.

---

## 📷 YOLOv8 Model Notes

- Uses `yolov8n.pt` model (auto-downloaded if missing).  
- To train your own model:
  - Use `vehicle_dataset.yaml`
  - Follow [Ultralytics YOLOv8 Docs](https://docs.ultralytics.com)

---

## 📌 Dependencies

```
flask
flask-cors
torch
opencv-python
pillow
ultralytics
```

Install them using:

```bash
pip install -r requirements.txt
```

---

## 📦 Deployment (Render)

### Steps:

1. **Push to GitHub**  
   Ensure your project is fully committed.

2. **Create `requirements.txt`**  
   Include all Python dependencies listed above.

   Or auto-generate:
   ```bash
   pip freeze > requirements.txt
   ```

3. **(Optional) Add `render.yaml`**  

   ```yaml
   services:
     - type: web
       name: intellitraffic
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: python app.py
   ```

4. **Deploy on [Render](https://render.com)**  
   - Click "New Web Service"  
   - Connect GitHub repo  
   - Set:
     - Build command: `pip install -r requirements.txt`  
     - Start command: `python app.py`  
     - Environment: Python 3.x  

---

## 🤝 Contributions

Pull requests are welcome! For major changes, open an issue first to discuss what you want to modify.

---

## 📄 License

This project is open-source under the **MIT License**.

---
