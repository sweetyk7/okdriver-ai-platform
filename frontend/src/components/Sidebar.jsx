import React from 'react';
import { NavLink } from 'react-router-dom';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: '🏠' },
  { path: '/live', label: 'Live View', icon: '📹' },
  { path: '/cameras', label: 'Cameras', icon: '📷' },
  { path: '/watchlist', label: 'Watchlist', icon: '🚨' },
  { path: '/analytics', label: 'Analytics', icon: '📊' },
  { path: '/recordings', label: 'Recordings', icon: '💾' },
  { path: '/settings', label: 'Settings', icon: '⚙️' },
];

export default function Sidebar({ collapsed, onToggle }) {
  return (
    <nav className={`app-sidebar glass-panel ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="brand">
          {!collapsed && <span>🚔 okDriver AI</span>}
          {collapsed && <span>🚔</span>}
        </div>
        <button className="sidebar-toggle" onClick={onToggle}>
          {collapsed ? '→' : '←'}
        </button>
      </div>

      <div className="sidebar-nav">
        {NAV_ITEMS.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            end={item.path === '/'}
          >
            <span className="nav-icon">{item.icon}</span>
            {!collapsed && <span className="nav-label">{item.label}</span>}
          </NavLink>
        ))}
      </div>

      <div className="sidebar-footer">
        {!collapsed && (
          <div className="sidebar-user">
            <div className="user-avatar">AD</div>
            <div>
              <div style={{ fontWeight: 600, fontSize: '13px' }}>Admin</div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>System Admin</div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
