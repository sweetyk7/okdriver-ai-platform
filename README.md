# okDriver AI Platform 🚔

> **Full-Stack CCTV Monitoring & Real-Time AI Alert System**  
> Built with FastAPI (Python) + React.js

---

## ✨ Features

- 📷 **Camera Registry** – Add and manage CCTV cameras with location info
- 🗺️ **Interactive GIS Map** – View all cameras plotted on a live map (Leaflet.js)
- 🎥 **Live Video Feeds** – Simulated CCTV footage displayed on dashboard
- 🤖 **AI Detection API** – Receives vehicle detection events from AI models
- 🚨 **Real-Time Alerts** – Instant popup alerts when a watchlisted vehicle is detected
- 🗂️ **Watchlist Management** – Add/track blacklisted/stolen vehicles
- 🛣️ **Vehicle Movement History** – Track a vehicle's route across cameras on the map

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, Vite, Leaflet.js, Axios |
| Backend | Python, FastAPI, SQLAlchemy |
| Database | SQLite (dev) |
| Real-Time | WebSockets + Polling |

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone <your-repo-link>
cd okDriver
```

### 2. Start the Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```
Backend runs at: **http://127.0.0.1:8000**  
API Docs: **http://127.0.0.1:8000/docs**

### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
Dashboard runs at: **http://localhost:5173**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/cameras/` | Add a new camera |
| GET | `/cameras/` | List all cameras |
| POST | `/watchlist/` | Add vehicle to watchlist |
| POST | `/detect/` | Submit AI detection event |
| GET | `/alerts/` | Get recent watchlist alerts |
| GET | `/vehicles/{id}/history` | Get vehicle route history |

---

## 🧪 Quick Demo Test

1. Add a camera via `POST /cameras/`
2. Add a vehicle to watchlist via `POST /watchlist/`
3. Simulate AI detection via `POST /detect/` with the same vehicle number
4. Watch the **real-time alert popup** appear on the dashboard!
