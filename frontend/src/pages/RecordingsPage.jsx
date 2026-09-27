import React, { useState, useEffect } from 'react';
import API from '../utils/api';

export default function RecordingsPage() {
  const [recordings, setRecordings] = useState([]);
  const [snapshots, setSnapshots] = useState([]);
  const [tab, setTab] = useState('recordings');

  useEffect(() => {
    API.get('/media/recordings').then(r => setRecordings(r.data)).catch(() => {});
    API.get('/media/snapshots').then(r => setSnapshots(r.data)).catch(() => {});
  }, []);

  const data = tab === 'recordings' ? recordings : snapshots;

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>💾 Recordings & Snapshots</h2>
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
        <button className={`layout-btn ${tab === 'recordings' ? 'active' : ''}`} onClick={() => setTab('recordings')}>
          🎥 Recordings ({recordings.length})
        </button>
        <button className={`layout-btn ${tab === 'snapshots' ? 'active' : ''}`} onClick={() => setTab('snapshots')}>
          📸 Snapshots ({snapshots.length})
        </button>
      </div>

      {data.length === 0 ? (
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
          No {tab} found yet. Use the camera toolbar to start recording or take snapshots.
        </div>
      ) : (
        <div className="camera-table glass-panel">
          <table>
            <thead>
              <tr>
                <th>Camera</th>
                <th>Date</th>
                <th>Filename</th>
                <th>Size</th>
                <th>Path</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, i) => (
                <tr key={i}>
                  <td><strong>{item.camera_id}</strong></td>
                  <td>{item.date}</td>
                  <td>{item.filename}</td>
                  <td>{tab === 'recordings' ? `${item.size_mb} MB` : `${item.size_kb} KB`}</td>
                  <td style={{ fontSize: '11px', color: 'var(--text-muted)', wordBreak: 'break-all' }}>{item.path}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
