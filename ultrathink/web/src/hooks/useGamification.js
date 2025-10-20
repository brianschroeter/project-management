import { useState, useEffect, useCallback } from 'react'
import { calculateLevel, getXPProgress } from '../styles/theme'

/**
 * Gamification Hook
 * Manages XP, levels, achievements, and streaks
 */

// Achievement definitions
const ACHIEVEMENTS = [
  {
    id: 'first_task',
    name: 'First Steps',
    description: 'Complete your first task',
    icon: '🎯',
    tier: 'bronze',
    condition: (stats) => stats.tasksCompleted >= 1
  },
  {
    id: 'task_master_5',
    name: 'Task Master',
    description: 'Complete 5 tasks',
    icon: '⭐',
    tier: 'bronze',
    condition: (stats) => stats.tasksCompleted >= 5
  },
  {
    id: 'task_master_25',
    name: 'Super Achiever',
    description: 'Complete 25 tasks',
    icon: '🌟',
    tier: 'silver',
    condition: (stats) => stats.tasksCompleted >= 25
  },
  {
    id: 'task_master_100',
    name: 'Century',
    description: 'Complete 100 tasks',
    icon: '💯',
    tier: 'gold',
    condition: (stats) => stats.tasksCompleted >= 100
  },
  {
    id: 'streak_3',
    name: 'On Fire',
    description: '3 day streak',
    icon: '🔥',
    tier: 'bronze',
    condition: (stats) => stats.currentStreak >= 3
  },
  {
    id: 'streak_7',
    name: 'Week Warrior',
    description: '7 day streak',
    icon: '🔥🔥',
    tier: 'silver',
    condition: (stats) => stats.currentStreak >= 7
  },
  {
    id: 'streak_30',
    name: 'Monthly Master',
    description: '30 day streak',
    icon: '🔥🔥🔥',
    tier: 'gold',
    condition: (stats) => stats.currentStreak >= 30
  },
  {
    id: 'energy_master',
    name: 'Energy Master',
    description: 'Complete tasks at all energy levels',
    icon: '⚡',
    tier: 'silver',
    condition: (stats) => {
      return stats.completedByEnergy?.low > 0 &&
             stats.completedByEnergy?.medium > 0 &&
             stats.completedByEnergy?.high > 0
    }
  },
  {
    id: 'morning_person',
    name: 'Morning Person',
    description: 'Complete 10 tasks before noon',
    icon: '🌅',
    tier: 'bronze',
    condition: (stats) => stats.morningTasks >= 10
  },
  {
    id: 'night_owl',
    name: 'Night Owl',
    description: 'Complete 10 tasks after 8 PM',
    icon: '🦉',
    tier: 'bronze',
    condition: (stats) => stats.nightTasks >= 10
  },
  {
    id: 'level_5',
    name: 'Level 5 Unlocked',
    description: 'Reach level 5',
    icon: '🏆',
    tier: 'silver',
    condition: (stats) => stats.level >= 5
  },
  {
    id: 'level_10',
    name: 'Legend',
    description: 'Reach level 10',
    icon: '👑',
    tier: 'gold',
    condition: (stats) => stats.level >= 10
  },
  {
    id: 'quick_win',
    name: 'Quick Winner',
    description: 'Complete a task in under 5 minutes',
    icon: '⚡',
    tier: 'bronze',
    condition: (stats) => stats.quickWins >= 1
  },
  {
    id: 'focus_master',
    name: 'Focus Master',
    description: 'Complete 5 high-energy tasks',
    icon: '🎯',
    tier: 'silver',
    condition: (stats) => stats.completedByEnergy?.high >= 5
  }
]

// XP rewards
const XP_REWARDS = {
  low: 10,      // Low energy task
  medium: 20,   // Medium energy task
  high: 40,     // High energy task
  quick_win: 5, // Bonus for tasks under 5 min
  streak_bonus: 10 // Daily streak bonus
}

const STORAGE_KEY = 'ultrathink_gamification'

