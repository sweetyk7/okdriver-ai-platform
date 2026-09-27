import React, { useState, useEffect } from 'react';
import API from '../utils/api';

export default function WatchlistPage() {
  const [vehicles, setVehicles] = useState([]);
  const [newVehicle, setNewVehicle] = useState({ vehicle_number: '', reason: '', severity: 'High' });
  const [showForm, setShowForm] = useState(false);
  const [lookupPlate, setLookupPlate] = useState('');
  const [vahanData, setVahanData] = useState(null);

  const loadWatchlist = () => API.get('/watchlist/vehicles').then(r => setVehicles(r.data)).catch(() => {});
  useEffect(() => { loadWatchlist(); }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!newVehicle.vehicle_number) return;
    await API.post('/watchlist/vehicles', newVehicle);
    setNewVehicle({ vehicle_number: '', reason: '', severity: 'High' });
    setShowForm(false);
    loadWatchlist();
  };

  const handleDelete = async (vn) => {
    await API.delete(`/watchlist/vehicles/${vn}`);
    loadWatchlist();
  };

  const lookupVahan = async () => {
    if (!lookupPlate.trim()) return;
    try {
      const r = await API.get(`/gov/vahan/${lookupPlate}`);
      setVahanData(r.data);
    } catch { setVahanData(null); }
  };

  const simulateAlert = async (vn) => {
    await API.post('/detect/', { camera_id: 'GJ-CAM-001', vehicle_number: vn });
    alert(`Detection triggered for ${vn}!`);
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>🚨 Vehicle Watchlist</h2>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add Vehicle'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleAdd} className="add-cam-form glass-panel">
          <div className="form-grid">
            <input placeholder="Vehicle Number (e.g. GJ01AB1234)" value={newVehicle.vehicle_number} onChange={e => setNewVehicle({ ...newVehicle, vehicle_number: e.target.value })} required />
            <input placeholder="Reason" value={newVehicle.reason} onChange={e => setNewVehicle({ ...newVehicle, reason: e.target.value })} required />
            <select value={newVehicle.severity} onChange={e => setNewVehicle({ ...newVehicle, severity: e.target.value })}>
              <option>Critical</option><option>High</option><option>Medium</option><option>Low</option>
            </select>
          </div>
          <button type="submit" className="btn-success">Add to Watchlist</button>
        </form>
      )}

      {/* VAHAN Lookup */}
      <div className="glass-panel" style={{ padding: '16px', marginBottom: '20px' }}>
        <p className="section-title">🔍 VAHAN Database Lookup</p>
        <div className="history-form">
          <input placeholder="Enter plate number to lookup..." value={lookupPlate} onChange={e => setLookupPlate(e.target.value)} onKeyDown={e => e.key === 'Enter' && lookupVahan()} />
          <button onClick={lookupVahan}>Lookup</button>
        </div>
        {vahanData && (
          <div className="vahan-result">
            <div className="vahan-grid">
              <div><span className="vahan-label">Owner</span><span>{vahanData.owner}</span></div>
              <div><span className="vahan-label">Vehicle</span><span>{vahanData.make_model}</span></div>
              <div><span className="vahan-label">Type</span><span>{vahanData.vehicle_type}</span></div>
              <div><span className="vahan-label">RTO</span><span>{vahanData.rto}</span></div>
              <div><span className="vahan-label">Status</span><span className={`status-badge ${vahanData.status.toLowerCase()}`}>{vahanData.status}</span></div>
              <div><span className="vahan-label">Insurance</span><span>{vahanData.insurance_valid ? '✅ Valid' : '❌ Expired'}</span></div>
            </div>
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px' }}>Source: {vahanData.source}</p>
          </div>
        )}
      </div>

      {/* Watchlist Table */}
      <div className="camera-table glass-panel">
        <table>
          <thead>
            <tr>
              <th>Vehicle Number</th>
              <th>Reason</th>
              <th>Severity</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {vehicles.map(v => (
              <tr key={v.id}>
                <td><strong>{v.vehicle_number}</strong></td>
                <td>{v.reason}</td>
                <td><span className={`severity-badge ${v.severity.toLowerCase()}`}>{v.severity}</span></td>
                <td>
                  <button className="btn-warning-sm" onClick={() => simulateAlert(v.vehicle_number)} title="Simulate Detection">⚡</button>
                  <button className="btn-danger-sm" onClick={() => handleDelete(v.vehicle_number)} title="Remove" style={{ marginLeft: '8px' }}>✕</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
