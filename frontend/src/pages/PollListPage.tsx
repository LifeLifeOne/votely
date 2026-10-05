import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router'

import { listPolls } from '../api/polls'
import { ErrorMessage, Loading } from '../components/Status'

export function PollListPage() {
  const polls = useQuery({ queryKey: ['polls'], queryFn: listPolls })

  if (polls.isPending) return <Loading />
  if (polls.isError) return <ErrorMessage error={polls.error} />

  return (
    <>
      <h1>Polls</h1>
      {polls.data.length === 0 ? (
        <p className="meta">No polls yet.</p>
      ) : (
        <ul className="stack plain-list">
          {polls.data.map((poll) => (
            <li key={poll.id}>
              <Link to={`/polls/${poll.id}`} className="card poll-link">
                <strong>{poll.question}</strong>
                <div className="meta">
                  {poll.options.length} options · {new Date(poll.created_at).toLocaleDateString()}{' '}
                  {poll.is_closed && <span className="badge">Closed</span>}{' '}
                  {poll.has_voted && <span className="badge">Voted</span>}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  )
}