export function useGamification() {
  const [stats, setStats] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      return JSON.parse(saved)
    }
    return {
      xp: 0,
      level: 1,
      tasksCompleted: 0,
      currentStreak: 0,
      longestStreak: 0,
      lastCompletionDate: null,
      achievements: [],
      completedByEnergy: { low: 0, medium: 0, high: 0 },
      morningTasks: 0,
      nightTasks: 0,
      quickWins: 0
    }
  })

  const [showLevelUp, setShowLevelUp] = useState(false)
  const [newAchievements, setNewAchievements] = useState([])

  // Save to localStorage whenever stats change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stats))
  }, [stats])

  // Check for new achievements
  const checkAchievements = useCallback((newStats) => {
    const unlocked = []
    ACHIEVEMENTS.forEach(achievement => {
      if (!newStats.achievements.includes(achievement.id) &&
          achievement.condition(newStats)) {
        unlocked.push(achievement)
      }
    })
    return unlocked
  }, [])

  // Add XP
  const addXP = useCallback((amount, reason = 'Task completed') => {
    setStats(prevStats => {
      const oldLevel = prevStats.level
      const newXP = prevStats.xp + amount
      const newLevel = calculateLevel(newXP)

      // Level up!
      if (newLevel > oldLevel) {
        setTimeout(() => setShowLevelUp(true), 500)
      }

      const newStats = {
        ...prevStats,
        xp: newXP,
        level: newLevel
      }

      // Check for new achievements
      const unlocked = checkAchievements(newStats)
      if (unlocked.length > 0) {
        setNewAchievements(unlocked)
        newStats.achievements = [...prevStats.achievements, ...unlocked.map(a => a.id)]
      }

      return newStats
    })
  }, [checkAchievements])

  // Complete a task
  const completeTask = useCallback((taskData) => {
    const {
      energyLevel = 'medium',
      estimatedMinutes = 30,
      actualMinutes
    } = taskData

    setStats(prevStats => {
      const now = new Date()
      const today = now.toISOString().split('T')[0]
      const hour = now.getHours()

      // Calculate streak
      let newStreak = prevStats.currentStreak
      let newLongestStreak = prevStats.longestStreak

      if (prevStats.lastCompletionDate) {
        const lastDate = new Date(prevStats.lastCompletionDate)
        const yesterday = new Date(now)
        yesterday.setDate(yesterday.getDate() - 1)
        const yesterdayStr = yesterday.toISOString().split('T')[0]

        if (prevStats.lastCompletionDate === today) {
          // Same day, keep streak
        } else if (prevStats.lastCompletionDate === yesterdayStr) {
          // Consecutive day
          newStreak += 1
          newLongestStreak = Math.max(newStreak, prevStats.longestStreak)
        } else {
          // Streak broken
          newStreak = 1
        }
      } else {
        newStreak = 1
      }

      // Calculate XP
      let xpGained = XP_REWARDS[energyLevel] || XP_REWARDS.medium

      // Quick win bonus (under 5 min or under half estimated time)
      const isQuickWin = actualMinutes && (actualMinutes < 5 || actualMinutes < estimatedMinutes / 2)
      if (isQuickWin) {
        xpGained += XP_REWARDS.quick_win
      }

      // Streak bonus (after 3+ days)
      if (newStreak >= 3) {
        xpGained += XP_REWARDS.streak_bonus
      }

      // Update stats
      const newStats = {
        ...prevStats,
        tasksCompleted: prevStats.tasksCompleted + 1,
        currentStreak: newStreak,
        longestStreak: newLongestStreak,
        lastCompletionDate: today,
        completedByEnergy: {
          ...prevStats.completedByEnergy,
          [energyLevel]: (prevStats.completedByEnergy[energyLevel] || 0) + 1
        },
        morningTasks: hour < 12 ? prevStats.morningTasks + 1 : prevStats.morningTasks,
        nightTasks: hour >= 20 ? prevStats.nightTasks + 1 : prevStats.nightTasks,
        quickWins: isQuickWin ? prevStats.quickWins + 1 : prevStats.quickWins
      }

      // Add XP
      const oldLevel = newStats.level
      const newXP = newStats.xp + xpGained
      const newLevel = calculateLevel(newXP)

      newStats.xp = newXP
      newStats.level = newLevel

      // Level up!
      if (newLevel > oldLevel) {
        setTimeout(() => setShowLevelUp(true), 500)
      }

      // Check for new achievements
      const unlocked = checkAchievements(newStats)
      if (unlocked.length > 0) {
        setNewAchievements(unlocked)
        newStats.achievements = [...prevStats.achievements, ...unlocked.map(a => a.id)]
      }

      return newStats
    })

    return {
      xpGained: XP_REWARDS[energyLevel] || XP_REWARDS.medium,
      leveledUp: false // Will be set by state update
    }
  }, [checkAchievements])

  // Reset stats (for testing)
  const resetStats = useCallback(() => {
    if (confirm('Are you sure you want to reset all gamification data?')) {
      setStats({
        xp: 0,
        level: 1,
        tasksCompleted: 0,
        currentStreak: 0,
        longestStreak: 0,
        lastCompletionDate: null,
        achievements: [],
        completedByEnergy: { low: 0, medium: 0, high: 0 },
        morningTasks: 0,
        nightTasks: 0,
        quickWins: 0
      })
    }
  }, [])

  // Get achievement list with unlock status
  const getAchievements = useCallback(() => {
    return ACHIEVEMENTS.map(achievement => ({
      ...achievement,
      unlocked: stats.achievements.includes(achievement.id)
    }))
  }, [stats.achievements])

  // Get XP progress
  const xpProgress = getXPProgress(stats.xp)

  return {
    stats,
    xpProgress,
    addXP,
    completeTask,
    resetStats,
    getAchievements,
    showLevelUp,
    setShowLevelUp,
    newAchievements,
    setNewAchievements
  }
}
