import { type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'

import { useRegister } from '../auth/hooks'
import { ErrorMessage } from '../components/Status'

// Same rule as the API (backend/app/api/schemas.py), checked early for a better experience.
export const MIN_PASSWORD_LENGTH = 12

export function RegisterPage() {
  const registration = useRegister()
  const navigate = useNavigate()

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    registration.mutate(
      { email: String(form.get('email')), password: String(form.get('password')) },
      { onSuccess: () => navigate('/') },
    )
  }

  return (
    <section className="card auth-card">
      <h1>Create an account</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input name="email" type="email" autoComplete="email" required />
        </label>
        <div className="field">
          <label>
            Password
            <input
              name="password"
              type="password"
              autoComplete="new-password"
              minLength={MIN_PASSWORD_LENGTH}
              maxLength={128}
              aria-describedby="password-hint"
              required
            />
          </label>
          <span id="password-hint" className="meta">
            At least {MIN_PASSWORD_LENGTH} characters.
          </span>
        </div>
        {registration.isError && <ErrorMessage error={registration.error} />}
        <button type="submit" disabled={registration.isPending}>
          Sign up
        </button>
      </form>
      <p className="meta form-footer">
        Already registered? <Link to="/login">Log in</Link>
      </p>
    </section>
  )
}
