import React from 'react';

export default function SettingsPage() {
  return (
    <div className="page-content">
      <div className="page-header">
        <h2>⚙️ Settings</h2>
      </div>

      <div className="settings-grid">
        <div className="glass-panel settings-card">
          <h3>🔐 System Info</h3>
          <div className="settings-item"><span>Platform</span><span>okDriver AI v2.0</span></div>
          <div className="settings-item"><span>Backend</span><span>FastAPI (Python)</span></div>
          <div className="settings-item"><span>Frontend</span><span>React + Vite</span></div>
          <div className="settings-item"><span>Database</span><span>SQLite</span></div>
          <div className="settings-item"><span>AI Engine</span><span>OpenCV + Cascade</span></div>
        </div>

        <div className="glass-panel settings-card">
          <h3>📡 API Integrations</h3>
          <div className="settings-item"><span>VAHAN (Vehicle DB)</span><span className="status-badge online">Mock Active</span></div>
          <div className="settings-item"><span>SARTHI (License DB)</span><span className="status-badge online">Mock Active</span></div>
          <div className="settings-item"><span>eGujCop (CCTNS)</span><span className="status-badge online">Mock Active</span></div>
          <div className="settings-item"><span>NAFIS (Fingerprint)</span><span className="status-badge online">Mock Active</span></div>
        </div>

        <div className="glass-panel settings-card">
          <h3>🤖 AI Modules</h3>
          <div className="settings-item"><span>ANPR (Number Plate)</span><span className="status-badge online">Enabled</span></div>
          <div className="settings-item"><span>Face Detection</span><span className="status-badge online">Enabled</span></div>
          <div className="settings-item"><span>Anomaly Detection</span><span className="status-badge online">Enabled</span></div>
          <div className="settings-item"><span>Crowd Analysis</span><span className="status-badge degraded">Coming Soon</span></div>
        </div>
      </div>
    </div>
  );
}
