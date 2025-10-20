import { ProgressRing } from './ProgressRing'
import { theme } from '../styles/theme'

/**
 * Gamification Stats Display
 * Shows XP, level, streak in a colorful dashboard
 */
export function GamificationStats({ stats, xpProgress }) {
  return (
    <div style={{
      display: 'flex',
      gap: '1rem',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap'
    }}>
      {/* Level Display */}
      <div className="level-container hover-lift" style={{ flex: '1 1 auto', minWidth: '140px' }}>
        <div className="level-badge">
          {stats.level}
        </div>
        <div className="level-info">
          <span className="level-label">Level</span>
          <span className="level-value">Level {stats.level}</span>
        </div>
      </div>

      {/* XP Display */}
      <div className="xp-container hover-lift" style={{ flex: '1 1 auto', minWidth: '160px' }}>
        <div className="xp-icon">⚡</div>
        <div className="xp-text">
          <span className="xp-label">Experience</span>
          <span className="xp-value">{stats.xp} XP</span>
        </div>
      </div>

      {/* Streak Display */}
      <div className="streak-container hover-lift" style={{ flex: '1 1 auto', minWidth: '140px' }}>
        <div className="streak-flame">🔥</div>
        <div className="streak-info">
          <span className="streak-label">Streak</span>
          <span className="streak-value">{stats.currentStreak}</span>
          <span className="streak-days">days</span>
        </div>
      </div>

      {/* Tasks Completed */}
      <div className="stat-card hover-lift" style={{
        flex: '1 1 auto',
        minWidth: '120px',
        padding: '1rem',
        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        borderRadius: '1rem',
        color: 'white',
        textAlign: 'center',
        boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)'
      }}>
        <div style={{ fontSize: '2rem', fontWeight: 700 }}>
          {stats.tasksCompleted}
        </div>
        <div style={{
          fontSize: '0.75rem',
          opacity: 0.9,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginTop: '0.25rem'
        }}>
          Tasks Done
        </div>
      </div>
    </div>
  )
}

/**
 * XP Progress Bar with Level Info
 */
export function XPProgressBar({ xpProgress }) {
  return (
    <div style={{
      padding: '1rem',
      background: 'white',
      borderRadius: '0.75rem',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '0.5rem'
      }}>
        <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#64748b' }}>
          Level {xpProgress.level}
        </span>
        <span style={{ fontSize: '0.875rem', color: '#64748b' }}>
          {xpProgress.currentXP} / {xpProgress.nextLevelXP} XP
        </span>
      </div>
      <div style={{
        height: '8px',
        background: '#e2e8f0',
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
      <div style={{
        marginTop: '0.5rem',
        textAlign: 'center',
        fontSize: '0.75rem',
        color: '#94a3b8'
      }}>
        {Math.round(xpProgress.progress)}% to Level {xpProgress.level + 1}
      </div>
    </div>
  )
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
