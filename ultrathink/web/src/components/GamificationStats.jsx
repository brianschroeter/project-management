import { ProgressRing } from './ProgressRing'
import { theme } from '../styles/theme'

/**
 * Gamification Stats Display
 * Shows XP, level, streak in a unified, organized grid
 */
export function GamificationStats({ stats, xpProgress, isDark = false }) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
      gap: '1rem',
      width: '100%'
    }}>
      {/* Level Card */}
      <div className="stat-card-unified hover-lift" style={{
        padding: '1.25rem',
        background: isDark ? theme.dark.bg.secondary : 'white',
        borderRadius: '1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        boxShadow: isDark ? '0 2px 12px rgba(0,0,0,0.3)' : '0 2px 12px rgba(0,0,0,0.08)',
        border: `2px solid transparent`,
        backgroundClip: 'padding-box',
        position: 'relative'
      }}>
        <div style={{
          width: '3.5rem',
          height: '3.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: theme.gamification.level.gradient,
          borderRadius: '0.75rem',
          fontSize: '1.75rem',
          fontWeight: 700,
          color: 'white',
          boxShadow: '0 4px 12px rgba(245, 158, 11, 0.3)',
          flexShrink: 0
        }}>
          {stats.level}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: '0.75rem',
            fontWeight: 600,
            color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: '0.25rem'
          }}>
            Level
          </div>
          <div style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            color: isDark ? theme.dark.text.primary : theme.light.text.primary,
            lineHeight: 1
          }}>
            Level {stats.level}
          </div>
        </div>
      </div>

      {/* XP Card with Progress */}
      <div className="stat-card-unified hover-lift" style={{
        padding: '1.25rem',
        background: isDark ? theme.dark.bg.secondary : 'white',
        borderRadius: '1rem',
        boxShadow: isDark ? '0 2px 12px rgba(0,0,0,0.3)' : '0 2px 12px rgba(0,0,0,0.08)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
          <div style={{
            width: '3.5rem',
            height: '3.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: theme.gamification.xp.gradient,
            borderRadius: '0.75rem',
            fontSize: '1.75rem',
            boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)',
            flexShrink: 0
          }}>
            ⚡
          </div>
          <div style={{ flex: 1 }}>
            <div style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '0.25rem'
            }}>
              Experience
            </div>
            <div style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              color: isDark ? theme.dark.text.primary : theme.light.text.primary,
              lineHeight: 1
            }}>
              {stats.xp} XP
            </div>
          </div>
        </div>
        {/* Inline Progress Bar */}
        <div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '0.5rem'
          }}>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              color: isDark ? theme.dark.text.muted : theme.light.text.muted
            }}>
              Progress to Level {xpProgress.level + 1}
            </span>
            <span style={{
              fontSize: '0.75rem',
              color: isDark ? theme.dark.text.muted : theme.light.text.muted
            }}>
              {Math.round(xpProgress.progress)}%
            </span>
          </div>
          <div style={{
            height: '6px',
            background: isDark ? 'rgba(255,255,255,0.1)' : '#e2e8f0',
            borderRadius: '9999px',
            overflow: 'hidden'
          }}>
            <div
              style={{
                height: '100%',
                width: `${xpProgress.progress}%`,
                background: theme.gamification.xp.gradient,
                transition: 'width 0.5s ease',
                borderRadius: '9999px'
              }}
            />
          </div>
        </div>
      </div>

      {/* Streak Card */}
      <div className="stat-card-unified hover-lift" style={{
        padding: '1.25rem',
        background: isDark ? theme.dark.bg.secondary : 'white',
        borderRadius: '1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        boxShadow: isDark ? '0 2px 12px rgba(0,0,0,0.3)' : '0 2px 12px rgba(0,0,0,0.08)'
      }}>
        <div style={{
          width: '3.5rem',
          height: '3.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: theme.gamification.streak.gradient,
          borderRadius: '0.75rem',
          fontSize: '1.75rem',
          boxShadow: '0 4px 12px rgba(239, 68, 68, 0.3)',
          flexShrink: 0
        }}>
          🔥
        </div>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: '0.75rem',
            fontWeight: 600,
            color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: '0.25rem'
          }}>
            Streak
          </div>
          <div style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            color: isDark ? theme.dark.text.primary : theme.light.text.primary,
            lineHeight: 1,
            display: 'flex',
            alignItems: 'baseline',
            gap: '0.5rem'
          }}>
            {stats.currentStreak}
            <span style={{
              fontSize: '0.875rem',
              fontWeight: 600,
              color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
            }}>
              days
            </span>
          </div>
        </div>
      </div>

      {/* Tasks Completed Card */}
      <div className="stat-card-unified hover-lift" style={{
        padding: '1.25rem',
        background: isDark ? theme.dark.bg.secondary : 'white',
        borderRadius: '1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        boxShadow: isDark ? '0 2px 12px rgba(0,0,0,0.3)' : '0 2px 12px rgba(0,0,0,0.08)'
      }}>
        <div style={{
          width: '3.5rem',
          height: '3.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          borderRadius: '0.75rem',
          fontSize: '1.75rem',
          fontWeight: 700,
          color: 'white',
          boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
          flexShrink: 0
        }}>
          ✓
        </div>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: '0.75rem',
            fontWeight: 600,
            color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: '0.25rem'
          }}>
            Tasks Done
          </div>
          <div style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            color: isDark ? theme.dark.text.primary : theme.light.text.primary,
            lineHeight: 1
          }}>
            {stats.tasksCompleted}
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * XP Progress Bar with Level Info
 * @deprecated - Now integrated into GamificationStats component
 * Kept for backwards compatibility
 */
export function XPProgressBar({ xpProgress }) {
  return null
}

/**
 * Level Up Modal
 */
export function LevelUpModal({ level, onClose }) {
  return (
    <div className="level-up-modal" onClick={onClose}>
      <div className="level-up-content" onClick={(e) => e.stopPropagation()}>
        <div className="level-up-icon">🎉</div>
        <div className="level-up-title">Level Up!</div>
        <div className="level-up-subtitle">
          You've reached Level {level}
        </div>
        <button className="level-up-close" onClick={onClose}>
          Awesome!
        </button>
      </div>
    </div>
  )
}
