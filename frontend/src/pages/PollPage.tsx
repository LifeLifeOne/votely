import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router'

import { ApiError } from '../api/client'
import { getPoll, getResults } from '../api/polls'
import { ResultsChart } from '../components/ResultsChart'
import { ErrorMessage, Loading } from '../components/Status'

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
      {poll.data.is_closed && <span className="badge">Closed</span>}
      {results.data && <ResultsChart results={results.data} />}
    </article>
  )
}
