import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router'

import { ApiError } from '../api/client'
import { getPoll, getResults } from '../api/polls'
import { ResultsChart } from '../components/ResultsChart'
import { ErrorMessage, Loading } from '../components/Status'
import { VoteForm } from '../components/VoteForm'

// Results are refreshed periodically so votes from other users show up without reloading.
export const RESULTS_REFRESH_MS = 5000

export function PollPage() {
  const { pollId = '' } = useParams()
  const poll = useQuery({ queryKey: ['poll', pollId], queryFn: () => getPoll(pollId) })
  const results = useQuery({
    queryKey: ['results', pollId],
    queryFn: () => getResults(pollId),
    refetchInterval: RESULTS_REFRESH_MS,
    enabled: poll.isSuccess,
  })

  if (poll.isPending) return <Loading />
  if (poll.isError) {
    if (poll.error instanceof ApiError && poll.error.status === 404) {
      return <h1>Poll not found</h1>
    }
    return <ErrorMessage error={poll.error} />
  }

  return (
    <article className="card">
      <h1>{poll.data.question}</h1>
      <p className="poll-status meta">
        {poll.data.is_closed ? (
          <span className="badge closed">Closed</span>
        ) : (
          <span className="badge open">Open</span>
        )}
        {poll.data.closes_at && !poll.data.is_closed && (
          <span>Closes on {new Date(poll.data.closes_at).toLocaleString()}</span>
        )}
      </p>
      <VoteForm poll={poll.data} />
      {results.data && <ResultsChart results={results.data} />}
    </article>
  )
}
