import React, { useState } from 'react';
import robotLogo from '../assets/hero.jpg';


export default function Sidebar({
  activeTab,
  setActiveTab,
  mockMode,
  user,
  onLogout,
}) {
  const [profileOpen, setProfileOpen] = useState(false);


  const getInitial = () => {
    return (
      user?.full_name?.charAt(0) ||
      user?.email?.charAt(0) ||
      'U'
    ).toUpperCase();
  };


  return (
    <aside className="sidebar">

      {/* ==========================================================
          Brand Header
          ========================================================== */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '40px',
        }}
      >

        <div
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            overflow: 'hidden',
            border: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow:
              '0 0 16px var(--accent-purple-glow)',
            background: 'var(--bg-card)',
          }}
        >

          <img
            src={robotLogo}
            alt="RAG Robot Logo"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
          />

        </div>


        <div className="logo-text">

          <h2
            style={{
              fontSize: '1.25rem',
              fontWeight: 700,
              letterSpacing: '-0.02em',
              background:
                'linear-gradient(to right, #fff, var(--text-secondary))',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            QueryNest
          </h2>

          <span
            style={{
              fontSize: '0.7rem',
              color: 'var(--text-muted)',
              display: 'block',
              marginTop: '-2px',
            }}
          >
            KNOWLEDGE BASE CONSOLE
          </span>

        </div>

      </div>


      {/* ==========================================================
          Navigation
          ========================================================== */}
      <nav
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          flex: 1,
        }}
      >

        {/* Upload Documents */}

        <button
          type="button"
          onClick={() => setActiveTab('upload')}
          className={`btn ${
            activeTab === 'upload'
              ? 'btn-primary'
              : 'btn-secondary'
          }`}
          style={{
            justifyContent: 'flex-start',
            width: '100%',
            padding: '12px 16px',
            border:
              activeTab === 'upload'
                ? 'none'
                : '1px solid var(--border-color)',
            background:
              activeTab === 'upload'
                ? undefined
                : 'transparent',
          }}
        >

          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              flexShrink: 0,
            }}
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" />
          </svg>

          <span
            className="nav-label"
            style={{
              marginLeft: '8px',
            }}
          >
            Upload Documents
          </span>

        </button>


        {/* AI Chatbot */}

        <button
          type="button"
          onClick={() => setActiveTab('chat')}
          className={`btn ${
            activeTab === 'chat'
              ? 'btn-primary'
              : 'btn-secondary'
          }`}
          style={{
            justifyContent: 'flex-start',
            width: '100%',
            padding: '12px 16px',
            border:
              activeTab === 'chat'
                ? 'none'
                : '1px solid var(--border-color)',
            background:
              activeTab === 'chat'
                ? undefined
                : 'transparent',
          }}
        >

          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              flexShrink: 0,
            }}
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>

          <span
            className="nav-label"
            style={{
              marginLeft: '8px',
            }}
          >
            AI Chatbot
          </span>

        </button>


        {/* History & Statistics */}

        <button
          type="button"
          onClick={() => setActiveTab('history')}
          className={`btn ${
            activeTab === 'history'
              ? 'btn-primary'
              : 'btn-secondary'
          }`}
          style={{
            justifyContent: 'flex-start',
            width: '100%',
            padding: '12px 16px',
            border:
              activeTab === 'history'
                ? 'none'
                : '1px solid var(--border-color)',
            background:
              activeTab === 'history'
                ? undefined
                : 'transparent',
          }}
        >

          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              flexShrink: 0,
            }}
          >
            <rect x="18" y="3" width="4" height="18" />
            <rect x="10" y="8" width="4" height="13" />
            <rect x="2" y="13" width="4" height="8" />
          </svg>

          <span
            className="nav-label"
            style={{
              marginLeft: '8px',
            }}
          >
            History & Statistics
          </span>

        </button>


        {/* Analytics */}
        <button
          type="button"
          onClick={() => setActiveTab('analytics')}
          className={`btn ${activeTab === 'analytics' ? 'btn-primary' : 'btn-secondary'}`}
          style={{
            justifyContent: 'flex-start',
            width: '100%',
            padding: '12px 16px',
            border: activeTab === 'analytics' ? 'none' : '1px solid var(--border-color)',
            background: activeTab === 'analytics' ? undefined : 'transparent',
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="4" y1="19" x2="4" y2="10" />
            <line x1="10" y1="19" x2="10" y2="5" />
            <line x1="16" y1="19" x2="16" y2="13" />
            <line x1="22" y1="19" x2="22" y2="8" />
          </svg>
          <span className="nav-label" style={{ marginLeft: '8px' }}>Analytics</span>
        </button>

        {/* Knowledge Gaps */}
        <button
          type="button"
          onClick={() => setActiveTab('gaps')}
          className={`btn ${activeTab === 'gaps' ? 'btn-primary' : 'btn-secondary'}`}
          style={{
            justifyContent: 'flex-start',
            width: '100%',
            padding: '12px 16px',
            border: activeTab === 'gaps' ? 'none' : '1px solid var(--border-color)',
            background: activeTab === 'gaps' ? undefined : 'transparent',
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10.3 2.3 2.3 10.3a2 2 0 0 0 0 2.8l8.6 8.6a2 2 0 0 0 2.8 0l8-8a2 2 0 0 0 0-2.8l-8.6-8.6a2 2 0 0 0-2.8 0Z" />
            <line x1="8" y1="12" x2="12" y2="16" />
            <line x1="12" y1="8" x2="16" y2="12" />
          </svg>
          <span className="nav-label" style={{ marginLeft: '8px' }}>Knowledge Gaps</span>
        </button>

        {user?.role === 'Admin' && (
          <button
            type="button"
            onClick={() => setActiveTab('admin')}
            className={`btn ${activeTab.startsWith('admin') ? 'btn-primary' : 'btn-secondary'}`}
            style={{
              justifyContent: 'flex-start',
              width: '100%',
              padding: '12px 16px',
              border: activeTab.startsWith('admin') ? 'none' : '1px solid var(--border-color)',
              background: activeTab.startsWith('admin') ? undefined : 'transparent',
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 12l2-2 4 4L19 4l2 2-12 12z" />
              <path d="M5 20h14" />
            </svg>
            <span className="nav-label" style={{ marginLeft: '8px' }}>Admin Dashboard</span>
          </button>
        )}

        {/* ========================================================
            Logged-in User Profile
            ======================================================== */}

        {user && (
          <div className="sidebar-user-section">

            {/* Profile Button */}

            <button
              type="button"
              className="sidebar-user-button"
              onClick={() =>
                setProfileOpen(
                  (previous) => !previous
                )
              }
              aria-expanded={profileOpen}
              aria-label="Open user profile"
            >

              {/* Avatar */}

              <div className="sidebar-user-avatar">

                {user.avatar ? (
                  <img
                    src={user.avatar}
                    alt=""
                  />
                ) : (
                  <span>
                    {getInitial()}
                  </span>
                )}

              </div>


              {/* User information */}

              <div className="sidebar-user-info">

                <span className="sidebar-user-name">
                  {user.full_name}
                </span>

                <span className="sidebar-user-email">
                  {user.email}
                </span>

              </div>


              {/* Chevron */}

              <svg
                className={`sidebar-user-chevron ${
                  profileOpen
                    ? 'open'
                    : ''
                }`}
                width="15"
                height="15"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>

            </button>


            {/* ====================================================
                Profile Dropdown
                ==================================================== */}

            {profileOpen && (
              <div className="sidebar-user-menu show">

                {/* Logout only */}

                <button
                  type="button"
                  className="sidebar-logout-button"
                  onClick={async () => {
                    setProfileOpen(false);

                    try {
                      await onLogout();
                    } catch (error) {
                      console.error(
                        'Logout failed:',
                        error
                      );
                    }
                  }}
                >

                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M10 17l5-5-5-5" />
                    <path d="M15 12H3" />
                    <path d="M21 19V5a2 2 0 0 0-2-2h-6" />
                  </svg>

                  <span>
                    Sign Out
                  </span>

                </button>

              </div>
            )}

          </div>
        )}

      </nav>


      {/* ==========================================================
          Footer
          ========================================================== */}

      <div
        className="sidebar-footer-text"
        style={{
          marginTop: '24px',
          textAlign: 'center',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
        }}
      >
        RAG Workspace v1.0.0
      </div>

    </aside>
  );
}