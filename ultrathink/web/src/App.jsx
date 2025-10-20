import { useState, useEffect } from 'react'
import axios from 'axios'
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query'
import { Moon, Sun } from 'lucide-react'
import './App.css'
import './styles/animations.css'
import './styles/gamification.css'
import { TaskCard } from './components/TaskCard'
import { EnergySelector } from './components/EnergySelector'
import { GamificationStats, XPProgressBar, LevelUpModal } from './components/GamificationStats'
import { Confetti } from './components/Confetti'
import { useGamification } from './hooks/useGamification'
import { useDarkMode } from './hooks/useDarkMode'
import { theme } from './styles/theme'

const queryClient = new QueryClient()
const API_BASE = 'http://192.168.1.87:8001'

function Dashboard() {
  const [currentEnergy, setCurrentEnergy] = useState('medium')
  const [authStatus, setAuthStatus] = useState('checking')
  const [isDark, toggleDark] = useDarkMode()
  const gamification = useGamification()
  const [showConfetti, setShowConfetti] = useState(false)

  // Check auth status
  useEffect(() => {
    // Check for auth callback parameters in URL
    const urlParams = new URLSearchParams(window.location.search)
    const authParam = urlParams.get('auth')
    const messageParam = urlParams.get('message')

    if (authParam === 'success') {
      // Clear URL parameters
      window.history.replaceState({}, document.title, window.location.pathname)
      // Show success message briefly before checking status
      console.log('✅ Authentication successful!')
    } else if (authParam === 'error') {
      console.error('❌ Authentication failed:', messageParam)
      alert(`Authentication failed: ${messageParam || 'Unknown error'}`)
      window.history.replaceState({}, document.title, window.location.pathname)
    }

    // Check authentication status
    axios.get(`${API_BASE}/auth/status`)
      .then(res => {
        if (res.data.authenticated) {
          setAuthStatus('authenticated')
        } else {
          setAuthStatus('not_authenticated')
        }
      })
      .catch(() => setAuthStatus('not_authenticated'))
  }, [])

  // Fetch daily review
  const { data: dailyData, isLoading: dailyLoading } = useQuery({
    queryKey: ['daily'],
    queryFn: () => axios.get(`${API_BASE}/daily`).then(res => res.data),
    enabled: authStatus === 'authenticated',
  })

  // Fetch tasks
  const { data: tasks, isLoading: tasksLoading, refetch: refetchTasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: async () => {
      const res = await axios.get(`${API_BASE}/tasks`, {
        // Cache-busting: add timestamp and disable all caching
        params: { _t: Date.now() },
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      })
      // DEBUG: Log first task to diagnose projectId issue
      console.log('App.jsx - First task from API:', res.data[0])
      return res.data
    },
    enabled: authStatus === 'authenticated',
    staleTime: 0,  // Always fetch fresh data
    gcTime: 0,  // Don't cache responses (React Query v5 renamed cacheTime to gcTime)
  })

  // Energy suggestions
  const { data: suggestions } = useQuery({
    queryKey: ['suggestions', currentEnergy],
    queryFn: () => axios.get(`${API_BASE}/energy/suggest-tasks`, {
      params: { energy_level: currentEnergy, limit: 5 }
    }).then(res => res.data),
    enabled: authStatus === 'authenticated',
  })

  // Complete task mutation
  const completeMutation = useMutation({
    mutationFn: (taskId) => axios.post(`${API_BASE}/tasks/${taskId}/complete`),
    onSuccess: (_, taskId) => {
      // Find the completed task to get energy level
      const completedTask = tasks?.find(t => t.id === taskId)
      const energyLevel = completedTask?.ai_insights?.energy_level || 'medium'
      const estimatedMinutes = completedTask?.ai_insights?.estimated_minutes || 30

      // Award XP
      gamification.completeTask({
        energyLevel,
        estimatedMinutes
      })

      // Show celebration
      setShowConfetti(true)

      // Refetch data
      queryClient.invalidateQueries(['tasks'])
      queryClient.invalidateQueries(['daily'])
    },
  })

  if (authStatus === 'checking') {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Checking authentication...</p>
      </div>
    )
  }

  const handleLogin = async () => {
    try {
      const response = await axios.get(`${API_BASE}/auth/login`)
      // Redirect to TickTick OAuth page
      window.location.href = response.data.auth_url
    } catch (error) {
      console.error('Login error:', error)
      alert('Failed to initiate login. Please try again.')
    }
  }

  if (authStatus === 'not_authenticated') {
    return (
      <div className="auth-required">
        <h1>🧠 Ultrathink</h1>
        <p>ADHD-friendly task management for TickTick</p>
        <div className="auth-instructions">
          <p>Click the button below to connect your TickTick account:</p>
          <button
            onClick={handleLogin}
            className="login-button"
            style={{
              padding: '12px 24px',
              fontSize: '16px',
              fontWeight: 600,
              color: 'white',
              background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              marginTop: '16px',
              transition: 'transform 0.2s ease, box-shadow 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)'
              e.target.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.4)'
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)'
              e.target.style.boxShadow = 'none'
            }}
          >
            🔗 Login with TickTick
          </button>
          <p style={{ marginTop: '24px', fontSize: '14px', color: '#666' }}>
            You'll be redirected to TickTick to authorize this app
          </p>
        </div>
      </div>
    )
  }

  const handleComplete = (taskId) => {
    completeMutation.mutate(taskId)
  }

  const getEnergyEmoji = (level) => {
    return { low: '🟢', medium: '🟡', high: '🔴' }[level] || '⚪'
  }

  return (
    <div
      className="dashboard"
      style={{
        minHeight: '100vh',
        background: isDark ? theme.dark.bg.primary : theme.light.bg.primary,
        color: isDark ? theme.dark.text.primary : theme.light.text.primary,
        transition: 'all 0.3s ease'
      }}
    >
      {/* Confetti celebration */}
      <Confetti
        show={showConfetti}
        onComplete={() => setShowConfetti(false)}
      />

      {/* Level up modal */}
      {gamification.showLevelUp && (
        <LevelUpModal
          level={gamification.stats.level}
          onClose={() => gamification.setShowLevelUp(false)}
        />
      )}

      <header
        className="header"
        style={{
          padding: '2rem',
          background: isDark ? theme.dark.bg.secondary : 'white',
          boxShadow: isDark ? '0 2px 8px rgba(0,0,0,0.3)' : '0 2px 8px rgba(0,0,0,0.1)'
        }}
      >
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <h1 style={{ margin: 0, fontSize: '2rem' }}>🧠 Ultrathink Dashboard</h1>
          <button
            onClick={toggleDark}
            className="hover-scale smooth-transition"
            style={{
              padding: '0.75rem',
              background: isDark ? theme.dark.bg.tertiary : theme.light.bg.tertiary,
              color: isDark ? theme.dark.text.primary : theme.light.text.primary,
              border: 'none',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            {isDark ? <Sun size={20} /> : <Moon size={20} />}
            <span>{isDark ? 'Light' : 'Dark'} Mode</span>
          </button>
        </div>

        {/* Gamification Stats and XP Progress - Side by Side */}
        <div style={{
          maxWidth: '1400px',
          margin: '1.5rem auto 0',
          display: 'grid',
          gridTemplateColumns: '2fr 1fr',
          gap: '1.5rem',
          alignItems: 'start'
        }}>
          <div>
            <GamificationStats
              stats={gamification.stats}
              xpProgress={gamification.xpProgress}
            />
          </div>
          <div>
            <XPProgressBar xpProgress={gamification.xpProgress} />
          </div>
        </div>

        {/* Energy Selector */}
        <div style={{ maxWidth: '1400px', margin: '1.5rem auto 0' }}>
          <EnergySelector
            currentEnergy={currentEnergy}
            onChange={setCurrentEnergy}
            isDark={isDark}
          />
        </div>
      </header>

      <div className="main-content" style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '2rem'
      }}>
        {/* Daily Review */}
        {!dailyLoading && dailyData && (
          <section className="daily-review stagger-children" style={{
            marginBottom: '2rem'
          }}>
            <h2 style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: isDark ? theme.dark.text.primary : theme.light.text.primary
            }}>
              📅 Daily Review
            </h2>

            <div className="stats-row" style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem',
              marginBottom: '1.5rem'
            }}>
              <div className="stat-card hover-lift" style={{
                padding: '1rem',
                background: isDark ? theme.dark.bg.secondary : 'white',
                borderRadius: '0.75rem',
                boxShadow: isDark ? '0 2px 8px rgba(0,0,0,0.3)' : '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <span className="stat-label" style={{
                  fontSize: '0.875rem',
                  color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>Predicted Energy</span>
                <span className="stat-value" style={{
                  fontSize: '2rem',
                  fontWeight: 700,
                  color: isDark ? theme.dark.text.primary : theme.light.text.primary,
                  display: 'block',
                  marginTop: '0.25rem'
                }}>
                  {getEnergyEmoji(dailyData.recommended_energy)} {dailyData.recommended_energy}
                </span>
              </div>

              <div className="stat-card hover-lift" style={{
                padding: '1rem',
                background: isDark ? theme.dark.bg.secondary : 'white',
                borderRadius: '0.75rem',
                boxShadow: isDark ? '0 2px 8px rgba(0,0,0,0.3)' : '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <span className="stat-label" style={{
                  fontSize: '0.875rem',
                  color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>Due Today</span>
                <span className="stat-value" style={{
                  fontSize: '2rem',
                  fontWeight: 700,
                  color: isDark ? theme.dark.text.primary : theme.light.text.primary,
                  display: 'block',
                  marginTop: '0.25rem'
                }}>{dailyData.due_today?.length || 0}</span>
              </div>

              <div className="stat-card hover-lift" style={{
                padding: '1rem',
                background: isDark ? theme.dark.bg.secondary : 'white',
                borderRadius: '0.75rem',
                boxShadow: isDark ? '0 2px 8px rgba(0,0,0,0.3)' : '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <span className="stat-label" style={{
                  fontSize: '0.875rem',
                  color: isDark ? theme.dark.text.secondary : theme.light.text.secondary,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>Stale Tasks</span>
                <span className="stat-value warn" style={{
                  fontSize: '2rem',
                  fontWeight: 700,
                  color: '#f59e0b',
                  display: 'block',
                  marginTop: '0.25rem'
                }}>{dailyData.stale_tasks?.length || 0}</span>
              </div>
            </div>

            {dailyData.top_priorities && dailyData.top_priorities.length > 0 && (
              <div className="top-priorities">
                <h3 style={{
                  fontSize: '1.25rem',
                  fontWeight: 600,
                  marginBottom: '1rem',
                  color: isDark ? theme.dark.text.primary : theme.light.text.primary
                }}>🎯 Top 3 Priorities</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {dailyData.top_priorities.map((task, i) => (
                    <TaskCard
                      key={i}
                      task={{
                        ...task,
                        id: task.task_id || i,
                        projectId: task.projectId || task.project_id  // Normalize snake_case to camelCase
                      }}
                      onComplete={handleComplete}
                      isDark={isDark}
                    />
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        {/* Energy-Matched Tasks */}
        {suggestions && suggestions.length > 0 && (
          <section className="suggestions stagger-children" style={{ marginBottom: '2rem' }}>
            <h2 style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: isDark ? theme.dark.text.primary : theme.light.text.primary
            }}>
              {getEnergyEmoji(currentEnergy)} Tasks for Your {currentEnergy} Energy
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {suggestions.map((task) => (
                <TaskCard
                  key={task.task_id}
                  task={{
                    ...task,
                    id: task.task_id,
                    projectId: task.projectId || task.project_id  // Normalize snake_case to camelCase
                  }}
                  onComplete={handleComplete}
                  isDark={isDark}
                />
              ))}
            </div>
          </section>
        )}

        {/* All Tasks */}
        {!tasksLoading && tasks && (
          <section className="all-tasks stagger-children" style={{ marginBottom: '2rem' }}>
            <h2 style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: isDark ? theme.dark.text.primary : theme.light.text.primary
            }}>
              📋 All Tasks ({tasks.length})
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {tasks.slice(0, 10).map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onComplete={handleComplete}
                  isDark={isDark}
                />
              ))}
            </div>
            {tasks.length > 10 && (
              <div style={{
                textAlign: 'center',
                marginTop: '1rem',
                fontSize: '0.875rem',
                color: isDark ? theme.dark.text.secondary : theme.light.text.secondary
              }}>
                Showing 10 of {tasks.length} tasks
              </div>
            )}
          </section>
        )}

        {/* Stale Tasks Warning */}
        {dailyData?.stale_tasks && dailyData.stale_tasks.length > 0 && (
          <section className="stale-tasks stagger-children" style={{ marginBottom: '2rem' }}>
            <h2 style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: '#f59e0b'
            }}>
              ⚠️ Tasks Needing Attention
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {dailyData.stale_tasks.slice(0, 5).map((task, i) => (
                <TaskCard
                  key={i}
                  task={{
                    ...task,
                    id: task.id || task.ticktick_task_id || i,
                    projectId: task.projectId || task.project_id,  // Normalize snake_case to camelCase
                    title: task.title || task.task_title,
                    content: task.content,
                    first_step: task.unstuck_help?.tiny_first_step
                  }}
                  onComplete={handleComplete}
                  isDark={isDark}
                  showClarifyButton={true}
                />
              ))}
            </div>
          </section>
        )}
      </div>

      <footer className="footer">
        <p>Ultrathink • ADHD-friendly task management</p>
        <p>Use 'ultra' command in terminal for quick access</p>
      </footer>
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  )
}

export default App
