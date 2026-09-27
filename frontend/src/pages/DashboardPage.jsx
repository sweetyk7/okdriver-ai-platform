import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import API from '../utils/api';
import CameraFeed from '../components/CameraFeed';

export default function DashboardPage() {
  const [cameras, setCameras] = useState([]);
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [vehicleQuery, setVehicleQuery] = useState('');
  const [routePoints, setRoutePoints] = useState([]);

  useEffect(() => {
    API.get('/cameras/').then(r => setCameras(r.data)).catch(() => {});
    API.get('/analytics/overview').then(r => setStats(r.data)).catch(() => {});
    API.get('/alerts/').then(r => setAlerts(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    const iv = setInterval(() => {
      API.get('/alerts/').then(r => setAlerts(r.data)).catch(() => {});
    }, 5000);
    return () => clearInterval(iv);
  }, []);

  const fetchHistory = async () => {
    if (!vehicleQuery.trim()) return;
    try {
      const r = await API.get(`/vehicles/${vehicleQuery}/history`);
      setRoutePoints(r.data.map(p => [p.latitude, p.longitude]));
    } catch { setRoutePoints([]); }
  };

  const mapCenter = cameras.length > 0
    ? [cameras[0].latitude, cameras[0].longitude]
    : [23.0225, 72.5714]; // Default: Ahmedabad

  return (
    <div className="page-content">
      {/* Stats Row */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>📷</div>
          <div><div className="stat-value">{stats?.cameras?.total || 0}</div><div className="stat-label">Total Cameras</div></div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>✅</div>
          <div><div className="stat-value">{stats?.cameras?.online || 0}</div><div className="stat-label">Online</div></div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' }}>🚨</div>
          <div><div className="stat-value">{stats?.detections?.total_alerts || 0}</div><div className="stat-label">Alerts</div></div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(139, 92, 246, 0.15)', color: '#8b5cf6' }}>🤖</div>
          <div><div className="stat-value">{stats?.detections?.ai_detections || 0}</div><div className="stat-label">AI Detections</div></div>
        </div>
      </div>

      {/* Main Grid: Map + Alerts */}
      <div className="dashboard-grid">
        <div className="map-container glass-panel" style={{ flex: 2 }}>
          <MapContainer center={mapCenter} zoom={12} scrollWheelZoom={true}>
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {cameras.map(cam => (
              <Marker key={cam.id} position={[cam.latitude, cam.longitude]}>
                <Popup><b>{cam.camera_id}</b><br />{cam.name}<br />Dept: {cam.department_name}<br />Status: {cam.status}</Popup>
              </Marker>
            ))}
            {routePoints.length > 1 && (
              <Polyline positions={routePoints} color="#ef4444" weight={4} dashArray="8,5" />
            )}
          </MapContainer>
        </div>

        {/* Right Panel: Alerts + Vehicle Tracker */}
        <div className="dashboard-right-panel">
          {/* Vehicle Tracker */}
          <div className="glass-panel" style={{ padding: '16px' }}>
            <p className="section-title">🗺️ Vehicle Route Tracker</p>
            <div className="history-form">
              <input
                placeholder="e.g. GJ01AB7821"
                value={vehicleQuery}
                onChange={e => setVehicleQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && fetchHistory()}
              />
              <button onClick={fetchHistory}>Track</button>
            </div>
            {routePoints.length > 0 && (
              <p style={{ fontSize: '12px', color: 'var(--success)' }}>
                ✅ Route drawn on map ({routePoints.length} points)
              </p>
            )}
          </div>


        </div>
      </div>

      {/* Preview Feeds */}
      <div className="glass-panel" style={{ padding: '16px' }}>
        <p className="section-title">📹 Camera Previews</p>
        <div className="video-grid cols-4">
          {cameras.slice(0, 4).map(cam => (
            <CameraFeed key={cam.id} feed={cam} />
          ))}
        </div>
      </div>
    </div>
  );
}
