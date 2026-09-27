import React, { useState, useEffect } from 'react';
import API from '../utils/api';
import CameraFeed from '../components/CameraFeed';
import { LAYOUT_OPTIONS } from '../utils/constants';

export default function LiveViewPage() {
  const [cameras, setCameras] = useState([]);
  const [cols, setCols] = useState(3);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [page, setPage] = useState(0);
  const perPage = cols * cols;

  useEffect(() => {
    API.get('/cameras/').then(r => setCameras(r.data)).catch(() => {});
  }, []);

  const departments = [...new Set(cameras.map(c => c.department_name).filter(Boolean))];

  const filtered = cameras.filter(c => {
    const matchSearch = !search || c.camera_id.toLowerCase().includes(search.toLowerCase()) || c.name.toLowerCase().includes(search.toLowerCase());
    const matchDept = !deptFilter || c.department_name === deptFilter;
    return matchSearch && matchDept;
  });

  const totalPages = Math.ceil(filtered.length / perPage);
  const paged = filtered.slice(page * perPage, (page + 1) * perPage);

  return (
    <div className="page-content">
      {/* Toolbar */}
      <div className="live-toolbar glass-panel">
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flex: 1 }}>
          <input
            className="toolbar-input"
            placeholder="Search cameras..."
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(0); }}
          />
          <select className="toolbar-select" value={deptFilter} onChange={e => { setDeptFilter(e.target.value); setPage(0); }}>
            <option value="">All Departments</option>
            {departments.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Layout:</span>
          {LAYOUT_OPTIONS.map(opt => (
            <button
              key={opt.cols}
              className={`layout-btn ${cols === opt.cols ? 'active' : ''}`}
              onClick={() => { setCols(opt.cols); setPage(0); }}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            {filtered.length} cameras | Page {page + 1}/{totalPages || 1}
          </span>
          <button className="layout-btn" onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}>◀</button>
          <button className="layout-btn" onClick={() => setPage(Math.min(totalPages - 1, page + 1))} disabled={page >= totalPages - 1}>▶</button>
        </div>
      </div>

      {/* Video Grid */}
      <div className={`video-grid cols-${cols}`}>
        {paged.map(cam => (
          <CameraFeed key={cam.id} feed={cam} large={cols === 1} />
        ))}
        {paged.length === 0 && (
          <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
            No cameras found. Try adjusting your filters.
          </div>
        )}
      </div>
    </div>
  );
}
