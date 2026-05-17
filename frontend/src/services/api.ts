const BASE = ''

export async function apiGet<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(endpoint, window.location.origin)
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  }
  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export async function apiPost<T>(endpoint: string, body: unknown): Promise<T> {
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export async function apiDelete<T>(endpoint: string, body: unknown): Promise<T> {
  const res = await fetch(endpoint, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export interface FilterConfig {
  filter_enabled: string
  min_playtime_hours: string
  whitelist: string
  blacklist: string
  max_legend_players: string
}

export async function getSettings(): Promise<FilterConfig> {
  return apiGet<FilterConfig>('/api/settings')
}

export async function updateSettings(settings: Partial<FilterConfig>): Promise<{ success: boolean; settings: FilterConfig }> {
  return apiPost<{ success: boolean; settings: FilterConfig }>('/api/settings', settings)
}