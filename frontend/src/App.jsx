import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import './App.css';

const DUMMY_VIDEOS = [
  'https://samplelib.com/lib/preview/mp4/sample-5s.mp4',
  'https://samplelib.com/lib/preview/mp4/sample-10s.mp4',
  'https://samplelib.com/lib/preview/mp4/sample-15s.mp4',
  'https://samplelib.com/lib/preview/mp4/sample-20s.mp4',
  'https://samplelib.com/lib/preview/mp4/sample-30s.mp4'
];

function getDummyVideo(id) {
  // Simple hash to consistently pick a video for a given id
  let hash = 0;
  for (let i = 0; i < id.length; i++) hash = id.charCodeAt(i) + ((hash << 5) - hash);
  return DUMMY_VIDEOS[Math.abs(hash) % DUMMY_VIDEOS.length];
}

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
  const [cameraSearch, setCameraSearch] = useState('');
  
  // New Camera Form State
  const [showAddForm, setShowAddForm] = useState(false);
  const [newCam, setNewCam] = useState({
    camera_id: '',
    name: '',
    department: 'Traffic',
    latitude: 28.6139,
    longitude: 77.2090,
    stream_url: ''
  });

  const loadCameras = () => {
    axios.get('http://127.0.0.1:8000/cameras/')
      .then(r => { setCameras(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  };

  // Fetch cameras
  useEffect(() => {
    loadCameras();
  }, []);

  const handleAddCamera = async (e) => {
    e.preventDefault();
    if (!newCam.camera_id || !newCam.name) return;
    try {
      await axios.post('http://127.0.0.1:8000/cameras/', newCam);
      setShowAddForm(false);
      setNewCam({ camera_id: '', name: '', department: 'Traffic', latitude: 28.6139, longitude: 77.2090, stream_url: '' });
      loadCameras();
    } catch (err) {
      console.error("Failed to add camera", err);
    }
  };

  const handleRemoveCamera = async (id) => {
    try {
      await axios.delete(`http://127.0.0.1:8000/cameras/${id}`);
      loadCameras();
    } catch (err) {
      console.error("Failed to remove camera", err);
    }
  };

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
        <div className="brand">🚔 Smart Policing Dashboard</div>

        <div className="stat-row">
          <div className="stat-box">
            <h3>Total Cameras</h3>
            <p>{cameras.length}</p>
          </div>
          <div className="stat-box" style={{ borderLeftColor: 'var(--success)' }}>
            <h3>Online</h3>
            <p style={{ color: 'var(--success)' }}>{cameras.length}</p>
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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <p className="section-title">🚨 Recent Alerts</p>
            <button 
              onClick={async () => {
                // Add dummy vehicle to watchlist
                await axios.post('http://127.0.0.1:8000/watchlist/', { vehicle_number: 'TEST-1234', reason: 'Stolen Vehicle (Simulated)' }).catch(()=>{});
                // Trigger detection
                await axios.post('http://127.0.0.1:8000/detect/', { camera_id: 'CAM-TEST', vehicle_number: 'TEST-1234' }).catch(()=>{});
              }}
              style={{ background: 'var(--warning)', border: 'none', color: 'black', borderRadius: '4px', padding: '4px 8px', cursor: 'pointer', fontSize: '10px', fontWeight: 'bold' }}
            >
              Simulate Alert
            </button>
          </div>
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

        {/* Camera List & Registry */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <p className="section-title" style={{ margin: 0 }}>📷 Camera Registry</p>
            <button 
              onClick={() => setShowAddForm(!showAddForm)}
              style={{ background: 'var(--accent-color)', border: 'none', color: 'white', borderRadius: '4px', padding: '4px 8px', cursor: 'pointer', fontSize: '11px' }}
            >
              {showAddForm ? 'Cancel' : '+ Add'}
            </button>
          </div>

          <div className="history-form">
            <input 
              placeholder="Search cameras..." 
              value={cameraSearch} 
              onChange={e => setCameraSearch(e.target.value)} 
            />
          </div>

          {showAddForm && (
            <form onSubmit={handleAddCamera} className="add-cam-form glass-panel" style={{ padding: '12px', marginBottom: '12px', display: 'flex', flexDirection: 'column', gap: '8px', background: '#f8fafc' }}>
              <input placeholder="Camera ID (e.g. CAM-04)" value={newCam.camera_id} onChange={e => setNewCam({...newCam, camera_id: e.target.value})} required style={{ padding: '8px', border: '1px solid var(--border-color)', borderRadius: '4px' }} />
              <input placeholder="Location Name" value={newCam.name} onChange={e => setNewCam({...newCam, name: e.target.value})} required style={{ padding: '8px', border: '1px solid var(--border-color)', borderRadius: '4px' }} />
              <div style={{ display: 'flex', gap: '8px' }}>
                <input type="number" step="0.0001" placeholder="Lat" value={newCam.latitude} onChange={e => setNewCam({...newCam, latitude: parseFloat(e.target.value)})} required style={{ width: '50%', padding: '8px', border: '1px solid var(--border-color)', borderRadius: '4px' }} />
                <input type="number" step="0.0001" placeholder="Lng" value={newCam.longitude} onChange={e => setNewCam({...newCam, longitude: parseFloat(e.target.value)})} required style={{ width: '50%', padding: '8px', border: '1px solid var(--border-color)', borderRadius: '4px' }} />
              </div>
              <input placeholder="Stream URL (Optional - e.g. http://ip:8080/video)" value={newCam.stream_url} onChange={e => setNewCam({...newCam, stream_url: e.target.value})} style={{ padding: '8px', border: '1px solid var(--border-color)', borderRadius: '4px' }} />
              <button type="submit" style={{ background: 'var(--success)', border: 'none', color: 'white', padding: '8px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Save Camera</button>
            </form>
          )}

          {loading ? <p>Loading...</p> : cameras.filter(c => c.camera_id.toLowerCase().includes(cameraSearch.toLowerCase()) || c.name.toLowerCase().includes(cameraSearch.toLowerCase())).map(cam => (
            <div key={cam.id} className="cam-item">
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span><strong>{cam.camera_id}</strong> - {cam.name}</span>
                <span className="status-dot">● Online</span>
              </div>
              <button 
                onClick={() => handleRemoveCamera(cam.camera_id)}
                style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid var(--danger)', color: 'var(--danger)', borderRadius: '4px', padding: '4px 8px', cursor: 'pointer', fontSize: '10px', height: 'fit-content' }}
                title="Remove Camera"
              >
                ✕
              </button>
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
          {cameras.length === 0 && !loading && (
            <div style={{ gridColumn: '1 / -1', padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
              No cameras added yet. Add a camera from the sidebar to view feeds.
            </div>
          )}
          {cameras.filter(c => c.camera_id.toLowerCase().includes(cameraSearch.toLowerCase()) || c.name.toLowerCase().includes(cameraSearch.toLowerCase())).map(feed => (
            <div key={feed.id} className="video-feed">
              {feed.stream_url ? (
                <img src={feed.stream_url} alt={`Live feed from ${feed.camera_id}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                <video autoPlay muted loop playsInline>
                  <source src={getDummyVideo(feed.camera_id)} type="video/mp4" />
                </video>
              )}
              {/* Top label: Camera ID + timestamp */}
              <div className="video-top-label">
                <span>{feed.camera_id} | {feed.department}</span>
                <LiveClock />
              </div>
              {/* Bottom label: Live indicator */}
              <div className="video-label">
                <span><span className="live-dot" />REC</span>
                <span>{feed.name}</span>
              </div>
              
              {/* Delete overlay button on hover can be added here or just rely on sidebar */}
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}

export default App;
