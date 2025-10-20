/**
 * Service Worker Registration
 * Enables PWA functionality with offline support
 */

/**
 * Register the service worker
 * @returns {Promise<ServiceWorkerRegistration | null>}
 */
export async function registerServiceWorker() {
  // Check if service workers are supported
  if (!('serviceWorker' in navigator)) {
    console.log('[PWA] Service Workers not supported in this browser');
    return null;
  }

  try {
    // Wait for page to load
    await new Promise((resolve) => {
      if (document.readyState === 'complete') {
        resolve();
      } else {
        window.addEventListener('load', resolve);
      }
    });

    console.log('[PWA] Registering Service Worker...');

    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/'
    });

    console.log('[PWA] Service Worker registered successfully:', registration.scope);

    // Check for updates periodically
    setInterval(() => {
      registration.update();
    }, 60000); // Check every minute

    // Handle updates
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing;

      if (newWorker) {
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            console.log('[PWA] New content available, please refresh');

            // Optionally show update notification to user
            showUpdateNotification();
          }
        });
      }
    });

    return registration;
  } catch (error) {
    console.error('[PWA] Service Worker registration failed:', error);
    return null;
  }
}

/**
 * Unregister the service worker
 * @returns {Promise<boolean>}
 */
export async function unregisterServiceWorker() {
  if (!('serviceWorker' in navigator)) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const unregistered = await registration.unregister();

    if (unregistered) {
      console.log('[PWA] Service Worker unregistered successfully');
    }

    return unregistered;
  } catch (error) {
    console.error('[PWA] Service Worker unregistration failed:', error);
    return false;
  }
}

/**
 * Show update notification to user
 */
function showUpdateNotification() {
  // Create a simple toast notification
  const toast = document.createElement('div');
  toast.className = 'pwa-update-toast';
  toast.innerHTML = `
    <div style="
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 1rem 1.5rem;
      border-radius: 0.75rem;
      box-shadow: 0 10px 40px rgba(0,0,0,0.3);
      z-index: 10000;
      font-family: system-ui, sans-serif;
      max-width: 320px;
      animation: slideUp 0.3s ease-out;
    ">
      <div style="font-weight: 600; margin-bottom: 0.5rem;">
        🎉 New version available!
      </div>
      <div style="font-size: 0.875rem; margin-bottom: 1rem; opacity: 0.9;">
        A new version of Ultrathink is ready. Refresh to update.
      </div>
      <button
        onclick="window.location.reload()"
        style="
          width: 100%;
          padding: 0.5rem;
          background: white;
          color: #667eea;
          border: none;
          border-radius: 0.5rem;
          font-weight: 600;
          cursor: pointer;
        "
      >
        Refresh Now
      </button>
    </div>
  `;

  document.body.appendChild(toast);

  // Auto-remove after 30 seconds
  setTimeout(() => {
    toast.remove();
  }, 30000);
}

/**
 * Check if app is installed as PWA
 * @returns {boolean}
 */
export function isPWA() {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true
  );
}

/**
 * Request notification permissions
 * @returns {Promise<NotificationPermission>}
 */
export async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    console.log('[PWA] Notifications not supported');
    return 'denied';
  }

  if (Notification.permission === 'granted') {
    return 'granted';
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    return permission;
  }

  return Notification.permission;
}

/**
 * Show a notification
 * @param {string} title - Notification title
 * @param {object} options - Notification options
 */
export async function showNotification(title, options = {}) {
  const permission = await requestNotificationPermission();

  if (permission === 'granted') {
    const registration = await navigator.serviceWorker.ready;

    await registration.showNotification(title, {
      icon: '/vite.svg',
      badge: '/vite.svg',
      ...options
    });
  }
}

/**
 * Install prompt for PWA
 */
let deferredPrompt = null;

export function setupInstallPrompt() {
  window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent the default install prompt
    e.preventDefault();

    // Store the event for later use
    deferredPrompt = e;

    console.log('[PWA] Install prompt available');

    // Optionally show custom install button
    showInstallButton();
  });

  // Track if app was installed
  window.addEventListener('appinstalled', () => {
    console.log('[PWA] App installed successfully');
    deferredPrompt = null;

    // Hide install button if shown
    hideInstallButton();
  });
}

/**
 * Show install button
 */
function showInstallButton() {
  // Only show if not already installed
  if (isPWA()) {
    return;
  }

  const button = document.createElement('button');
  button.id = 'pwa-install-button';
  button.className = 'pwa-install-btn';
  button.innerHTML = `
    <div style="
      position: fixed;
      bottom: 80px;
      right: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 0.75rem 1.5rem;
      border-radius: 9999px;
      box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
      cursor: pointer;
      font-weight: 600;
      font-size: 0.875rem;
      z-index: 9999;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      border: none;
      font-family: system-ui, sans-serif;
    ">
      📱 Install App
    </div>
  `;

  button.addEventListener('click', installPWA);

  document.body.appendChild(button);
}

/**
 * Hide install button
 */
function hideInstallButton() {
  const button = document.getElementById('pwa-install-button');
  if (button) {
    button.remove();
  }
}

/**
 * Trigger PWA install prompt
 */
export async function installPWA() {
  if (!deferredPrompt) {
    console.log('[PWA] Install prompt not available');
    return;
  }

  // Show the install prompt
  deferredPrompt.prompt();

  // Wait for user response
  const { outcome } = await deferredPrompt.userChoice;

  console.log(`[PWA] User ${outcome === 'accepted' ? 'accepted' : 'dismissed'} the install prompt`);

  // Clear the deferred prompt
  deferredPrompt = null;

  // Hide install button
  hideInstallButton();
}
