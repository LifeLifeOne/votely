import type { PollResults } from '../api/types'

export function ResultsChart({ results }: { results: PollResults }) {
  const topVotes = Math.max(...results.options.map((option) => option.votes))

  return (
    <section className="results" aria-labelledby="results-title">
      <h2 id="results-title">
        Results
        <span className="meta">
          {results.total_votes} {results.total_votes === 1 ? 'vote' : 'votes'}
        </span>
      </h2>
      {results.options.map((option) => (
        <div
          key={option.option_id}
          className={option.votes > 0 && option.votes === topVotes ? 'leader' : undefined}
        >
          <div className="result-label">
            <span>{option.label}</span>
            <span className="result-value">
              {option.percentage}% <span className="meta">· {option.votes}</span>
            </span>
          </div>
          <div
            className="bar"
            role="meter"
            aria-label={option.label}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={option.percentage}
          >
            <div className="bar-fill" style={{ width: `${option.percentage}%` }} />
          </div>
        </div>
      ))}
    </section>
  )
}
