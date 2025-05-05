// --- CONFIGURATION ---
const API_URL = 'http://127.0.0.1:5000/api/traffic';  // URL for the Flask backend

// --- CHARTS ---
let lineChart;
const laneIds = ['A', 'B', 'C', 'D'];
let timeLabels = [];
let history = {
    A: [],
    B: [],
    C: [],
    D: []
};

function initLineChart() {
    const ctx = document.getElementById('barChart').getContext('2d');
    lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeLabels,
            datasets: [
                { label: 'Lane A', data: history.A, borderColor: '#28a745', fill: false },
                { label: 'Lane B', data: history.B, borderColor: '#dc3545', fill: false },
                { label: 'Lane C', data: history.C, borderColor: '#007bff', fill: false },
                { label: 'Lane D', data: history.D, borderColor: '#ffc107', fill: false }
            ]
        },
        options: { responsive: true }
    });
}

function updateLineChart(a, b, c, d) {
    const now = new Date().toLocaleTimeString();
    timeLabels.push(now);
    history.A.push(a);
    history.B.push(b);
    history.C.push(c);
    history.D.push(d);

    // Keep only the last 20 points for clarity
    if (timeLabels.length > 20) {
        timeLabels.shift();
        history.A.shift();
        history.B.shift();
        history.C.shift();
        history.D.shift();
    }

    lineChart.data.labels = timeLabels;
    lineChart.data.datasets[0].data = history.A;
    lineChart.data.datasets[1].data = history.B;
    lineChart.data.datasets[2].data = history.C;
    lineChart.data.datasets[3].data = history.D;
    lineChart.update();
}

function setSignalStatus(elem, status) {
  elem.classList.remove('green', 'red', 'yellow');
  elem.classList.add(status.toLowerCase());
}

function updatePanel(lane, data) {
  document.getElementById('vehicle' + lane).textContent = data.vehicle_count;
  document.getElementById('timer' + lane).textContent = data.time_left;
  const statusElem = document.getElementById('status' + lane);
  statusElem.textContent = data.signal;
  statusElem.className = 'badge ' + (data.signal === 'GREEN' ? 'bg-success' : data.signal === 'YELLOW' ? 'bg-warning text-dark' : 'bg-danger');
  const signalElem = document.getElementById('signal' + lane);
  setSignalStatus(signalElem, data.signal);
}

// --- IMAGE UPLOAD AND DASHBOARD UPDATE ---

const imageInput = document.getElementById('image-upload');
if (imageInput) {
    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('image', file);

        // Show uploaded image
        const imgElem = document.getElementById('uploaded-image');
        imgElem.src = URL.createObjectURL(file);
        imgElem.style.display = 'block';

        fetch('http://127.0.0.1:5000/api/traffic', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            // Update lane info
            document.getElementById('vehicleA').textContent = data.lane_A.vehicle_count;
            document.getElementById('vehicleB').textContent = data.lane_B.vehicle_count;
            document.getElementById('vehicleC').textContent = data.lane_C.vehicle_count;
            document.getElementById('vehicleD').textContent = data.lane_D.vehicle_count;

            document.getElementById('timerA').textContent = data.lane_A.time_left;
            document.getElementById('timerB').textContent = data.lane_B.time_left;
            document.getElementById('timerC').textContent = data.lane_C.time_left;
            document.getElementById('timerD').textContent = data.lane_D.time_left;

            document.getElementById('statusA').textContent = data.lane_A.signal;
            document.getElementById('statusB').textContent = data.lane_B.signal;
            document.getElementById('statusC').textContent = data.lane_C.signal;
            document.getElementById('statusD').textContent = data.lane_D.signal;

            // Update lane signal color
            document.getElementById('signalA').style.background = data.lane_A.signal === 'GREEN' ? 'green' : (data.lane_A.signal === 'YELLOW' ? 'yellow' : 'red');
            document.getElementById('signalB').style.background = data.lane_B.signal === 'GREEN' ? 'green' : (data.lane_B.signal === 'YELLOW' ? 'yellow' : 'red');
            document.getElementById('signalC').style.background = data.lane_C.signal === 'GREEN' ? 'green' : (data.lane_C.signal === 'YELLOW' ? 'yellow' : 'red');
            document.getElementById('signalD').style.background = data.lane_D.signal === 'GREEN' ? 'green' : (data.lane_D.signal === 'YELLOW' ? 'yellow' : 'red');

            // Update detected objects
            let objInfo = "Detected Objects:<br>";
            for (let [key, value] of Object.entries(data.object_counts)) {
                objInfo += `${key.charAt(0).toUpperCase() + key.slice(1)}: ${value} `;
            }
            document.getElementById('object-info').innerHTML = objInfo;
        });
    });
}

const useSampleBtn = document.getElementById('use-sample-btn');
if (useSampleBtn) {
    useSampleBtn.addEventListener('click', async function() {
        try {
            const response = await fetch(API_URL, {
                method: 'POST'
                // No body, so backend will use sample data
            });
            const data = await response.json();
            updateDashboard(data);
        } catch (error) {
            alert('Failed to fetch sample data from backend.');
        }
    });
}

