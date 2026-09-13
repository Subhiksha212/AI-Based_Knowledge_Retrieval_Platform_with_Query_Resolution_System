import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import UploadPage from './pages/UploadPage';
import ChatPage from './pages/ChatPage';
import AuthPage from './pages/AuthPage';
import HistoryPage from './pages/HistoryPage';
import AnalyticsPage from './pages/AnalyticsPage';
import KnowledgeGapPage from './pages/KnowledgeGapPage';
import { useAuth } from './context/Authcontext';
import * as api from './services/api';
import './App.css';

function App() {
  const { user, isLoggedIn, loading: authLoading, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('upload');
  const [mockMode] = useState(api.getMockMode());

  if (authLoading) {
    return (
      <div className="app-auth-loading">
        <div className="app-auth-loading-content">
          <div className="app-auth-loading-title">Loading QueryNest...</div>
          <div className="app-auth-loading-text">Verifying your session</div>
        </div>
      </div>
    );
  }

  if (!isLoggedIn || !user) return <AuthPage />;

  const show = (tab) => ({
    display: activeTab === tab ? 'block' : 'none',
    height: '100%',
  });

  return (
    <div className="main-app">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        mockMode={mockMode}
        user={user}
        onLogout={logout}
      />

      <main className="main-content">
        <div style={show('upload')}>
          <UploadPage onStartChat={() => setActiveTab('chat')} />
        </div>
        <div style={show('chat')}><ChatPage /></div>
        <div style={show('history')}><HistoryPage /></div>
        <div style={show('analytics')}>
          <AnalyticsPage onNavigateToGaps={() => setActiveTab('gaps')} />
        </div>
        <div style={show('gaps')}>
          <KnowledgeGapPage onIngest={() => setActiveTab('upload')} />
        </div>
      </main>
    </div>
  );
}

export default App;
