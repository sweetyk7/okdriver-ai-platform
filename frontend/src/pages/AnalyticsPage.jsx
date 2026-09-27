import React, { useState, useEffect } from 'react';
import API from '../utils/api';

export default function AnalyticsPage() {
  const [overview, setOverview] = useState(null);
  const [byType, setByType] = useState([]);
  const [byCamera, setByCamera] = useState([]);
  const [health, setHealth] = useState([]);

  useEffect(() => {
    API.get('/analytics/overview').then(r => setOverview(r.data)).catch(() => {});
    API.get('/analytics/detections-by-type').then(r => setByType(r.data)).catch(() => {});
    API.get('/analytics/detections-by-camera').then(r => setByCamera(r.data)).catch(() => {});
    API.get('/analytics/camera-health').then(r => setHealth(r.data)).catch(() => {});
  }, []);

  const maxDetection = Math.max(...byType.map(d => d.count), 1);
  const maxCamera = Math.max(...byCamera.map(d => d.count), 1);

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>📊 Analytics & Intelligence</h2>
      </div>

      {/* Overview Cards */}
      {overview && (
        <div className="stats-grid">
          <div className="stat-card"><div className="stat-icon" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>📷</div><div><div className="stat-value">{overview.cameras.total}</div><div className="stat-label">Total Cameras</div></div></div>
          <div className="stat-card"><div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>✅</div><div><div className="stat-value">{overview.cameras.online}</div><div className="stat-label">Online</div></div></div>
          <div className="stat-card"><div className="stat-icon" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' }}>🚨</div><div><div className="stat-value">{overview.detections.total_alerts}</div><div className="stat-label">Total Alerts</div></div></div>
          <div className="stat-card"><div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b' }}>🛡️</div><div><div className="stat-value">{overview.watchlist.vehicles}</div><div className="stat-label">Watchlist Vehicles</div></div></div>
        </div>
      )}

      <div className="analytics-grid">
        {/* Detections by Type */}
        <div className="glass-panel chart-card">
          <p className="section-title">🤖 AI Detections by Type</p>
          <div className="bar-chart">
            {byType.map(d => (
              <div key={d.type} className="bar-row">
                <span className="bar-label">{d.type}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${(d.count / maxDetection) * 100}%` }}></div>
                </div>
                <span className="bar-value">{d.count}</span>
              </div>
            ))}
            {byType.length === 0 && <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No AI detections yet.</p>}
          </div>
        </div>

        {/* Detections by Camera */}
        <div className="glass-panel chart-card">
          <p className="section-title">📷 Top Cameras by Detections</p>
          <div className="bar-chart">
            {byCamera.map(d => (
              <div key={d.camera_id} className="bar-row">
                <span className="bar-label">{d.camera_id}</span>
                <div className="bar-track">
                  <div className="bar-fill bar-fill-blue" style={{ width: `${(d.count / maxCamera) * 100}%` }}></div>
                </div>
                <span className="bar-value">{d.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Camera Health */}
        <div className="glass-panel chart-card">
          <p className="section-title">🏥 Camera Health Overview</p>
          <div className="health-overview">
            {health.map(h => (
              <div key={h.status} className="health-stat">
                <div className={`health-circle ${h.status.toLowerCase()}`}>{h.count}</div>
                <span>{h.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
