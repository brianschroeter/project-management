import { theme, getEnergyTheme } from '../styles/theme'

/**
 * Animated Energy Level Selector
 * Colorful gradient buttons for selecting energy level
 */
export function EnergySelector({ currentEnergy, onChange, isDark = false }) {
  const energyLevels = ['low', 'medium', 'high']

  return (
    <div className="energy-selector" style={{
      display: 'flex',
      gap: '0.75rem',
      padding: '0.5rem',
      background: isDark ? theme.dark.bg.secondary : theme.light.bg.secondary,
      borderRadius: '1rem',
      flexWrap: 'wrap'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        fontSize: '0.875rem',
        fontWeight: 600,
        color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
        paddingLeft: '0.5rem'
      }}>
        Current Energy:
      </div>

      {energyLevels.map(level => {
        const energyTheme = getEnergyTheme(level, isDark)
        const isActive = currentEnergy === level

        return (
          <button
            key={level}
            onClick={() => onChange(level)}
            className={`energy-btn ${isActive ? 'active' : ''} hover-lift smooth-transition`}
            style={{
              padding: '0.75rem 1.5rem',
              border: 'none',
              borderRadius: '0.75rem',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: isActive ? energyTheme.gradient : (isDark ? theme.dark.bg.tertiary : 'white'),
              color: isActive ? 'white' : (isDark ? theme.dark.text.primary : theme.light.text.primary),
              boxShadow: isActive ? energyTheme.shadow : (isDark ? '0 2px 4px rgba(0,0,0,0.3)' : '0 2px 4px rgba(0,0,0,0.1)'),
              transform: isActive ? 'scale(1.05)' : 'scale(1)',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              if (!isActive) {
                e.currentTarget.style.background = energyTheme.gradient
                e.currentTarget.style.color = 'white'
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive) {
                e.currentTarget.style.background = isDark ? theme.dark.bg.tertiary : 'white'
                e.currentTarget.style.color = isDark ? theme.dark.text.primary : theme.light.text.primary
              }
            }}
          >
            <span style={{ fontSize: '1.25rem' }}>{energyTheme.emoji}</span>
            <span style={{ textTransform: 'capitalize' }}>{level}</span>
          </button>
        )
      })}
    </div>
  )
}

/**
 * Compact Energy Badge
 * Shows energy level as a small badge
 */
export function EnergyBadge({ level, isDark = false }) {
  const energyTheme = getEnergyTheme(level, isDark)

  return (
    <div
      className="energy-badge"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.25rem',
        padding: '0.25rem 0.5rem',
        borderRadius: '9999px',
        background: energyTheme.gradient,
        color: 'white',
        fontSize: '0.75rem',
        fontWeight: 600
      }}
    >
      <span>{energyTheme.emoji}</span>
      <span style={{ textTransform: 'capitalize' }}>{level}</span>
    </div>
  )
}
