/**
 * Telemetry service for tracking performance metrics
 * This should be used instead of storing metrics in global state
 * Metrics are tracked but don't trigger UI re-renders
 */

interface PerformanceMetric {
  endpoint: string
  duration: number
  timestamp: number
  status: number
}

interface PageLoadMetric {
  page: string
  loadTime: number
  timestamp: number
}

class TelemetryService {
  private metrics: PerformanceMetric[] = []
  private pageLoads: PageLoadMetric[] = []
  private maxMetrics = 100 // Keep only last 100 metrics to avoid memory leaks

  recordApiResponseTime(endpoint: string, duration: number, status: number): void {
    const metric: PerformanceMetric = {
      endpoint,
      duration,
      timestamp: Date.now(),
      status,
    }

    this.metrics.push(metric)

    // Remove old metrics if exceeding limit
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics)
    }

    // Log slow requests for debugging
    if (duration > 5000) {
      console.warn(`[TELEMETRY] Slow API request: ${endpoint} took ${duration}ms`)
    }
  }

  recordPageLoadTime(page: string, loadTime: number): void {
    const metric: PageLoadMetric = {
      page,
      loadTime,
      timestamp: Date.now(),
    }

    this.pageLoads.push(metric)

    // Remove old metrics if exceeding limit
    if (this.pageLoads.length > this.maxMetrics) {
      this.pageLoads = this.pageLoads.slice(-this.maxMetrics)
    }

    // Log slow page loads for debugging
    if (loadTime > 3000) {
      console.warn(`[TELEMETRY] Slow page load: ${page} took ${loadTime}ms`)
    }
  }

  getAverageResponseTime(endpoint?: string): number {
    const filtered = endpoint
      ? this.metrics.filter(m => m.endpoint === endpoint)
      : this.metrics

    if (filtered.length === 0) return 0

    const total = filtered.reduce((sum, m) => sum + m.duration, 0)
    return Math.round(total / filtered.length)
  }

  getAveragePageLoadTime(page?: string): number {
    const filtered = page
      ? this.pageLoads.filter(p => p.page === page)
      : this.pageLoads

    if (filtered.length === 0) return 0

    const total = filtered.reduce((sum, p) => sum + p.loadTime, 0)
    return Math.round(total / filtered.length)
  }

  getMetrics() {
    return {
      apiMetrics: this.metrics,
      pageLoadMetrics: this.pageLoads,
    }
  }

  clear(): void {
    this.metrics = []
    this.pageLoads = []
  }
}

// Global telemetry service instance
export const telemetryService = new TelemetryService()
