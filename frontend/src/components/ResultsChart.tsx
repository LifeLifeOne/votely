import type { PollResults } from '../api/types'

export function ResultsChart({ results }: { results: PollResults }) {
  return (
    <section className="results" aria-label="Results">
      <p className="meta">
        {results.total_votes} {results.total_votes === 1 ? 'vote' : 'votes'}
      </p>
      {results.options.map((option) => (
        <div key={option.option_id}>
          <div className="result-label">
            <span>{option.label}</span>
            <span className="meta">
              {option.percentage}% · {option.votes}
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
