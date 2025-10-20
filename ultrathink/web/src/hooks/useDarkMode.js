import { useState, useEffect } from 'react'

/**
 * Dark Mode Hook
 * Manages dark mode state and persists to localStorage
 */
export function useDarkMode() {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('ultrathink_dark_mode')
    return saved ? JSON.parse(saved) : false
  })

  useEffect(() => {
    localStorage.setItem('ultrathink_dark_mode', JSON.stringify(isDark))

    // Update document class for global dark mode styles
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDark])

  const toggle = () => setIsDark(prev => !prev)

  return [isDark, toggle]
}
