export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

interface ValidationIssue {
  msg: string
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const body: { detail?: string | ValidationIssue[] } = await response.json()
    if (typeof body.detail === 'string') return body.detail
    // FastAPI validation errors: a list of issues, the first one is enough for the UI.
    if (Array.isArray(body.detail) && body.detail.length > 0) return body.detail[0].msg
  } catch {
    // Not a JSON body (e.g. proxy error page).
  }
  return response.statusText || `request failed (${response.status})`
}

/**
 * Call the Votely API. Paths are relative to /api/v1 on the current origin, so the session
 * cookie is sent automatically and no CORS configuration is needed.
 */
export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const url = new URL(`/api/v1${path}`, window.location.origin)
  const response = await fetch(url, {
    ...init,
    credentials: 'same-origin',
    headers: { 'content-type': 'application/json', ...init.headers },
  })

  if (!response.ok) {
    throw new ApiError(response.status, await errorMessage(response))
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}
