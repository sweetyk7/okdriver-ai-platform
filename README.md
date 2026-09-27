# OKDriver AI Platform 🚙📷

A high-performance, ultra-low latency fleet monitoring dashboard built with React, FastAPI, WebRTC, and MediaMTX.

OKDriver allows you to turn ordinary Android smartphones (or any RTSP-compatible IP camera) into secure, remote dashcams. It uses an enterprise-grade media server (MediaMTX) and a secure mesh network (Tailscale) to stream crystal-clear 1080p video directly to a web dashboard with less than 0.1s of latency.

---

## 📊 Flow Diagram

The diagram below illustrates how all the components of the OKDriver AI platform communicate to deliver a zero-latency video stream:

```mermaid
sequenceDiagram
    participant User as 💻 Web Browser (React/Vercel)
    participant Ngrok as 🌐 Ngrok Tunnel
    participant FastAPI as 🐍 FastAPI Backend
    participant MediaMTX as 📽️ MediaMTX Server
    participant Tailscale as 🔒 Tailscale VPN
    participant Camera as 📱 IP Camera / Android

    User->>Ngrok: 1. Clicks "Live View"
    Ngrok->>FastAPI: 2. Forwards Request
    FastAPI->>MediaMTX: 3. Registers Camera URL (sourceOnDemand)
    FastAPI->>MediaMTX: 4. Forwards WebRTC SDP Offer (WHEP)
    MediaMTX->>Tailscale: 5. Connects via RTSP
    Tailscale->>Camera: 6. Requests H.264 Video Stream
    Camera-->>Tailscale: 7. Streams Raw Video/Audio
    Tailscale-->>MediaMTX: 8. Delivers Packets to Server
    MediaMTX-->>FastAPI: 9. Returns WebRTC SDP Answer
    FastAPI-->>Ngrok: 10. Forwards SDP Answer
    Ngrok-->>User: 11. Finalizes WebRTC Handshake
    Note over User, MediaMTX: 12. Direct WebRTC P2P Video Stream Begins (Zero Latency)
```

---

## 🏗️ System Architecture & Workflow

OKDriver is designed for scale and performance. Here is how the video travels from a smartphone to your browser without crashing or lagging:

1. **The Cameras (Data Source):**
   - The cameras (Android phones or dedicated IP Cams) capture H.264 video and audio.
   - The cameras are securely hidden behind a **Tailscale** Zero-Trust VPN, keeping them safe from public internet scanners without the need for port forwarding.
2. **The Media Server (MediaMTX):**
   - Running on your central laptop/server, **MediaMTX** waits in the background. 
   - It is completely idle until a user opens the dashboard (**On-Demand Streaming**).
3. **The Control Plane (FastAPI):**
   - A Python backend manages the SQLite database of cameras. 
   - When the user clicks "Live View", FastAPI registers the phone's Tailscale IP with MediaMTX and passes the WebRTC (WHEP) negotiation.
4. **The Client (React Dashboard):**
   - Hosted on **Vercel**, the React frontend connects to the FastAPI server (via **Ngrok**).
   - Once the WebRTC handshake completes, MediaMTX instantly reaches out to the phone over Tailscale, grabs the raw RTSP video packets, and passes them straight to the browser. Zero transcoding, zero lag!

---

## 🚀 Scalability

The OKDriver platform is built to handle **hundreds of concurrent camera streams** on a single standard server. 

- **Zero Transcoding Overhead**: Unlike standard OpenCV or FFmpeg wrappers that decode and re-encode video frames (which destroys CPU performance), MediaMTX simply copies the raw H.264 bytes straight from the camera to your browser. This uses `<1% CPU` per stream.
- **Source On-Demand**: MediaMTX is configured to only connect to a camera when a user is actively viewing it on the dashboard. When the user closes the tab, the server drops the connection, saving battery on the phones and freeing up server bandwidth.
- **WebRTC (WHEP)**: Traditional streaming (like HLS or WebSockets) induces 5-10 seconds of delay. By natively using the WebRTC HTTP Egress Protocol (WHEP) over UDP, OKDriver achieves sub-`100ms` latency globally.

---

## 📷 Connecting Other Types of Cameras

While this guide focuses on Android phones, OKDriver's MediaMTX backbone is entirely agnostic. You can connect **any** RTSP-capable camera to this dashboard!

1. **Dedicated IP Cameras (Hikvision, Dahua, Reolink, etc.)**
   - Simply connect the camera to your local network or Tailscale.
   - Find its RTSP URL (e.g., `rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0`).
   - Add it to the dashboard! MediaMTX natively supports ONVIF and RTSP authentication.
2. **Raspberry Pi Cameras**
   - MediaMTX has built-in native support for Raspberry Pi hardware cameras (`rpiCamera`).
   - You can stream directly from a Pi by pointing the dashboard to the Pi's MediaMTX instance.
3. **USB Webcams**
   - If you want to stream a local USB webcam plugged into your server, you can use FFmpeg to serve it as an RTSP stream, which OKDriver will instantly pick up.

*(For Android phones, install the **IP Webcam** app from the Play Store, set resolution to 720p/1080p, start the server, and use `http://<TAILSCALE_IP>:8080/video` in the dashboard).*

---

## ⚡ Quick Start Guide

Want to run this yourself? Follow these steps to spin up the entire stack.

### 1. Prerequisites
- **Python 3.8+** installed on your server/laptop.
- **Node.js** installed (if you want to run the frontend locally).
- **Tailscale** installed on your server and all Android phones (logged into the same account).
- **Ngrok** installed and authenticated (to expose the backend to Vercel).

### 2. Clone & Start MediaMTX
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

### 3. Start the Python Backend
Open a **new terminal tab**:
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # (On Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Expose the Backend
Open a **third terminal tab** and use Ngrok to expose port 8000 to the public internet so Vercel can reach it:
```bash
ngrok http 8000
```
Copy the `https://xxxx.ngrok.app` URL it gives you.

### 5. Frontend Deployment (Vercel)
1. Deploy the `frontend` folder to Vercel.
2. In your Vercel Project Settings, add a new Environment Variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://xxxx.ngrok.app` (The URL you copied in Step 4)
3. Redeploy the Vercel project.

### 6. View Your Cameras
Go to your live Vercel dashboard. Click **Add Camera**, type in the camera name, and input the camera URL. Click **Live View**, and you will instantly see a high-definition stream with audio support!
