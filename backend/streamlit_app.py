import streamlit as st
import requests
from PIL import Image
import io

st.title("🚦 IntelliTraffic - Streamlit Frontend")
st.write("Upload a traffic image to analyze lane-wise vehicle detection using YOLOv8.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Send image to Flask backend
    files = {"image": uploaded_file.getvalue()}
    try:
        response = requests.post("http://127.0.0.1:5000/api/traffic", files={"image": uploaded_file})
        if response.status_code == 200:
            result = response.json()

            st.subheader("🔢 Lane Results")
            for lane in ['lane_A', 'lane_B', 'lane_C', 'lane_D']:
                lane_info = result[lane]
                st.markdown(f"**{lane}:** {lane_info['vehicle_count']} vehicles, Signal: {lane_info['signal']}, Time left: {lane_info['time_left']}s")

            st.subheader("📊 Object Counts")
            st.json(result["object_counts"])

            st.subheader("🚨 Emergency Detection")
            if result["emergency_detected"]:
                st.error(f"Emergency vehicle detected in Lane {result['emergency_lane']}")
            else:
                st.success("No emergency vehicle detected.")

            st.caption(f"Detection Confidence: {round(result['accuracy_rate']*100, 2)}%")
        else:
            st.error("Failed to get a response from the backend.")
    except Exception as e:
        st.error(f"Error: {e}")
