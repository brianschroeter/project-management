import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { registerServiceWorker, setupInstallPrompt } from './utils/registerSW'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)

// Register service worker for PWA functionality
registerServiceWorker()

// Setup PWA install prompt
setupInstallPrompt()

// Log PWA status
if (import.meta.env.DEV) {
  console.log('🚀 Ultrathink running in development mode')
} else {
  console.log('🚀 Ultrathink PWA ready')
}
