/**
 * Ultrathink Theme System
 * Colorful, engaging, ADHD-friendly color palette with gradients
 */

export const theme = {
  // Energy Level Colors with Gradients
  energy: {
    low: {
      base: '#4ade80',
      gradient: 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)',
      shadow: '0 4px 20px rgba(74, 222, 128, 0.3)',
      emoji: '🟢',
      label: 'Low Energy',
      description: 'Light tasks, routine work'
    },
    medium: {
      base: '#fbbf24',
      gradient: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
      shadow: '0 4px 20px rgba(251, 191, 36, 0.3)',
      emoji: '🟡',
      label: 'Medium Energy',
      description: 'Moderate focus required'
    },
    high: {
      base: '#f43f5e',
      gradient: 'linear-gradient(135deg, #f43f5e 0%, #a855f7 100%)',
      shadow: '0 4px 20px rgba(244, 63, 94, 0.3)',
      emoji: '🔴',
      label: 'High Energy',
      description: 'Deep focus, creative work'
    }
  },

  // Gamification Colors
  gamification: {
    xp: {
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
      text: '#3b82f6'
    },
    level: {
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
      text: '#f59e0b'
    },
    streak: {
      gradient: 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)',
      text: '#ef4444'
    },
    achievement: {
      gold: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
      silver: 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)',
      bronze: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)'
    }
  },

  // Priority Colors
  priority: {
    urgent: {
      bg: '#fee2e2',
      border: '#f87171',
      text: '#991b1b'
    },
    high: {
      bg: '#fef3c7',
      border: '#fbbf24',
      text: '#92400e'
    },
    medium: {
      bg: '#dbeafe',
      border: '#60a5fa',
      text: '#1e40af'
    },
    low: {
      bg: '#f3f4f6',
      border: '#9ca3af',
      text: '#374151'
    }
  },

  // Status Colors
  status: {
    completed: {
      bg: '#d1fae5',
      border: '#34d399',
      text: '#065f46'
    },
    inProgress: {
      bg: '#dbeafe',
      border: '#60a5fa',
      text: '#1e40af'
    },
    blocked: {
      bg: '#ffe4e6',
      border: '#fb7185',
      text: '#881337'
    },
    stale: {
      bg: '#fef3c7',
      border: '#fbbf24',
      text: '#92400e'
    }
  },

  // Dark Mode Colors
  dark: {
    bg: {
      primary: '#0f172a',
      secondary: '#1e293b',
      tertiary: '#334155'
    },
    text: {
      primary: '#f1f5f9',
      secondary: '#cbd5e1',
      muted: '#94a3b8'
    },
    accent: {
      purple: '#a855f7',
      blue: '#3b82f6',
      pink: '#ec4899'
    },
    energy: {
      low: {
        gradient: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
        shadow: '0 4px 20px rgba(34, 197, 94, 0.4)'
      },
      medium: {
        gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        shadow: '0 4px 20px rgba(245, 158, 11, 0.4)'
      },
      high: {
        gradient: 'linear-gradient(135deg, #ec4899 0%, #a855f7 100%)',
        shadow: '0 4px 20px rgba(236, 72, 153, 0.4)'
      }
    }
  },

  // Light Mode Colors
  light: {
    bg: {
      primary: '#ffffff',
      secondary: '#f8fafc',
      tertiary: '#f1f5f9'
    },
    text: {
      primary: '#0f172a',
      secondary: '#475569',
      muted: '#94a3b8'
    }
  },

  // Spacing
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem'
  },

  // Border Radius
  radius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
    full: '9999px'
  },

  // Animations
  animations: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms'
    },
    easing: {
      default: 'cubic-bezier(0.4, 0, 0.2, 1)',
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
    }
  },

  // Shadows
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
    glow: '0 0 20px rgba(147, 51, 234, 0.3)'
  }
}

// Helper function to get energy theme
export const getEnergyTheme = (level, isDark = false) => {
  const energyLevel = level?.toLowerCase() || 'medium'
  if (isDark) {
    return theme.dark.energy[energyLevel] || theme.dark.energy.medium
  }
  return theme.energy[energyLevel] || theme.energy.medium
}

// Helper function for XP level calculation
export const calculateLevel = (xp) => {
  // Level 1: 0-100 XP
  // Level 2: 100-250 XP
  // Level 3: 250-500 XP
  // Level n: exponential growth
  return Math.floor(Math.sqrt(xp / 50)) + 1
}

export const getXPForNextLevel = (currentLevel) => {
  return Math.pow(currentLevel, 2) * 50
}

export const getXPProgress = (xp) => {
  const level = calculateLevel(xp)
  const currentLevelXP = getXPForNextLevel(level - 1)
  const nextLevelXP = getXPForNextLevel(level)
  const progress = ((xp - currentLevelXP) / (nextLevelXP - currentLevelXP)) * 100
  return { level, progress: Math.min(progress, 100), nextLevelXP, currentXP: xp }
}
