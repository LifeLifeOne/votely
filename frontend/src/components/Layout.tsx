import { Link, Outlet, useNavigate } from 'react-router'

import { useCurrentUser, useLogout } from '../auth/hooks'

export function Layout() {
  const { data: user } = useCurrentUser()
  const logout = useLogout()
  const navigate = useNavigate()

  return (
    <div className="container">
      <header className="header">
        <Link to="/" className="brand">
          Votely
        </Link>
        <nav className="nav" aria-label="Account">
          {user ? (
            <>
              <Link to="/polls/new" className="button">
                New poll
              </Link>
              <span className="meta user-email">{user.email}</span>
              <button
                type="button"
                className="secondary"
                onClick={() => logout.mutate(undefined, { onSuccess: () => navigate('/') })}
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Log in</Link>
              <Link to="/register" className="button">
                Sign up
              </Link>
            </>
          )}
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
