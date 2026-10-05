import { type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'

import { useLogin } from '../auth/hooks'
import { safeRedirect } from '../auth/redirect'
import { ErrorMessage } from '../components/Status'

export function LoginPage() {
  const login = useLogin()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    login.mutate(
      { email: String(form.get('email')), password: String(form.get('password')) },
      { onSuccess: () => navigate(safeRedirect(searchParams.get('next'))) },
    )
  }

  return (
    <section className="card auth-card">
      <h1>Log in</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input name="email" type="email" autoComplete="email" required />
        </label>
        <label>
          Password
          <input name="password" type="password" autoComplete="current-password" required />
        </label>
        {login.isError && <ErrorMessage error={login.error} />}
        <button type="submit" disabled={login.isPending}>
          Log in
        </button>
      </form>
      <p className="meta form-footer">
        No account yet? <Link to="/register">Sign up</Link>
      </p>
    </section>
  )
}
