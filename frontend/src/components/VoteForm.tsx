import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { Link } from 'react-router'

import { vote } from '../api/polls'
import type { Poll } from '../api/types'
import { useCurrentUser } from '../auth/hooks'
import { ErrorMessage } from './Status'

export function VoteForm({ poll }: { poll: Poll }) {
  const { data: user } = useCurrentUser()
  const [optionId, setOptionId] = useState<string | null>(null)
  const queryClient = useQueryClient()
  const voting = useMutation({
    mutationFn: (selected: string) => vote(poll.id, selected),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: ['poll', poll.id] }),
        queryClient.invalidateQueries({ queryKey: ['results', poll.id] }),
        queryClient.invalidateQueries({ queryKey: ['polls'] }),
      ]),
  })

  if (poll.is_closed) return <p className="meta">This poll is closed.</p>
  if (poll.has_voted) return <p className="success">Thanks, your vote has been recorded.</p>
  if (!user) {
    return (
      <p className="meta">
        <Link to={`/login?next=${encodeURIComponent(`/polls/${poll.id}`)}`}>Log in</Link> to vote.
      </p>
    )
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (optionId) voting.mutate(optionId)
  }

  return (
    <form onSubmit={handleSubmit}>
      <fieldset>
        <legend>Your vote</legend>
        {poll.options.map((option) => (
          <label className="choice" key={option.id}>
            <input
              type="radio"
              name="option"
              value={option.id}
              checked={optionId === option.id}
              onChange={() => setOptionId(option.id)}
            />
            {option.label}
          </label>
        ))}
      </fieldset>
      {voting.isError && <ErrorMessage error={voting.error} />}
      <button type="submit" disabled={!optionId || voting.isPending}>
        Vote
      </button>
    </form>
  )
}
