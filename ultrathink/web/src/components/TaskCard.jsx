import { useState, useEffect } from 'react'
import axios from 'axios'
import { EnergyBadge } from './EnergySelector'
import { theme, getEnergyTheme } from '../styles/theme'
import { ChevronDown, ChevronUp, ExternalLink, CheckCircle, Copy, Check } from 'lucide-react'
import { ClarifyingQuestions } from './ClarifyingQuestions'

const API_BASE = 'http://192.168.1.87:8001'

/**
 * Enhanced Task Card Component
 * Features: Expand/collapse, energy badges, TickTick linking, quick actions
 */
export function TaskCard({
  task,
  onComplete,
  onExpand,
  isDark = false,
  showEmailBadge = true,
  showClarifyButton = false,
  onClarify
}) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isCompleting, setIsCompleting] = useState(false)
  const [clarifyingData, setClarifyingData] = useState(null)
  const [loadingClarifying, setLoadingClarifying] = useState(false)
  const [showClarifying, setShowClarifying] = useState(false)
  const [copied, setCopied] = useState(false)
  const [showToast, setShowToast] = useState(false)
  const [toastMessage, setToastMessage] = useState('')

  const insights = task.ai_insights || {}
  const energyLevel = insights.energy_level || 'medium'
  const energyTheme = getEnergyTheme(energyLevel, isDark)

  // Fetch clarifying questions when task is expanded
  useEffect(() => {
    if (isExpanded && !clarifyingData && task.id) {
      fetchClarifyingQuestions()
    }
  }, [isExpanded, task.id])

  const fetchClarifyingQuestions = async () => {
    setLoadingClarifying(true)
    try {
      const response = await axios.get(`${API_BASE}/tasks/${task.id}/clarifying-questions`)
      setClarifyingData(response.data)
      // Auto-show clarifying questions if task is vague
      if (response.data.is_vague && (!response.data.existing_answers || Object.keys(response.data.existing_answers).length === 0)) {
        setShowClarifying(true)
      }
    } catch (error) {
      console.error('Error fetching clarifying questions:', error)
    } finally {
      setLoadingClarifying(false)
    }
  }

  const handleSaveClarifyingAnswers = async (taskId, answers) => {
    try {
      await axios.post(`${API_BASE}/tasks/${taskId}/clarifying-answers`, answers)
      setShowClarifying(false)
      // Refetch to get updated data
      await fetchClarifyingQuestions()
    } catch (error) {
      console.error('Error saving clarifying answers:', error)
      throw error
    }
  }

  const handleComplete = async () => {
    if (isCompleting) return
    if (!confirm('Mark this task as complete?')) return

    setIsCompleting(true)
    try {
      await onComplete(task.id)
    } finally {
      setIsCompleting(false)
    }
  }

  const handleExpand = () => {
    const newExpanded = !isExpanded
    setIsExpanded(newExpanded)
    if (newExpanded && onExpand) {
      onExpand(task)
    }
  }

  // Copy task ID to clipboard
  const copyTaskId = async () => {
    try {
      await navigator.clipboard.writeText(task.id)
      setCopied(true)
      showToastNotification('Task ID copied! You can paste this in TickTick search if the link doesn\'t work.')
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy task ID:', error)
      showToastNotification('Failed to copy. Task ID: ' + task.id, true)
    }
  }

  // Show toast notification
  const showToastNotification = (message, isError = false) => {
    setToastMessage(message)
    setShowToast(true)
    setTimeout(() => setShowToast(false), isError ? 5000 : 3000)
  }

  // Open task directly in TickTick
  const openTickTickLink = async (e) => {
    e.preventDefault()

    // DEBUG: Log task data to diagnose projectId issue
    console.log('TaskCard - Full task object:', task)
    console.log('TaskCard - task.projectId:', task.projectId)
    console.log('TaskCard - task.id:', task.id)

    // Construct direct task URL with projectId
    const directTaskUrl = task.projectId
      ? `https://ticktick.com/webapp/#p/${task.projectId}/tasks/${task.id}`
      : `https://ticktick.com/webapp/#/tasks/${task.id}`

    console.log('TaskCard - Constructed URL:', directTaskUrl)

    const newWindow = window.open(directTaskUrl, '_blank', 'noopener,noreferrer')

    if (!newWindow) {
      showToastNotification('Popup blocked! Please allow popups for this site.', true)
      return
    }

    showToastNotification('Opening task in TickTick...', false)
  }

  // TickTick deep link
  const ticktickLink = task.projectId
    ? `https://ticktick.com/webapp/#p/${task.projectId}/tasks/${task.id}`
    : `https://ticktick.com/webapp/#/tasks/${task.id}`

  return (
    <div
      className="task-card hover-lift smooth-transition animate-fade-in"
      style={{
        padding: '1rem',
        background: isDark ? theme.dark.bg.secondary : 'white',
        borderRadius: '0.75rem',
        boxShadow: isDark
          ? '0 2px 8px rgba(0,0,0,0.3)'
          : '0 2px 8px rgba(0,0,0,0.1)',
        borderLeft: `4px solid ${energyTheme.base}`,
        transition: 'all 0.2s ease'
      }}
    >
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: '0.75rem',
        marginBottom: '0.75rem'
      }}>
        <div style={{ flex: 1 }}>
          <h3 style={{
            margin: 0,
            fontSize: '1rem',
            fontWeight: 600,
            color: isDark ? theme.dark.text.primary : theme.light.text.primary,
            marginBottom: '0.5rem'
          }}>
            {task.title}
          </h3>

          {/* Meta info */}
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.5rem',
            alignItems: 'center'
          }}>
            <EnergyBadge level={energyLevel} isDark={isDark} />

            {insights.estimated_minutes && (
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.25rem 0.5rem',
                background: isDark ? theme.dark.bg.tertiary : theme.light.bg.secondary,
                borderRadius: '9999px',
                fontSize: '0.75rem',
                color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
              }}>
                <span>⏱️</span>
                <span>{insights.estimated_minutes}min</span>
              </div>
            )}

            {insights.priority_score && (
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.25rem 0.5rem',
                background: isDark ? theme.dark.bg.tertiary : theme.light.bg.secondary,
                borderRadius: '9999px',
                fontSize: '0.75rem',
                color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
              }}>
                <span>📊</span>
                <span>{Math.round(insights.priority_score)}/100</span>
              </div>
            )}

            {/* Email badge */}
            {showEmailBadge && task.email_source && (
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.25rem 0.5rem',
                background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                color: 'white',
                borderRadius: '9999px',
                fontSize: '0.75rem',
                fontWeight: 600
              }}>
                <span>📧</span>
                <span>{task.email_source}</span>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          alignItems: 'flex-start'
        }}>
          <button
            onClick={handleComplete}
            disabled={isCompleting}
            className="hover-scale smooth-transition"
            style={{
              padding: '0.5rem',
              background: 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: isCompleting ? 'not-allowed' : 'pointer',
              opacity: isCompleting ? 0.5 : 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title="Mark as complete"
          >
            <CheckCircle size={20} />
          </button>

          <button
            onClick={handleExpand}
            className="hover-scale smooth-transition"
            style={{
              padding: '0.5rem',
              background: isDark ? theme.dark.bg.tertiary : theme.light.bg.secondary,
              color: isDark ? theme.dark.text.primary : theme.light.text.primary,
              border: 'none',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
        </div>
      </div>

      {/* Vague task indicator in collapsed view */}
      {!isExpanded && clarifyingData && clarifyingData.is_vague && (!clarifyingData.existing_answers || Object.keys(clarifyingData.existing_answers).length === 0) && (
        <div style={{
          padding: '0.75rem',
          background: isDark
            ? 'rgba(251, 191, 36, 0.1)'
            : 'rgba(251, 191, 36, 0.05)',
          borderLeft: `3px solid ${theme.energy.medium}`,
          borderRadius: '0.5rem',
          fontSize: '0.875rem',
          marginBottom: '0.5rem'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: isDark ? theme.dark.text.primary : theme.light.text.primary,
            fontWeight: 600
          }}>
            <span>💡</span>
            <span>This task needs clarification</span>
          </div>
          <div style={{
            marginTop: '0.25rem',
            fontSize: '0.8125rem',
            color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
          }}>
            {clarifyingData.questions?.length || 0} questions to help you get started
          </div>
        </div>
      )}

      {/* First step hint */}
      {task.first_step && !isExpanded && (
        <div style={{
          padding: '0.75rem',
          background: isDark ? theme.dark.bg.tertiary : theme.light.bg.tertiary,
          borderRadius: '0.5rem',
          fontSize: '0.875rem',
          color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
          fontStyle: 'italic',
          display: 'flex',
          gap: '0.5rem'
        }}>
          <span>💡</span>
          <span>{task.first_step}</span>
        </div>
      )}

      {/* Expanded content */}
      {isExpanded && (
        <div
          className="animate-fade-in"
          style={{
            marginTop: '1rem',
            paddingTop: '1rem',
            borderTop: `1px solid ${isDark ? theme.dark.bg.tertiary : theme.light.bg.tertiary}`
          }}
        >
          {/* Description */}
          {task.content && (
            <div style={{
              marginBottom: '1rem',
              fontSize: '0.875rem',
              color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
              lineHeight: 1.6
            }}>
              {task.content}
            </div>
          )}

          {/* First step (in expanded view) */}
          {task.first_step && (
            <div style={{
              padding: '0.75rem',
              background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
              borderRadius: '0.5rem',
              fontSize: '0.875rem',
              color: '#92400e',
              marginBottom: '1rem',
              display: 'flex',
              gap: '0.5rem'
            }}>
              <span>💡</span>
              <div>
                <strong>First step:</strong> {task.first_step}
              </div>
            </div>
          )}

          {/* Email link */}
          {task.email_link && (
            <div style={{ marginBottom: '1rem' }}>
              <a
                href={task.email_link}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                  color: 'white',
                  textDecoration: 'none',
                  borderRadius: '0.5rem',
                  fontSize: '0.875rem',
                  fontWeight: 600
                }}
                className="hover-lift smooth-transition"
              >
                <span>📧</span>
                <span>View Original Email</span>
                <ExternalLink size={16} />
              </a>
              {task.email_has_attachments && (
                <span style={{
                  marginLeft: '0.5rem',
                  fontSize: '0.875rem',
                  color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
                }}>
                  📎 {task.email_attachment_count} attachment(s)
                </span>
              )}
            </div>
          )}

          {/* Clarifying Questions */}
          {clarifyingData && clarifyingData.is_vague && showClarifying && (
            <div style={{ marginBottom: '1rem' }}>
              <ClarifyingQuestions
                taskId={task.id}
                questions={clarifyingData.questions || []}
                existingAnswers={clarifyingData.existing_answers || {}}
                vaguenessScore={clarifyingData.vagueness_score || 0}
                reasons={clarifyingData.reasons || []}
                suggestions={clarifyingData.suggestions || ''}
                isDark={isDark}
                onAnswersSubmit={handleSaveClarifyingAnswers}
                onDismiss={() => setShowClarifying(false)}
              />
            </div>
          )}

          {/* Clarifying badge when answered */}
          {clarifyingData && clarifyingData.is_vague && !showClarifying && clarifyingData.existing_answers && Object.keys(clarifyingData.existing_answers).length > 0 && (
            <div
              onClick={() => setShowClarifying(true)}
              style={{
                marginBottom: '1rem',
                padding: '0.75rem',
                background: isDark
                  ? 'rgba(16, 185, 129, 0.1)'
                  : 'rgba(16, 185, 129, 0.05)',
                borderLeft: `3px solid ${theme.energy.low}`,
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              className="hover-lift"
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                color: isDark ? theme.dark.text.primary : theme.light.text.primary
              }}>
                <CheckCircle size={16} color={theme.energy.low} />
                <span style={{ fontWeight: 600 }}>
                  Clarifying questions answered ({Object.keys(clarifyingData.existing_answers).length})
                </span>
              </div>
              <div style={{
                marginTop: '0.25rem',
                fontSize: '0.8125rem',
                color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
              }}>
                Click to view or edit answers
              </div>
            </div>
          )}

          {/* Show clarifying button when vague but collapsed */}
          {clarifyingData && clarifyingData.is_vague && !showClarifying && (!clarifyingData.existing_answers || Object.keys(clarifyingData.existing_answers).length === 0) && (
            <button
              onClick={() => setShowClarifying(true)}
              className="hover-lift smooth-transition"
              style={{
                marginBottom: '1rem',
                width: '100%',
                padding: '0.75rem',
                background: `linear-gradient(135deg, ${theme.energy.medium}, ${theme.energy.high})`,
                color: 'white',
                border: 'none',
                borderRadius: '0.75rem',
                fontSize: '0.9375rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem'
              }}
            >
              <span>💡</span>
              <span>This task needs clarification - Answer {clarifyingData.questions?.length || 0} questions</span>
            </button>
          )}

          {/* Actions row */}
          <div style={{
            display: 'flex',
            gap: '0.75rem',
            flexWrap: 'wrap'
          }}>
            {/* TickTick link - opens task directly */}
            <button
              onClick={openTickTickLink}
              className="hover-lift smooth-transition"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 1rem',
                background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
              title="Open this task in TickTick"
            >
              <ExternalLink size={16} />
              <span>Open in TickTick</span>
            </button>

            {/* Copy Task ID button */}
            <button
              onClick={copyTaskId}
              className="hover-lift smooth-transition"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 1rem',
                background: copied
                  ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                  : isDark ? theme.dark.bg.tertiary : theme.light.bg.secondary,
                color: copied ? 'white' : (isDark ? theme.dark.text.primary : theme.light.text.primary),
                border: 'none',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              title="Just copy the task ID - manually search in TickTick if needed"
            >
              {copied ? <Check size={16} /> : <Copy size={16} />}
              <span>{copied ? 'Copied!' : 'Just Copy ID'}</span>
            </button>

            {/* Clarify button */}
            {showClarifyButton && onClarify && (
              <button
                onClick={() => onClarify(task)}
                className="hover-lift smooth-transition"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                <span>💡</span>
                <span>Get AI Help to Clarify</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Toast notification */}
      {showToast && (
        <div
          className="animate-fade-in"
          style={{
            position: 'fixed',
            bottom: '2rem',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 9999,
            padding: '1rem 1.5rem',
            background: toastMessage.includes('Failed') || toastMessage.includes('blocked')
              ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
              : 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
            color: 'white',
            borderRadius: '0.75rem',
            boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
            fontSize: '0.875rem',
            fontWeight: 600,
            maxWidth: '90%',
            textAlign: 'center',
            animation: 'slideUp 0.3s ease'
          }}
        >
          {toastMessage}
        </div>
      )}
    </div>
  )
}
