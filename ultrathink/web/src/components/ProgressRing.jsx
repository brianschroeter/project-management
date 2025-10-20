import { useEffect, useState } from 'react'

/**
 * Circular Progress Ring Component
 * Shows progress as a colorful ring with percentage
 */
export function ProgressRing({
  progress = 0, // 0-100
  size = 120,
  strokeWidth = 8,
  color = '#3b82f6',
  label = 'Progress',
  showPercentage = true,
  animated = true
}) {
  const [animatedProgress, setAnimatedProgress] = useState(0)

  useEffect(() => {
    if (animated) {
      // Animate progress on mount
      const timer = setTimeout(() => {
        setAnimatedProgress(progress)
      }, 100)
      return () => clearTimeout(timer)
    } else {
      setAnimatedProgress(progress)
    }
  }, [progress, animated])

  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (animatedProgress / 100) * circumference

  return (
    <div className="progress-ring-container" style={{ width: size, height: size }}>
      <svg className="progress-ring-svg" width={size} height={size}>
        {/* Background circle */}
        <circle
          className="progress-ring-bg"
          cx={size / 2}
          cy={size / 2}
          r={radius}
        />
        {/* Progress circle */}
        <circle
          className="progress-ring-fill"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={offset}
          style={{
            transition: animated ? 'stroke-dashoffset 0.5s ease' : 'none'
          }}
        />
      </svg>
      <div className="progress-ring-text">
        {showPercentage && (
          <span className="progress-ring-percentage">
            {Math.round(animatedProgress)}%
          </span>
        )}
        {label && (
          <span className="progress-ring-label">
            {label}
          </span>
        )}
      </div>
    </div>
  )
}
