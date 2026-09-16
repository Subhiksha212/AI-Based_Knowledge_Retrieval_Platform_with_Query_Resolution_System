import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import UploadPage from './pages/UploadPage';
import ChatPage from './pages/ChatPage';
import AuthPage from './pages/AuthPage';
import HistoryPage from './pages/HistoryPage';
import AnalyticsPage from './pages/AnalyticsPage';
import KnowledgeGapPage from './pages/KnowledgeGapPage';
import AdminDashboard from './pages/AdminDashboard';
import AdminUsers from './pages/AdminUsers';
import AdminUserDetail from './pages/AdminUserDetail';
import AdminDocuments from './pages/AdminDocuments';
import AdminAnalytics from './pages/AdminAnalytics';
import { useAuth } from './context/Authcontext';
import * as api from './services/api';
import './App.css';

function App() {
  const { user, isLoggedIn, loading: authLoading, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('upload');
  const [adminUserId, setAdminUserId] = useState(null);
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

  if (!isLoggedIn || !user) {
    return <AuthPage />;
  }

  const isAdmin = user?.role === 'Admin';

  const navigateToAdmin = (tab) => {
    if (isAdmin) {
      setActiveTab(tab);
    }
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'upload':
        return <UploadPage onStartChat={() => setActiveTab('chat')} />;

      case 'chat':
        return <ChatPage />;

      case 'history':
        return <HistoryPage />;

      case 'analytics':
        return <AnalyticsPage onNavigateToGaps={() => setActiveTab('gaps')} />;

      case 'gaps':
        return <KnowledgeGapPage onIngest={() => setActiveTab('upload')} />;

      case 'admin':
        return isAdmin ? (
          <AdminDashboard onNavigate={navigateToAdmin} />
        ) : (
          <UploadPage onStartChat={() => setActiveTab('chat')} />
        );

      case 'admin-users':
        return isAdmin ? (
          <AdminUsers
            onNavigateBack={() => setActiveTab('admin')}
            onNavigateToUser={(userId) => {
              setAdminUserId(userId);
              setActiveTab('admin-user-detail');
            }}
          />
        ) : (
          <UploadPage onStartChat={() => setActiveTab('chat')} />
        );

      case 'admin-user-detail':
        return isAdmin ? (
          <AdminUserDetail
            userId={adminUserId}
            onNavigateBack={() => setActiveTab('admin-users')}
          />
        ) : (
          <UploadPage onStartChat={() => setActiveTab('chat')} />
        );

      case 'admin-documents':
        return isAdmin ? (
          <AdminDocuments onNavigateBack={() => setActiveTab('admin')} />
        ) : (
          <UploadPage onStartChat={() => setActiveTab('chat')} />
        );

      case 'admin-analytics':
        return isAdmin ? (
          <AdminAnalytics onNavigateBack={() => setActiveTab('admin')} />
        ) : (
          <UploadPage onStartChat={() => setActiveTab('chat')} />
        );

      default:
        return <UploadPage onStartChat={() => setActiveTab('chat')} />;
    }
  };

  return (
    <div className="main-app">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        mockMode={mockMode}
        user={user}
        onLogout={logout}
      />

      <main className="main-content">{renderActivePage()}</main>
    </div>
  );
}

export default App;
