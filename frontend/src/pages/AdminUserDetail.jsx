import React, { useEffect, useState } from 'react';
import * as api from '../services/api';
import './AdminDashboard.css';

export default function AdminUserDetail({ userId, onNavigateBack = () => {} }) {

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadUser();
  }, [userId]);

  const loadUser = async () => {
    try {
      setLoading(true);
      setError('');

      const data = await api.getAdminUser(userId);
      setUser(data);
    } catch (err) {
      setError(err.message || 'Failed to load user details.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-page">
        <div className="admin-loading">Loading user details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-page">
        <button
          type="button"
          className="admin-back-btn"
          onClick={() => onNavigateBack()}
        >
          ← Back to Users
        </button>

        <div className="admin-error">{error}</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="admin-page">
        <button
          type="button"
          className="admin-back-btn"
          onClick={() => onNavigateBack()}
        >
          ← Back to Users
        </button>

        <div className="admin-empty">User not found.</div>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <div className="admin-page-header">
        <h1>User Details</h1>

        <button
          type="button"
          className="admin-back-btn"
          onClick={() => onNavigateBack()}
        >
          ← Back to Users
        </button>
      </div>

      <div className="admin-user-info">
        <div className="admin-info-card">
          <p><strong>Name:</strong> {user.full_name || 'N/A'}</p>
          <p><strong>Email:</strong> {user.email || 'N/A'}</p>
          <p><strong>Role:</strong> {user.role || 'N/A'}</p>
        </div>

        <div className="admin-info-card">
          <p>
            <strong>Documents:</strong> {user.document_count ?? 0}
          </p>
          <p>
            <strong>Queries:</strong> {user.query_count ?? 0}
          </p>
        </div>

        <div className="admin-info-card">
          <p>
            <strong>Created:</strong>{' '}
            {user.created_at
              ? new Date(user.created_at).toLocaleString()
              : 'N/A'}
          </p>
        </div>
      </div>

      <section className="admin-section">
        <div className="admin-section-header">
          <h2>User Documents</h2>
        </div>

        {user.documents && user.documents.length > 0 ? (
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Created</th>
                </tr>
              </thead>

              <tbody>
                {user.documents.map((document) => (
                  <tr key={document.id}>
                    <td>{document.filename || 'N/A'}</td>
                    <td>{document.file_type || 'N/A'}</td>
                    <td>{document.status || 'N/A'}</td>
                    <td>
                      {document.created_at
                        ? new Date(
                            document.created_at
                          ).toLocaleString()
                        : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="admin-empty">
            This user has no documents.
          </div>
        )}
      </section>
    </div>
  );
}