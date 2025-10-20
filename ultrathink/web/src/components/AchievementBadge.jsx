/**
 * Achievement Badge Component
 * Displays unlocked and locked achievements
 */
export function AchievementBadge({ achievement, unlocked = false, onClick }) {
  return (
    <div
      className={`achievement-card ${unlocked ? '' : 'locked'} hover-lift`}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <div className="achievement-card-icon">
        {unlocked ? achievement.icon : '🔒'}
      </div>
      <div className="achievement-card-title">
        {achievement.name}
      </div>
      <div className="achievement-card-description">
        {achievement.description}
      </div>
      {unlocked && (
        <div className={`achievement-badge ${achievement.tier}`}>
          {achievement.tier}
        </div>
      )}
    </div>
  )
}

/**
 * Inline achievement badge (for notifications)
 */
export function InlineAchievementBadge({ achievement }) {
  return (
    <div className={`achievement-badge ${achievement.tier} animate-bounce`}>
      <span className="achievement-icon">{achievement.icon}</span>
      <span>{achievement.name}</span>
    </div>
  )
}
