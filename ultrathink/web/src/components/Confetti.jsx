import ReactConfetti from 'react-confetti'
import { useEffect, useState } from 'react'

/**
 * Confetti Celebration Component
 * Shows confetti animation on task completion
 */
export function Confetti({ show, onComplete, duration = 3000 }) {
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  })

  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight
      })
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    if (show && onComplete) {
      const timer = setTimeout(() => {
        onComplete()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [show, onComplete, duration])

  if (!show) return null

  return (
    <ReactConfetti
      width={dimensions.width}
      height={dimensions.height}
      numberOfPieces={200}
      recycle={false}
      gravity={0.3}
      colors={['#4ade80', '#fbbf24', '#f43f5e', '#3b82f6', '#a855f7', '#ec4899']}
    />
  )
}
