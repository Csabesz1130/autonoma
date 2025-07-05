export interface DebugEntry {
  timestamp: string
  level: 'info' | 'warn' | 'error' | 'success'
  component: string
  message: string
  data?: any
  stack?: string
}

class DebugService {
  private entries: DebugEntry[] = []
  private maxEntries = 100
  private isEnabled = typeof window !== 'undefined' && window.location.hostname === 'localhost'

  log(level: DebugEntry['level'], component: string, message: string, data?: any) {
    const entry: DebugEntry = {
      timestamp: new Date().toISOString(),
      level,
      component,
      message,
      data,
      stack: level === 'error' ? new Error().stack : undefined
    }

    this.entries.push(entry)
    
    // Keep only the last maxEntries
    if (this.entries.length > this.maxEntries) {
      this.entries = this.entries.slice(-this.maxEntries)
    }

    // Always log to console
    const logMessage = `[${entry.timestamp}] ${level.toUpperCase()} ${component}: ${message}`
    
    switch (level) {
      case 'error':
        console.error(logMessage, data)
        break
      case 'warn':
        console.warn(logMessage, data)
        break
      case 'success':
        console.log(`✅ ${logMessage}`, data)
        break
      default:
        console.log(logMessage, data)
    }
  }

  info(component: string, message: string, data?: any) {
    this.log('info', component, message, data)
  }

  warn(component: string, message: string, data?: any) {
    this.log('warn', component, message, data)
  }

  error(component: string, message: string, data?: any) {
    this.log('error', component, message, data)
  }

  success(component: string, message: string, data?: any) {
    this.log('success', component, message, data)
  }

  getEntries(filterLevel?: DebugEntry['level']): DebugEntry[] {
    return filterLevel 
      ? this.entries.filter(entry => entry.level === filterLevel)
      : this.entries
  }

  clear() {
    this.entries = []
  }

  exportLogs(): string {
    return JSON.stringify(this.entries, null, 2)
  }

  // API debugging helpers
  async logAPICall(endpoint: string, method: string, requestData?: any, response?: Response) {
    const component = 'API'
    
    this.info(component, `${method} ${endpoint}`, {
      requestData,
      status: response?.status,
      statusText: response?.statusText
    })

    if (response && !response.ok) {
      let errorData
      try {
        errorData = await response.clone().text()
      } catch (e) {
        errorData = 'Could not read response body'
      }
      
      this.error(component, `API Error: ${response.status} ${response.statusText}`, {
        endpoint,
        method,
        requestData,
        errorData
      })
    }

    return response
  }

  // Extension generation debugging
  logExtensionStep(step: string, data?: any) {
    this.info('ExtensionGenerator', `Step: ${step}`, data)
  }

  logExtensionError(step: string, error: Error | string, data?: any) {
    this.error('ExtensionGenerator', `Error in ${step}: ${error}`, data)
  }

  logExtensionSuccess(step: string, data?: any) {
    this.success('ExtensionGenerator', `Completed: ${step}`, data)
  }

  // Performance monitoring
  startTimer(label: string): () => void {
    const start = performance.now()
    this.info('Performance', `Timer started: ${label}`)
    
    return () => {
      const duration = performance.now() - start
      this.info('Performance', `Timer ended: ${label} (${duration.toFixed(2)}ms)`)
    }
  }

  // Health check helpers
  async checkBackendHealth(): Promise<boolean> {
    try {
      const response = await fetch('/api/health', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        this.success('HealthCheck', 'Backend is healthy')
        return true
      } else {
        this.error('HealthCheck', 'Backend health check failed', { status: response.status })
        return false
      }
    } catch (error) {
      this.error('HealthCheck', 'Backend health check failed', error)
      return false
    }
  }

  async checkChromeExtensionAPI(): Promise<boolean> {
    try {
      const response = await fetch('/api/chrome-extension/health', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        this.success('HealthCheck', 'Chrome Extension API is healthy')
        return true
      } else {
        this.error('HealthCheck', 'Chrome Extension API health check failed', { status: response.status })
        return false
      }
    } catch (error) {
      this.error('HealthCheck', 'Chrome Extension API health check failed', error)
      return false
    }
  }
}

export const debugService = new DebugService()

// Export individual functions for convenience
export const debug = {
  info: debugService.info.bind(debugService),
  warn: debugService.warn.bind(debugService),
  error: debugService.error.bind(debugService),
  success: debugService.success.bind(debugService),
  clear: debugService.clear.bind(debugService),
  getEntries: debugService.getEntries.bind(debugService),
  exportLogs: debugService.exportLogs.bind(debugService),
  logAPICall: debugService.logAPICall.bind(debugService),
  logExtensionStep: debugService.logExtensionStep.bind(debugService),
  logExtensionError: debugService.logExtensionError.bind(debugService),
  logExtensionSuccess: debugService.logExtensionSuccess.bind(debugService),
  startTimer: debugService.startTimer.bind(debugService),
  checkBackendHealth: debugService.checkBackendHealth.bind(debugService),
  checkChromeExtensionAPI: debugService.checkChromeExtensionAPI.bind(debugService)
}

// Auto-run health checks on load
if (typeof window !== 'undefined') {
  setTimeout(() => {
    debugService.checkBackendHealth()
    debugService.checkChromeExtensionAPI()
  }, 1000)
}