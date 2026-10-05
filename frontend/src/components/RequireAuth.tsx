import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router'

import { useCurrentUser } from '../auth/hooks'
import { Loading } from './Status'

/** Send anonymous visitors to the login page, then back here once logged in. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { data: user, isPending } = useCurrentUser()
  const location = useLocation()

  if (isPending) return <Loading />
  if (!user) {
    return <Navigate to={`/login?next=${encodeURIComponent(location.pathname)}`} replace />
  }
  return children
}
