import { Link, Outlet } from 'react-router'

export function Layout() {
  return (
    <div className="container">
      <header className="header">
        <Link to="/" className="brand">
          Votely
        </Link>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
