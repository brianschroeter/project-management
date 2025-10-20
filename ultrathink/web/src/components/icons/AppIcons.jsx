/**
 * Centralized Icon System
 * Using lucide-react for consistent, accessible icons
 * Replaces emoji usage throughout the app
 */

import {
  Brain,
  Calendar,
  Target,
  ClipboardList,
  AlertTriangle,
  Clock,
  BarChart3,
  Mail,
  Lightbulb,
  Circle,
  Zap,
  Flame,
  Sparkles,
  Inbox,
  CheckCircle2,
  TrendingUp,
  Award,
  Star,
  Trophy,
  Rocket,
  Coffee,
  Battery,
  BatteryMedium,
  BatteryLow
} from 'lucide-react'

/**
 * App Logo / Brain Icon
 */
export const BrainIcon = ({ size = 24, className = '' }) => (
  <Brain size={size} className={className} aria-hidden="true" />
)

/**
 * Calendar / Daily Review Icon
 */
export const CalendarIcon = ({ size = 24, className = '' }) => (
  <Calendar size={size} className={className} aria-hidden="true" />
)

/**
 * Target / Priority Icon
 */
export const TargetIcon = ({ size = 24, className = '' }) => (
  <Target size={size} className={className} aria-hidden="true" />
)

/**
 * Clipboard / All Tasks Icon
 */
export const TasksIcon = ({ size = 24, className = '' }) => (
  <ClipboardList size={size} className={className} aria-hidden="true" />
)

/**
 * Warning / Stale Tasks Icon
 */
export const WarningIcon = ({ size = 24, className = '' }) => (
  <AlertTriangle size={size} className={className} aria-hidden="true" />
)

/**
 * Clock / Time Estimate Icon
 */
export const ClockIcon = ({ size = 24, className = '' }) => (
  <Clock size={size} className={className} aria-hidden="true" />
)

/**
 * Chart / Priority Score Icon
 */
export const ChartIcon = ({ size = 24, className = '' }) => (
  <BarChart3 size={size} className={className} aria-hidden="true" />
)

/**
 * Mail / Email Icon
 */
export const MailIcon = ({ size = 24, className = '' }) => (
  <Mail size={size} className={className} aria-hidden="true" />
)

/**
 * Lightbulb / Ideas / First Step Icon
 */
export const IdeaIcon = ({ size = 24, className = '' }) => (
  <Lightbulb size={size} className={className} aria-hidden="true" />
)

/**
 * Energy Level Icons with Colors
 */
export const EnergyIcon = ({ level = 'medium', size = 20, className = '' }) => {
  const icons = {
    low: <BatteryLow size={size} className={className} style={{ color: '#4ade80' }} aria-hidden="true" />,
    medium: <BatteryMedium size={size} className={className} style={{ color: '#fbbf24' }} aria-hidden="true" />,
    high: <Battery size={size} className={className} style={{ color: '#f43f5e' }} aria-hidden="true" />
  }

  return icons[level] || icons.medium
}

/**
 * Energy Circle Icons (for badges)
 */
export const EnergyCircle = ({ level = 'medium', size = 16 }) => {
  const colors = {
    low: '#4ade80',
    medium: '#fbbf24',
    high: '#f43f5e'
  }

  return (
    <Circle
      size={size}
      fill={colors[level]}
      color={colors[level]}
      aria-hidden="true"
    />
  )
}

/**
 * XP / Lightning Icon
 */
export const XPIcon = ({ size = 24, className = '' }) => (
  <Zap size={size} className={className} aria-hidden="true" />
)

/**
 * Streak / Flame Icon
 */
export const StreakIcon = ({ size = 24, className = '' }) => (
  <Flame size={size} className={className} aria-hidden="true" />
)

/**
 * Celebration / Sparkles Icon
 */
export const CelebrationIcon = ({ size = 24, className = '' }) => (
  <Sparkles size={size} className={className} aria-hidden="true" />
)

/**
 * Empty State / Inbox Icon
 */
export const EmptyIcon = ({ size = 24, className = '' }) => (
  <Inbox size={size} className={className} aria-hidden="true" />
)

/**
 * Success / Check Circle Icon
 */
export const SuccessIcon = ({ size = 24, className = '' }) => (
  <CheckCircle2 size={size} className={className} aria-hidden="true" />
)

/**
 * Level / Trophy Icon
 */
export const LevelIcon = ({ size = 24, className = '' }) => (
  <Trophy size={size} className={className} aria-hidden="true" />
)

/**
 * Achievement / Award Icon
 */
export const AchievementIcon = ({ size = 24, className = '' }) => (
  <Award size={size} className={className} aria-hidden="true" />
)

/**
 * Rocket / Launch Icon
 */
export const RocketIcon = ({ size = 24, className = '' }) => (
  <Rocket size={size} className={className} aria-hidden="true" />
)

/**
 * Trending / Progress Icon
 */
export const TrendingIcon = ({ size = 24, className = '' }) => (
  <TrendingUp size={size} className={className} aria-hidden="true" />
)

/**
 * Star / Favorite Icon
 */
export const StarIcon = ({ size = 24, className = '', filled = false }) => (
  <Star
    size={size}
    className={className}
    fill={filled ? 'currentColor' : 'none'}
    aria-hidden="true"
  />
)

/**
 * Coffee Break Icon
 */
export const BreakIcon = ({ size = 24, className = '' }) => (
  <Coffee size={size} className={className} aria-hidden="true" />
)

/**
 * Icon wrapper with consistent sizing and accessibility
 */
export const Icon = ({ children, label, size = 24, className = '' }) => (
  <span
    className={`inline-flex items-center justify-center ${className}`}
    aria-label={label}
    role={label ? 'img' : 'presentation'}
    style={{
      width: size,
      height: size
    }}
  >
    {children}
  </span>
)

/**
 * Icon utilities
 */
export const iconSizes = {
  xs: 12,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
  '2xl': 48
}

/**
 * Get icon size from size prop
 */
export const getIconSize = (size) => {
  if (typeof size === 'number') return size
  return iconSizes[size] || iconSizes.md
}
