import { ApiError, request } from './client'
import type { User } from './types'

export interface Credentials {
  email: string
  password: string
}

/** The logged-in user, or null for anonymous visitors. */
export async function getCurrentUser(): Promise<User | null> {
  try {
    return await request<User>('/auth/me')
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null
    throw error
  }
}

export function register(credentials: Credentials): Promise<User> {
  return request<User>('/auth/register', { method: 'POST', body: JSON.stringify(credentials) })
}

// The session lives in an httpOnly cookie set by the API: there is no token to store here.
export function login(credentials: Credentials): Promise<void> {
  return request<void>('/auth/login', { method: 'POST', body: JSON.stringify(credentials) })
}

export function logout(): Promise<void> {
  return request<void>('/auth/logout', { method: 'POST' })
}
