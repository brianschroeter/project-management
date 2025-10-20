import { useState, useEffect } from 'react'
import axios from 'axios'
import { Mail, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react'
import { theme } from '../styles/theme'

const API_BASE = 'http://192.168.1.87:8001'

/**
 * Email Setup Component
 * Allows users to connect Gmail and Outlook accounts for email-to-task conversion
 */
export function EmailSetup({ isDark }) {
  const [emailStatus, setEmailStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch email authentication status
  useEffect(() => {
    fetchEmailStatus()
  }, [])

  const fetchEmailStatus = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/email/status`)
      setEmailStatus(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load email status')
      console.error('Email status error:', err)
    } finally {
      setLoading(false)
    }
  }

  const initiateGmailAuth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/email/gmail/auth`)
      // Open OAuth URL in new window
      window.open(response.data.auth_url, '_blank', 'width=600,height=700')

      // Poll for status update
      setTimeout(() => {
        fetchEmailStatus()
      }, 5000)
    } catch (err) {
      if (err.response?.status === 501) {
        setError('Gmail OAuth is not configured. Please contact your administrator.')
      } else {
        setError('Failed to start Gmail authentication')
      }
      console.error('Gmail auth error:', err)
    }
  }

  const initiateOutlookAuth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/email/outlook/auth`)
      // Open OAuth URL in new window
      window.open(response.data.auth_url, '_blank', 'width=600,height=700')

      // Poll for status update
      setTimeout(() => {
        fetchEmailStatus()
      }, 5000)
    } catch (err) {
      if (err.response?.status === 501) {
        setError('Outlook OAuth is not configured. Please contact your administrator.')
      } else {
        setError('Failed to start Outlook authentication')
      }
      console.error('Outlook auth error:', err)
    }
  }

  if (loading) {
    return (
      <div style={{
        padding: '2rem',
        background: isDark ? theme.dark.bg.secondary : 'white',
        borderRadius: '1rem',
        boxShadow: isDark ? '0 2px 8px rgba(0,0,0,0.3)' : '0 2px 8px rgba(0,0,0,0.1)',
        textAlign: 'center'
      }}>
        <div className="spinner"></div>
        <p style={{ marginTop: '1rem', color: isDark ? theme.dark.text.secondary : theme.light.text.secondary }}>
          Loading email settings...
        </p>
      </div>
    )
  }

  return (
    <div style={{
      padding: '2rem',
      background: isDark ? theme.dark.bg.secondary : 'white',
      borderRadius: '1rem',
      boxShadow: isDark ? '0 2px 8px rgba(0,0,0,0.3)' : '0 2px 8px rgba(0,0,0,0.1)'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        marginBottom: '1.5rem'
      }}>
        <Mail size={28} color={isDark ? theme.dark.text.primary : theme.light.text.primary} />
        <h2 style={{
          margin: 0,
          fontSize: '1.5rem',
          fontWeight: 700,
          color: isDark ? theme.dark.text.primary : theme.light.text.primary
        }}>
          Email Integration
        </h2>
      </div>

      {error && (
        <div style={{
          padding: '1rem',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '0.5rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <AlertCircle size={20} color="#ef4444" />
          <span style={{ color: '#ef4444', fontSize: '0.875rem' }}>{error}</span>
        </div>
      )}

      <p style={{
        marginBottom: '2rem',
        color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
        lineHeight: '1.6'
      }}>
        Connect your email accounts to automatically create tasks from forwarded emails.
        When you forward an email to your Ultrathink address, we'll use AI to extract the task details.
      </p>

      {/* Gmail Account */}
      <div className="hover-lift" style={{
        padding: '1.5rem',
        background: isDark ? theme.dark.bg.tertiary : theme.light.bg.tertiary,
        borderRadius: '0.75rem',
        marginBottom: '1rem',
        border: `2px solid ${
          emailStatus?.gmail?.authenticated
            ? '#10b981'
            : isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
        }`
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'linear-gradient(135deg, #EA4335 0%, #FBBC04 100%)',
              borderRadius: '0.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem'
            }}>
              📧
            </div>
            <div>
              <h3 style={{
                margin: 0,
                fontSize: '1.125rem',
                fontWeight: 600,
                color: isDark ? theme.dark.text.primary : theme.light.text.primary
              }}>
                Gmail
              </h3>
              {emailStatus?.gmail?.authenticated && emailStatus?.gmail?.email && (
                <p style={{
                  margin: 0,
                  fontSize: '0.875rem',
                  color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
                }}>
                  {emailStatus.gmail.email}
                </p>
              )}
            </div>
          </div>

          {emailStatus?.gmail?.authenticated ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              background: 'rgba(16, 185, 129, 0.1)',
              borderRadius: '0.5rem'
            }}>
              <CheckCircle size={20} color="#10b981" />
              <span style={{ color: '#10b981', fontWeight: 600, fontSize: '0.875rem' }}>
                Connected
              </span>
            </div>
          ) : (
            <button
              onClick={initiateGmailAuth}
              className="hover-scale smooth-transition"
              style={{
                padding: '0.75rem 1.5rem',
                background: 'linear-gradient(135deg, #EA4335 0%, #FBBC04 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '0.875rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              Connect Gmail
              <ExternalLink size={16} />
            </button>
          )}
        </div>

        {emailStatus?.gmail?.authenticated && (
          <div style={{
            padding: '0.75rem',
            background: isDark ? 'rgba(16, 185, 129, 0.1)' : 'rgba(16, 185, 129, 0.05)',
            borderRadius: '0.5rem',
            fontSize: '0.875rem',
            color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
          }}>
            <strong style={{ color: isDark ? theme.dark.text.primary : theme.light.text.primary }}>
              Forward emails to:
            </strong>{' '}
            <code style={{
              padding: '0.25rem 0.5rem',
              background: isDark ? theme.dark.bg.secondary : 'white',
              borderRadius: '0.25rem',
              fontFamily: 'monospace'
            }}>
              tasks@ultrathink.app
            </code>
          </div>
        )}
      </div>

      {/* Outlook Account */}
      <div className="hover-lift" style={{
        padding: '1.5rem',
        background: isDark ? theme.dark.bg.tertiary : theme.light.bg.tertiary,
        borderRadius: '0.75rem',
        border: `2px solid ${
          emailStatus?.outlook?.authenticated
            ? '#10b981'
            : isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
        }`
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'linear-gradient(135deg, #0078D4 0%, #00BCF2 100%)',
              borderRadius: '0.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem'
            }}>
              💼
            </div>
            <div>
              <h3 style={{
                margin: 0,
                fontSize: '1.125rem',
                fontWeight: 600,
                color: isDark ? theme.dark.text.primary : theme.light.text.primary
              }}>
                Outlook / Microsoft 365
              </h3>
              {emailStatus?.outlook?.authenticated && emailStatus?.outlook?.email && (
                <p style={{
                  margin: 0,
                  fontSize: '0.875rem',
                  color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
                }}>
                  {emailStatus.outlook.email}
                </p>
              )}
            </div>
          </div>

          {emailStatus?.outlook?.authenticated ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              background: 'rgba(16, 185, 129, 0.1)',
              borderRadius: '0.5rem'
            }}>
              <CheckCircle size={20} color="#10b981" />
              <span style={{ color: '#10b981', fontWeight: 600, fontSize: '0.875rem' }}>
                Connected
              </span>
            </div>
          ) : (
            <button
              onClick={initiateOutlookAuth}
              className="hover-scale smooth-transition"
              style={{
                padding: '0.75rem 1.5rem',
                background: 'linear-gradient(135deg, #0078D4 0%, #00BCF2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '0.875rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              Connect Outlook
              <ExternalLink size={16} />
            </button>
          )}
        </div>

        {emailStatus?.outlook?.authenticated && (
          <div style={{
            padding: '0.75rem',
            background: isDark ? 'rgba(16, 185, 129, 0.1)' : 'rgba(16, 185, 129, 0.05)',
            borderRadius: '0.5rem',
            fontSize: '0.875rem',
            color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
          }}>
            <strong style={{ color: isDark ? theme.dark.text.primary : theme.light.text.primary }}>
              Forward emails to:
            </strong>{' '}
            <code style={{
              padding: '0.25rem 0.5rem',
              background: isDark ? theme.dark.bg.secondary : 'white',
              borderRadius: '0.25rem',
              fontFamily: 'monospace'
            }}>
              tasks@ultrathink.app
            </code>
          </div>
        )}
      </div>

      {/* Help Text */}
      <div style={{
        marginTop: '1.5rem',
        padding: '1rem',
        background: isDark ? 'rgba(59, 130, 246, 0.1)' : 'rgba(59, 130, 246, 0.05)',
        borderRadius: '0.5rem',
        border: '1px solid rgba(59, 130, 246, 0.2)'
      }}>
        <h4 style={{
          margin: '0 0 0.5rem 0',
          fontSize: '0.875rem',
          fontWeight: 600,
          color: isDark ? theme.dark.text.primary : theme.light.text.primary
        }}>
          📖 How it works
        </h4>
        <ul style={{
          margin: 0,
          paddingLeft: '1.25rem',
          fontSize: '0.875rem',
          color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
          lineHeight: '1.6'
        }}>
          <li>Connect your Gmail or Outlook account using the buttons above</li>
          <li>Forward any email to <code>tasks@ultrathink.app</code></li>
          <li>AI will extract the task title, description, and priority</li>
          <li>A new task will be created in TickTick automatically</li>
          <li>The task will include a link back to the original email</li>
        </ul>
      </div>
    </div>
  )
}
