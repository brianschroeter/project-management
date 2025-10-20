import { useState } from 'react'
import { HelpCircle, CheckCircle, Send, Lightbulb, XCircle } from 'lucide-react'
import { theme } from '../styles/theme'

/**
 * ClarifyingQuestions Component
 * Displays AI-generated questions to help clarify vague tasks
 * Allows users to answer and save responses
 */
export function ClarifyingQuestions({
  taskId,
  questions = [],
  existingAnswers = {},
  vaguenessScore = 0,
  reasons = [],
  suggestions = '',
  isDark = false,
  onAnswersSubmit,
  onDismiss,
  compact = false
}) {
  const [answers, setAnswers] = useState(existingAnswers)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)

  const handleAnswerChange = (question, answer) => {
    setAnswers(prev => ({
      ...prev,
      [question]: answer
    }))
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      await onAnswersSubmit(taskId, answers)
    } finally {
      setIsSubmitting(false)
    }
  }

  const allQuestionsAnswered = questions.length > 0 &&
    questions.every(q => answers[q] && answers[q].trim().length > 0)

  if (!questions || questions.length === 0) {
    return null
  }

  // Compact mode for daily review
  if (compact) {
    return (
      <div style={{
        padding: '0.75rem',
        background: isDark
          ? 'rgba(251, 191, 36, 0.1)'
          : 'rgba(251, 191, 36, 0.05)',
        borderLeft: `3px solid ${theme.energy.medium}`,
        borderRadius: '0.5rem',
        fontSize: '0.875rem'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '0.5rem'
        }}>
          <HelpCircle size={16} color={theme.energy.medium} />
          <span style={{
            fontWeight: 600,
            color: isDark ? theme.dark.text.primary : theme.light.text.primary
          }}>
            This task needs clarification ({Math.round(vaguenessScore * 10)}/10)
          </span>
        </div>
        <div style={{
          color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
          fontSize: '0.8125rem',
          lineHeight: '1.4'
        }}>
          {questions.length} question{questions.length !== 1 ? 's' : ''} to help you get started
        </div>
      </div>
    )
  }

  // Full mode for task creation
  return (
    <div style={{
      padding: '1.5rem',
      background: isDark ? theme.dark.bg.secondary : 'white',
      borderRadius: '1rem',
      border: `2px solid ${theme.energy.medium}`,
      boxShadow: isDark
        ? '0 4px 12px rgba(0,0,0,0.3)'
        : '0 4px 12px rgba(0,0,0,0.1)'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        marginBottom: '1rem'
      }}>
        <div style={{ flex: 1 }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            marginBottom: '0.5rem'
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '0.75rem',
              background: `linear-gradient(135deg, ${theme.energy.medium}, ${theme.energy.high})`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <HelpCircle size={24} color="white" />
            </div>
            <div>
              <h3 style={{
                margin: 0,
                fontSize: '1.125rem',
                fontWeight: 700,
                color: isDark ? theme.dark.text.primary : theme.light.text.primary
              }}>
                Let's Clarify This Task
              </h3>
              <p style={{
                margin: 0,
                fontSize: '0.875rem',
                color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
              }}>
                Vagueness score: {Math.round(vaguenessScore * 10)}/10
              </p>
            </div>
          </div>

          {/* Reasons */}
          {reasons && reasons.length > 0 && (
            <div style={{
              marginTop: '1rem',
              padding: '0.75rem',
              background: isDark
                ? 'rgba(239, 68, 68, 0.1)'
                : 'rgba(239, 68, 68, 0.05)',
              borderRadius: '0.5rem',
              fontSize: '0.875rem'
            }}>
              <div style={{
                fontWeight: 600,
                color: isDark ? theme.dark.text.primary : theme.light.text.primary,
                marginBottom: '0.5rem'
              }}>
                Why this task is vague:
              </div>
              <ul style={{
                margin: 0,
                paddingLeft: '1.25rem',
                color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
                lineHeight: '1.6'
              }}>
                {reasons.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            style={{
              padding: '0.5rem',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
              borderRadius: '0.5rem',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={e => e.target.style.background = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)'}
            onMouseLeave={e => e.target.style.background = 'transparent'}
          >
            <XCircle size={20} />
          </button>
        )}
      </div>

      {/* Questions */}
      <div style={{ marginBottom: '1.5rem' }}>
        {questions.map((question, idx) => {
          const isAnswered = answers[question] && answers[question].trim().length > 0

          return (
            <div
              key={idx}
              style={{
                marginBottom: '1rem',
                padding: '1rem',
                background: isDark ? theme.dark.bg.tertiary : theme.light.bg.tertiary,
                borderRadius: '0.75rem',
                border: `2px solid ${
                  isAnswered
                    ? theme.energy.low
                    : isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
                }`,
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.75rem',
                marginBottom: '0.75rem'
              }}>
                <div style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: isAnswered
                    ? `linear-gradient(135deg, ${theme.energy.low}, ${theme.energy.medium})`
                    : isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  color: isAnswered ? 'white' : isDark ? theme.dark.text.secondary : theme.light.text.secondary,
                  flexShrink: 0
                }}>
                  {isAnswered ? <CheckCircle size={14} /> : idx + 1}
                </div>
                <label style={{
                  fontWeight: 600,
                  color: isDark ? theme.dark.text.primary : theme.light.text.primary,
                  fontSize: '0.9375rem',
                  lineHeight: '1.5'
                }}>
                  {question}
                </label>
              </div>
              <textarea
                value={answers[question] || ''}
                onChange={e => handleAnswerChange(question, e.target.value)}
                placeholder="Type your answer here..."
                rows={2}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: isDark ? theme.dark.bg.secondary : 'white',
                  border: `2px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                  borderRadius: '0.5rem',
                  color: isDark ? theme.dark.text.primary : theme.light.text.primary,
                  fontSize: '0.875rem',
                  fontFamily: 'inherit',
                  resize: 'vertical',
                  transition: 'all 0.2s ease'
                }}
                onFocus={e => {
                  e.target.style.borderColor = theme.energy.medium
                  e.target.style.outline = 'none'
                }}
                onBlur={e => {
                  e.target.style.borderColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
                }}
              />
            </div>
          )
        })}
      </div>

      {/* AI Suggestions */}
      {suggestions && (
        <div style={{
          marginBottom: '1.5rem',
          padding: '1rem',
          background: isDark
            ? 'rgba(59, 130, 246, 0.1)'
            : 'rgba(59, 130, 246, 0.05)',
          borderRadius: '0.75rem',
          border: '1px solid rgba(59, 130, 246, 0.2)'
        }}>
          <button
            onClick={() => setShowSuggestions(!showSuggestions)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              padding: 0,
              color: isDark ? theme.dark.text.primary : theme.light.text.primary,
              fontWeight: 600,
              fontSize: '0.875rem',
              marginBottom: showSuggestions ? '0.75rem' : 0
            }}
          >
            <Lightbulb size={18} color="#3b82f6" />
            AI Suggestion
            <span style={{ fontSize: '0.75rem', marginLeft: 'auto' }}>
              {showSuggestions ? '▼' : '▶'}
            </span>
          </button>
          {showSuggestions && (
            <div style={{
              color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
              fontSize: '0.875rem',
              lineHeight: '1.6'
            }}>
              {suggestions}
            </div>
          )}
        </div>
      )}

      {/* Submit Button */}
      <div style={{
        display: 'flex',
        gap: '0.75rem',
        justifyContent: 'flex-end'
      }}>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="hover-scale smooth-transition"
            style={{
              padding: '0.875rem 1.5rem',
              background: 'transparent',
              border: `2px solid ${isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)'}`,
              borderRadius: '0.75rem',
              color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
              fontWeight: 600,
              fontSize: '0.9375rem',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            Skip for Now
          </button>
        )}
        <button
          onClick={handleSubmit}
          disabled={!allQuestionsAnswered || isSubmitting}
          className={allQuestionsAnswered ? 'hover-scale smooth-transition' : ''}
          style={{
            padding: '0.875rem 1.5rem',
            background: allQuestionsAnswered
              ? `linear-gradient(135deg, ${theme.energy.low}, ${theme.energy.medium})`
              : isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
            border: 'none',
            borderRadius: '0.75rem',
            color: allQuestionsAnswered ? 'white' : isDark ? theme.dark.text.secondary : theme.light.text.secondary,
            fontWeight: 700,
            fontSize: '0.9375rem',
            cursor: allQuestionsAnswered ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            opacity: allQuestionsAnswered ? 1 : 0.5,
            transition: 'all 0.2s ease'
          }}
        >
          {isSubmitting ? (
            <>
              <div className="spinner" style={{ width: '16px', height: '16px' }}></div>
              Saving...
            </>
          ) : (
            <>
              <Send size={18} />
              Save Answers
            </>
          )}
        </button>
      </div>

      {/* Answer count indicator */}
      {!allQuestionsAnswered && (
        <div style={{
          marginTop: '1rem',
          textAlign: 'right',
          fontSize: '0.8125rem',
          color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
        }}>
          {Object.keys(answers).filter(k => answers[k] && answers[k].trim()).length} / {questions.length} questions answered
        </div>
      )}
    </div>
  )
}
