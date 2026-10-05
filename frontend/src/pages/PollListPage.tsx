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
      <header className="page-header">
        <div>
          <h1>Polls</h1>
          <p className="meta">Vote on open questions and follow the results live.</p>
        </div>
        {/* Anonymous visitors are sent to the login page first (RequireAuth). */}
        <Link to="/polls/new" className="button">
          New poll
        </Link>
      </header>
      {polls.data.length === 0 ? (
        <div className="card empty">
          <p className="meta">
            No polls yet. <Link to="/polls/new">Create the first one</Link>.
          </p>
        </div>
      ) : (
        <ul className="stack plain-list">
          {polls.data.map((poll) => (
            <li key={poll.id}>
              <Link to={`/polls/${poll.id}`} className="card poll-link">
                <div>
                  <span className="poll-question">{poll.question}</span>
                  <span className="meta">
                    {poll.options.length} options · {new Date(poll.created_at).toLocaleDateString()}
                  </span>
                  <span className="badges">
                    {poll.is_closed ? (
                      <span className="badge closed">Closed</span>
                    ) : (
                      <span className="badge open">Open</span>
                    )}
                    {poll.has_voted && <span className="badge">Voted</span>}
                  </span>
                </div>
                <span className="poll-arrow" aria-hidden="true">
                  →
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  )
}
