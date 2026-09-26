import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import './App.css';

const VIDEO_FEEDS = [
  { 
    id: 'DL-CAM-01', 
    name: 'SAROJINI NAGAR CHOWK', 
    loc: 'SOUTH DELHI', 
    src: 'https://samplelib.com/lib/preview/mp4/sample-5s.mp4' 
  },
  { 
    id: 'DL-CAM-02', 
    name: 'INDIA GATE CIRCLE', 
    loc: 'NEW DELHI', 
    src: 'https://samplelib.com/lib/preview/mp4/sample-10s.mp4' 
  },
  { 
    id: 'DL-CAM-03', 
    name: 'GURUDWARA BANGLA SAHIB RD', 
    loc: 'CENTRAL DELHI', 
    src: 'https://samplelib.com/lib/preview/mp4/sample-15s.mp4' 
  },
];

function LiveClock() {
  const [time, setTime] = useState(new Date().toLocaleTimeString('en-IN'));
  useEffect(() => {
    const t = setInterval(() => setTime(new Date().toLocaleTimeString('en-IN')), 1000);
    return () => clearInterval(t);
  }, []);
  return <span>{new Date().toLocaleDateString('en-IN')} {time}</span>;
}

function App() {
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeAlert, setActiveAlert] = useState(null);
  const [alertHistory, setAlertHistory] = useState([]);
  const [vehicleQuery, setVehicleQuery] = useState('');
  const [routePoints, setRoutePoints] = useState([]);

  // Fetch cameras
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/cameras/')
      .then(r => { setCameras(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  // Polling for alerts every 3 seconds
  useEffect(() => {
    const pollAlerts = async () => {
      try {
        const r = await axios.get('http://127.0.0.1:8000/alerts/');
        if (r.data.length > 0) {
          setAlertHistory(prev => {
            const prevKeys = prev.map(a => a.vehicle_number + a.timestamp);
            const brandNew = r.data.filter(a => !prevKeys.includes(a.vehicle_number + a.timestamp));
            if (brandNew.length > 0) {
              setActiveAlert(brandNew[0]);
              setTimeout(() => setActiveAlert(null), 6000);
            }
            return r.data.slice(0, 5);
          });
        }
      } catch (_) {}
    };
    pollAlerts();
    const iv = setInterval(pollAlerts, 3000);
    return () => clearInterval(iv);
  }, []);

  // Fetch vehicle movement history
  const fetchHistory = async () => {
    if (!vehicleQuery.trim()) return;
    try {
      const r = await axios.get(`http://127.0.0.1:8000/vehicles/${vehicleQuery}/history`);
      const points = r.data.map(p => [p.latitude, p.longitude]);
      setRoutePoints(points);
    } catch (_) {
      setRoutePoints([]);
    }
  };

  return (
    <div className="dashboard-container">

      {/* 🚨 Alert Popup */}
      {activeAlert && (
        <div className="alert-popup">
          <h3>🚨 WATCHLIST ALERT</h3>
          <p><strong>Vehicle:</strong> {activeAlert.vehicle_number}</p>
          <p><strong>Camera:</strong> {activeAlert.camera_id}</p>
          <p><strong>Reason:</strong> {activeAlert.reason}</p>
        </div>
      )}

      {/* SIDEBAR */}
      <div className="sidebar glass-panel">
        <div className="brand">🔴 okDriver Live</div>

        <div className="stat-row">
          <div className="stat-box">
            <h3>Total Cameras</h3>
            <p>{cameras.length}</p>
          </div>
          <div className="stat-box" style={{ borderLeftColor: 'var(--success)' }}>
            <h3>Status</h3>
            <p style={{ color: 'var(--success)', fontSize: '16px' }}>Online</p>
          </div>
        </div>

        {/* Vehicle History Search */}
        <div>
          <p className="section-title">🗺️ Vehicle Route History</p>
          <div className="history-form">
            <input
              placeholder="e.g. RJ14-CHOR-1111"
              value={vehicleQuery}
              onChange={e => setVehicleQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && fetchHistory()}
            />
            <button onClick={fetchHistory}>Track</button>
          </div>
          {routePoints.length > 0
            ? <p style={{ fontSize: '12px', color: 'var(--success)' }}>✅ Route drawn on map ({routePoints.length} points)</p>
            : <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Enter vehicle number to track route</p>
          }
        </div>

        {/* Recent Alerts */}
        <div>
          <p className="section-title">🚨 Recent Alerts</p>
          {alertHistory.length === 0
            ? <p style={{ fontSize: '12px', color: 'gray' }}>No alerts yet.</p>
            : alertHistory.map((a, i) => (
              <div key={i} className="alert-item">
                <strong>{a.vehicle_number}</strong> at {a.camera_id}<br />
                <span style={{ color: '#ef4444', fontSize: '12px' }}>{a.reason}</span>
              </div>
            ))
          }
        </div>

        {/* Camera List */}
        <div>
          <p className="section-title">📷 Camera Registry</p>
          {loading ? <p>Loading...</p> : cameras.map(cam => (
            <div key={cam.id} className="cam-item">
              <span><strong>{cam.camera_id}</strong> - {cam.name}</span>
              <span className="status-dot">● Online</span>
            </div>
          ))}
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="main-content">

        {/* MAP */}
        <div className="map-container">
          <MapContainer center={[28.6139, 77.2090]} zoom={12} scrollWheelZoom={true}>
            <TileLayer
              attribution='&copy; OpenStreetMap contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {cameras.map(cam => (
              <Marker key={cam.id} position={[cam.latitude, cam.longitude]}>
                <Popup><b>{cam.camera_id}</b><br />{cam.name}<br />Dept: {cam.department}</Popup>
              </Marker>
            ))}
            {/* Route line */}
            {routePoints.length > 1 && (
              <Polyline positions={routePoints} color="#ef4444" weight={4} dashArray="8,5" />
            )}
            {/* Route markers */}
            {routePoints.map((pt, i) => (
              <Marker key={i} position={pt}>
                <Popup>Stop {i + 1}: {vehicleQuery}</Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* VIDEO FEEDS */}
        <div className="video-section glass-panel">
          {VIDEO_FEEDS.map(feed => (
            <div key={feed.id} className="video-feed">
              <video autoPlay muted loop playsInline>
                <source src={feed.src} type="video/mp4" />
              </video>
              {/* Top label: Camera ID + timestamp */}
              <div className="video-top-label">
                <span>CAM {feed.id} | {feed.loc}</span>
                <LiveClock />
              </div>
              {/* Bottom label: Live indicator */}
              <div className="video-label">
                <span><span className="live-dot" />REC</span>
                <span>{feed.name}</span>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}

export default App;
