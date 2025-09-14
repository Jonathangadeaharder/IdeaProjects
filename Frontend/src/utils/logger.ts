/**
 * Frontend file logging utility
 */

interface LogEntry {
  timestamp: string
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'
  component: string
  message: string
  data?: any
}

class FileLogger {
  private logs: LogEntry[] = []
  private maxLogs = 2000 // Increased for more debugging
  private flushInterval = 10000 // 10 seconds
  private logFile = `langplug-frontend-${new Date().toISOString().split('T')[0]}.log`
  private pendingLogs: LogEntry[] = [] // Buffer for unsent logs
  private isSending = false

  constructor() {
    // Add startup log
    this.addLog('INFO', 'Logger', '🚀 Frontend logger initialized')
    
    // Send logs to backend periodically
    setInterval(() => {
      this.sendLogsToBackend()
    }, this.flushInterval)

    // Send logs on page unload
    window.addEventListener('beforeunload', () => {
      this.sendLogsToBackend(true) // Force synchronous send
    })
    
    // Log page navigation
    this.addLog('INFO', 'Navigation', `Page loaded: ${window.location.pathname}`)
  }

  private addLog(level: LogEntry['level'], component: string, message: string, data?: any) {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      component,
      message,
      data: data ? JSON.stringify(data) : undefined
    }

    this.logs.push(logEntry)
    this.pendingLogs.push(logEntry) // Add to pending queue for backend

    // Also log to console for development with better formatting
    const consoleMessage = `[${level}] ${component}: ${message}`
    const consoleData = data ? (typeof data === 'object' ? data : `${data}`) : undefined
    
    switch (level) {
      case 'DEBUG':
        console.debug(`🐛 ${consoleMessage}`, consoleData || '')
        break
      case 'INFO':
        console.info(`ℹ️  ${consoleMessage}`, consoleData || '')
        break
      case 'WARN':
        console.warn(`⚠️  ${consoleMessage}`, consoleData || '')
        break
      case 'ERROR':
        console.error(`❌ ${consoleMessage}`, consoleData || '')
        break
    }

    // Keep only recent logs in memory
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs)
    }
  }

  private async sendLogsToBackend(synchronous = false) {
    if (this.pendingLogs.length === 0 || this.isSending) {
      return
    }

    this.isSending = true
    const logsToSend = [...this.pendingLogs]
    this.pendingLogs = [] // Clear pending logs

    try {
      const payload = {
        entries: logsToSend,
        client_id: 'frontend'
      }

      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const url = `${apiBase}/logs/frontend`
      
      if (synchronous) {
        // Use sendBeacon for synchronous sending on page unload
        navigator.sendBeacon(url, JSON.stringify(payload))
      } else {
        // Use fetch for regular async sending
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': localStorage.getItem('authToken') ? 
              `Bearer ${localStorage.getItem('authToken')}` : ''
          },
          body: JSON.stringify(payload)
        })

        if (!response.ok) {
          console.warn('Failed to send logs to backend:', response.statusText)
          // Put logs back in pending queue if failed
          this.pendingLogs.unshift(...logsToSend)
        }
      }
    } catch (error) {
      console.warn('Error sending logs to backend:', error)
      // Put logs back in pending queue if failed
      this.pendingLogs.unshift(...logsToSend)
    } finally {
      this.isSending = false
    }

    // Keep only recent logs in memory
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs)
    }
  }

  debug(component: string, message: string, data?: any) {
    this.addLog('DEBUG', component, message, data)
  }

  info(component: string, message: string, data?: any) {
    this.addLog('INFO', component, message, data)
  }

  warn(component: string, message: string, data?: any) {
    this.addLog('WARN', component, message, data)
  }

  error(component: string, message: string, data?: any) {
    this.addLog('ERROR', component, message, data)
  }

  // Method to manually download logs
  downloadLogs() {
    if (this.logs.length === 0) {
      console.warn('No logs to download')
      return
    }

    const logContent = '=== LangPlug Frontend Logs ===\n' +
      `Downloaded at: ${new Date().toISOString()}\n` +
      `Total entries: ${this.logs.length}\n` +
      '================================\n\n' +
      this.logs
        .map(log => {
          const parts = [log.timestamp, `[${log.level}]`, `${log.component}:`, log.message]
          if (log.data) parts.push(`| ${log.data}`)
          return parts.join(' ')
        })
        .join('\n')

    const blob = new Blob([logContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = this.logFile
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    
    URL.revokeObjectURL(url)
    console.info('✅ Logs downloaded:', this.logFile)
  }

  // Get current logs as string for display
  getCurrentLogs(): string {
    return this.logs
      .map(log => {
        const parts = [log.timestamp, `[${log.level}]`, `${log.component}:`, log.message]
        if (log.data) parts.push(`| ${log.data}`)
        return parts.join(' ')
      })
      .join('\n')
  }
  
  // Get recent logs (last N entries)
  getRecentLogs(count: number = 50): LogEntry[] {
    return this.logs.slice(-count)
  }
  
  // Add convenience methods for common workflow logging
  apiRequest(method: string, url: string, data?: any) {
    this.info('API', `→ ${method} ${url}`, data)
  }
  
  apiResponse(method: string, url: string, status: number, data?: any, duration?: number) {
    const durationStr = duration ? ` (${duration}ms)` : ''
    this.info('API', `← ${method} ${url} ${status}${durationStr}`, data)
  }
  
  userAction(action: string, details?: any) {
    this.info('User', `🖱️ ${action}`, details)
  }
  
  chunkProcessing(message: string, data?: any) {
    this.info('ChunkProcessing', `⚙️ ${message}`, data)
  }
  
  // Method to force send logs immediately
  async flushToBackend() {
    await this.sendLogsToBackend()
  }
}

// Global logger instance
export const logger = new FileLogger()

// Add helper methods to window for easy console access
declare global {
  interface Window {
    langplugLogger: FileLogger
    downloadLogs: () => void
    flushLogs: () => Promise<void>
    showLogs: (count?: number) => void
  }
}

window.langplugLogger = logger
window.downloadLogs = () => logger.downloadLogs()
window.flushLogs = () => logger.flushToBackend()
window.showLogs = (count = 20) => {
  console.group('🔍 Recent Frontend Logs')
  logger.getRecentLogs(count).forEach(log => {
    const style = {
      'ERROR': 'color: red; font-weight: bold',
      'WARN': 'color: orange; font-weight: bold', 
      'INFO': 'color: blue',
      'DEBUG': 'color: gray'
    }[log.level] || ''
    console.log(`%c[${log.level}] ${log.component}: ${log.message}`, style, log.data || '')
  })
  console.groupEnd()
  console.info('💡 Logs auto-save to Backend/logs/langplug-frontend-{date}.log')
  console.info('💡 Use flushLogs() to send logs immediately')
  console.info('💡 Use downloadLogs() to download browser logs')
}
