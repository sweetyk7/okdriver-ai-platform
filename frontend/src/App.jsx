import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import LiveViewPage from './pages/LiveViewPage';
import CameraRegistryPage from './pages/CameraRegistryPage';
import WatchlistPage from './pages/WatchlistPage';
import AnalyticsPage from './pages/AnalyticsPage';
import RecordingsPage from './pages/RecordingsPage';
import SettingsPage from './pages/SettingsPage';
import './App.css';

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/live" element={<LiveViewPage />} />
            <Route path="/cameras" element={<CameraRegistryPage />} />
            <Route path="/watchlist" element={<WatchlistPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/recordings" element={<RecordingsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
