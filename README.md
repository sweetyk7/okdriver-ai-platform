# OKDriver AI Platform 🚙📷

A high-performance, ultra-low latency fleet monitoring dashboard built with React, FastAPI, WebRTC, and MediaMTX.

OKDriver allows you to turn ordinary Android smartphones into secure, remote dashcams. It uses an enterprise-grade media server (MediaMTX) and a secure mesh network (Tailscale) to stream crystal-clear 1080p video directly to a web dashboard with less than 0.1s of latency.

---

## 🏗️ Architecture & Workflow

OKDriver is designed for scale and performance. Here is how the video travels from a smartphone to your browser without crashing or lagging:

1. **The Cameras (Android Phones):**
   - The phones run the **IP Webcam** app, capturing H.264 video and G711 audio.
   - The phones are connected to a **Tailscale** VPN, securing them behind a private IP address (e.g., `100.x.x.x`) without needing port forwarding.
2. **The Media Server (MediaMTX):**
   - Running on your central laptop/server, **MediaMTX** waits in the background. 
   - It is completely idle until a user opens the dashboard (On-Demand Streaming).
3. **The Control Plane (FastAPI):**
   - A Python backend manages the database of cameras. 
   - When the user clicks "Live View" on the dashboard, FastAPI registers the phone's Tailscale IP with MediaMTX.
4. **The Client (React Dashboard):**
   - Hosted on **Vercel**, the React frontend connects to the FastAPI server (via **Ngrok**).
   - The frontend establishes a direct **WebRTC (WHEP)** connection with MediaMTX.
   - MediaMTX instantly reaches out to the phone over Tailscale, grabs the raw RTSP video/audio packets, and passes them straight to the browser. Zero transcoding, zero lag, zero Python crashes!

---

## 🚀 Quick Start Guide

Want to run this yourself? Follow these steps to spin up the entire stack.

### 1. Prerequisites
- **Python 3.8+** installed on your server/laptop.
- **Node.js** installed (if you want to run the frontend locally).
- **Tailscale** installed on your server and all Android phones (logged into the same account).
- **Ngrok** installed and authenticated (to expose the backend to Vercel).

### 2. Camera Setup (Phones)
1. Install **IP Webcam** from the Google Play Store on your Android phones.
2. Open the app, go to **Video preferences**, and set the resolution to `1280x720` or `1920x1080` (Quality: 80).
3. Scroll to the bottom and click **Start Server**.
4. Open the Tailscale app on the phone and note its `100.x.x.x` IP address.

### 3. Clone & Start MediaMTX
1. Clone this repository:
   ```bash
   git clone https://github.com/sweetyk7/okdriver-ai-platform.git
   cd okdriver-ai-platform
   ```
2. Start the Media Server (Windows):
   ```powershell
   cd mediamtx
   .\start_mediamtx.ps1
   ```
   *(Note: This script will automatically download the 50MB MediaMTX executable for you if it is missing! Keep this window open.)*

### 4. Start the Python Backend
Open a **new terminal tab**:
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # (On Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Expose the Backend
Open a **third terminal tab** and use Ngrok to expose port 8000 to the public internet so Vercel can reach it:
```bash
ngrok http 8000
```
Copy the `https://xxxx.ngrok.app` URL it gives you.

### 6. Frontend Deployment (Vercel)
1. Deploy the `frontend` folder to Vercel.
2. In your Vercel Project Settings, add a new Environment Variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://xxxx.ngrok.app` (The URL you copied in Step 5)
3. Redeploy the Vercel project.

### 7. View Your Cameras
Go to your live Vercel dashboard. Click **Add Camera**, type in the camera name (e.g., `Dashcam 1`), and input the URL: `http://<TAILSCALE_IP>:8080/video`. 

Click **Live View**, and you will instantly see a high-definition stream with audio support!

---
*Built by the OKDriver Team.*