function updateDashboard(data) {
    console.log("API Response:", data);
    laneIds.forEach(lane => {
        updatePanel(lane, data['lane_' + lane]);
    });
    updateLineChart(
        data.lane_A.vehicle_count,
        data.lane_B.vehicle_count,
        data.lane_C.vehicle_count,
        data.lane_D.vehicle_count
    );
    // Optionally, display a message about the most crowded lane
    const messageElem = document.getElementById('result-message');
    const counts = laneIds.map(lane => data['lane_' + lane].vehicle_count);
    const maxCount = Math.max(...counts);
    const maxLanes = laneIds.filter((lane, idx) => counts[idx] === maxCount);
    if (maxLanes.length === 1) {
        messageElem.textContent = `Lane ${maxLanes[0]} has the most vehicles. Consider clearing Lane ${maxLanes[0]} first.`;
    } else {
        messageElem.textContent = `Lanes ${maxLanes.join(', ')} have the same (highest) vehicle count.`;
    }
    if (data.emergency_detected) {
        messageElem.textContent = 
            `Emergency vehicle detected in Lane ${data.emergency_lane}. Please clear this lane!`;
    }

    // --- Lane summary display ---
    const summaryElem = document.getElementById('lane-summary');
    let summaryHtml = '<h5>Lane Signal Status:</h5><div style="display:flex;justify-content:center;gap:20px;">';
    laneIds.forEach(lane => {
        const signal = data['lane_' + lane].signal;
        let colorClass = '';
        if (signal === 'GREEN') colorClass = 'text-success';
        else if (signal === 'RED') colorClass = 'text-danger';
        else if (signal === 'YELLOW') colorClass = 'text-warning';
        summaryHtml += `<div><b>Lane ${lane}:</b> <span class="${colorClass}">${signal}</span></div>`;
    });
    summaryHtml += '</div>';
    summaryElem.innerHTML = summaryHtml;

    const objectInfoElem = document.getElementById('object-info');
    if (data.object_counts && Object.keys(data.object_counts).length > 0) {
        let infoHtml = '<h5>Detected Objects:</h5><div style="display:flex;justify-content:center;gap:20px;">';
        for (const [obj, count] of Object.entries(data.object_counts)) {
            infoHtml += `<div><b>${obj.charAt(0).toUpperCase() + obj.slice(1)}:</b> ${count}</div>`;
        }
        infoHtml += '</div>';
        objectInfoElem.innerHTML = infoHtml;
    } else {
        objectInfoElem.innerHTML = '<em>No objects detected.</em>';
    }
}

// --- INIT ---
window.onload = function() {
    initLineChart();
    // Start auto-cycling sample data every 2 seconds
    setInterval(fetchSampleData, 2000);
};

async function fetchSampleData() {
    try {
        const response = await fetch(API_URL, { method: 'POST' });
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        // Optionally show error
    }
}

async function updateCentralLED() {
  try {
    // Replace with the actual image upload logic if needed
    // Here, we just fetch the latest signal status
    const response = await fetch('http://127.0.0.1:5000/api/traffic', {
      method: 'POST',
      // If your API expects an image, you need to send FormData with an image file here
      // For demo, you can skip body or use a test image
    });
    const data = await response.json();
    // Assume lane_A is the main signal for central LED
    const signal = data.lane_A.signal || "RED";
    const led = document.getElementById('central-led');
    led.classList.remove('red', 'green');
    led.classList.add(signal.toLowerCase());
  } catch (e) {
    // On error, set to red for safety
    const led = document.getElementById('central-led');
    led.classList.remove('green');
    led.classList.add('red');
  }
}

// Call every 5 seconds (adjust as needed)
setInterval(updateCentralLED, 5000);
// Call once on page load
updateCentralLED();

// Theme toggle logic
const themeToggle = document.getElementById('themeToggle');
function setTheme(night) {
  if (night) {
    document.body.classList.remove('day-theme');
    document.body.classList.add('night-theme');
    themeToggle.checked = true;
    themeToggle.nextElementSibling.textContent = "Night Mode";
  } else {
    document.body.classList.add('day-theme');
    document.body.classList.remove('night-theme');
    themeToggle.checked = false;
    themeToggle.nextElementSibling.textContent = "Day Mode";
  }
}
themeToggle.addEventListener('change', function() {
  setTheme(this.checked);
});
// Default to day mode
setTheme(false);

// Signal animation for demo (if backend doesn't provide real-time signal)
function cycleSignal(id) {
    const el = document.getElementById(id);
    let states = ['red', 'yellow', 'green'];
    let idx = 0;
    setInterval(() => {
        el.className = 'signal-indicator ' + states[idx];
        idx = (idx + 1) % states.length;
    }, 2000);
}
laneIds.forEach(lane => cycleSignal('signal' + lane));
