import React, { useState, useEffect } from 'react';
import API from '../utils/api';

export default function CameraRegistryPage() {
  const [cameras, setCameras] = useState([]);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [newCam, setNewCam] = useState({
    camera_id: '', name: '', department_name: 'Gujarat Police', camera_type: 'IP',
    protocol: 'RTSP', latitude: 23.0225, longitude: 72.5714, stream_url: '',
    zone: '', district: 'Ahmedabad'
  });

  const loadCameras = () => API.get('/cameras/').then(r => setCameras(r.data)).catch(() => {});
  useEffect(() => { loadCameras(); }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!newCam.camera_id || !newCam.name) return;
    try {
      await API.post('/cameras/', newCam);
      setShowForm(false);
      setNewCam({ camera_id: '', name: '', department_name: 'Gujarat Police', camera_type: 'IP', protocol: 'RTSP', latitude: 23.0225, longitude: 72.5714, stream_url: '', zone: '', district: 'Ahmedabad' });
      loadCameras();
    } catch (err) { console.error(err); }
  };

  const handleDelete = async (id) => {
    await API.delete(`/cameras/${id}`);
    loadCameras();
  };

  const filtered = cameras.filter(c =>
    c.camera_id.toLowerCase().includes(search.toLowerCase()) ||
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    (c.department_name || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>📷 Camera Registry</h2>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add Camera'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleAdd} className="add-cam-form glass-panel">
          <div className="form-grid">
            <input placeholder="Camera ID (e.g. GJ-CAM-013)" value={newCam.camera_id} onChange={e => setNewCam({ ...newCam, camera_id: e.target.value })} required />
            <input placeholder="Location Name" value={newCam.name} onChange={e => setNewCam({ ...newCam, name: e.target.value })} required />
            <select value={newCam.department_name} onChange={e => setNewCam({ ...newCam, department_name: e.target.value })}>
              <option>Gujarat Police</option><option>Gujarat Traffic Police</option><option>GSRTC</option>
              <option>Municipal Corporation</option><option>Health Department</option><option>Panchayat</option>
            </select>
            <select value={newCam.camera_type} onChange={e => setNewCam({ ...newCam, camera_type: e.target.value })}>
              <option>IP</option><option>PTZ</option><option>Analog</option><option>Mobile</option>
            </select>
            <select value={newCam.protocol} onChange={e => setNewCam({ ...newCam, protocol: e.target.value })}>
              <option>RTSP</option><option>MJPEG</option><option>ONVIF</option><option>HTTP</option>
            </select>
            <input placeholder="District" value={newCam.district} onChange={e => setNewCam({ ...newCam, district: e.target.value })} />
            <input type="number" step="0.0001" placeholder="Latitude" value={newCam.latitude} onChange={e => setNewCam({ ...newCam, latitude: parseFloat(e.target.value) })} required />
            <input type="number" step="0.0001" placeholder="Longitude" value={newCam.longitude} onChange={e => setNewCam({ ...newCam, longitude: parseFloat(e.target.value) })} required />
          </div>
          <input placeholder="Stream URL (e.g. rtsp://192.168.1.10:554/stream)" value={newCam.stream_url} onChange={e => setNewCam({ ...newCam, stream_url: e.target.value })} />
          <button type="submit" className="btn-success">Save Camera</button>
        </form>
      )}

      <input className="toolbar-input" placeholder="Search cameras by ID, name, or department..." value={search} onChange={e => setSearch(e.target.value)} style={{ width: '100%', marginBottom: '16px' }} />

      <div className="camera-table glass-panel">
        <table>
          <thead>
            <tr>
              <th>Camera ID</th>
              <th>Location</th>
              <th>Department</th>
              <th>Type</th>
              <th>Protocol</th>
              <th>District</th>
              <th>Status</th>
              <th>Health</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(cam => (
              <tr key={cam.id}>
                <td><strong>{cam.camera_id}</strong></td>
                <td>{cam.name}</td>
                <td>{cam.department_name || '-'}</td>
                <td><span className="badge">{cam.camera_type}</span></td>
                <td><span className="badge">{cam.protocol}</span></td>
                <td>{cam.district || '-'}</td>
                <td><span className={`status-badge ${cam.status.toLowerCase()}`}>{cam.status}</span></td>
                <td>
                  <div className="health-bar"><div className="health-fill" style={{ width: `${cam.health_score}%`, background: cam.health_score > 70 ? '#10b981' : cam.health_score > 40 ? '#f59e0b' : '#ef4444' }}></div></div>
                </td>
                <td>
                  <button className="btn-danger-sm" onClick={() => handleDelete(cam.camera_id)} title="Remove">✕</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
