import { ApiError } from '../api/client'

export function Loading() {
  return (
    <p role="status" className="meta">
      Loading…
    </p>
  )
}

export function ErrorMessage({ error }: { error: unknown }) {
  const message = error instanceof ApiError ? error.message : 'Something went wrong.'
  return (
    <p role="alert" className="error">
      {capitalize(message)}
    </p>
  )
}

function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1)
}
