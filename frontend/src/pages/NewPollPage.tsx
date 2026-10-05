import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router'

import { createPoll } from '../api/polls'
import { ErrorMessage } from '../components/Status'

// Same limits as the API (backend/app/api/schemas.py).
const MIN_OPTIONS = 2
const MAX_OPTIONS = 10

export function NewPollPage() {
  const [options, setOptions] = useState<string[]>(['', ''])
  const [formError, setFormError] = useState<string | null>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const creation = useMutation({
    mutationFn: createPoll,
    onSuccess: (poll) => {
      void queryClient.invalidateQueries({ queryKey: ['polls'] })
      navigate(`/polls/${poll.id}`)
    },
  })

  function updateOption(index: number, value: string) {
    setOptions((current) => current.map((option, i) => (i === index ? value : option)))
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const labels = options.map((option) => option.trim())
    if (new Set(labels.map((label) => label.toLowerCase())).size !== labels.length) {
      setFormError('Options must be unique.')
      return
    }
    setFormError(null)
    const closesAt = String(form.get('closes_at') ?? '')
    creation.mutate({
      question: String(form.get('question')).trim(),
      options: labels,
      // datetime-local has no timezone: convert the local time to an absolute ISO date.
      ...(closesAt && { closes_at: new Date(closesAt).toISOString() }),
    })
  }

  return (
    <section className="card">
      <h1>New poll</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Question
          <input name="question" minLength={3} maxLength={200} required />
        </label>
        <fieldset>
          <legend>Options</legend>
          {options.map((option, index) => (
            <div className="option-row" key={index}>
              <input
                aria-label={`Option ${index + 1}`}
                value={option}
                onChange={(event) => updateOption(index, event.target.value)}
                maxLength={100}
                required
              />
              {options.length > MIN_OPTIONS && (
                <button
                  type="button"
                  className="secondary"
                  aria-label={`Remove option ${index + 1}`}
                  onClick={() => setOptions((current) => current.filter((_, i) => i !== index))}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          {options.length < MAX_OPTIONS && (
            <button
              type="button"
              className="secondary"
              onClick={() => setOptions((current) => [...current, ''])}
            >
              Add an option
            </button>
          )}
        </fieldset>
        <label>
          Closing date (optional)
          <input name="closes_at" type="datetime-local" />
        </label>
        {formError && (
          <p role="alert" className="error">
            {formError}
          </p>
        )}
        {creation.isError && <ErrorMessage error={creation.error} />}
        <button type="submit" disabled={creation.isPending}>
          Create poll
        </button>
      </form>
    </section>
  )
}
