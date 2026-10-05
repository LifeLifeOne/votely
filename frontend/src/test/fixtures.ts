import type { Poll, PollResults, User } from '../api/types'

export const PASSWORD = 'correct horse battery'

export const alice: User = {
  id: '6f1c1d8e-0000-4000-8000-000000000001',
  email: 'alice@example.com',
  created_at: '2026-01-01T10:00:00Z',
}

export const poll: Poll = {
  id: '6f1c1d8e-0000-4000-8000-0000000000aa',
  author_id: alice.id,
  question: 'Where should we deploy?',
  closes_at: null,
  created_at: '2026-01-02T10:00:00Z',
  is_closed: false,
  has_voted: false,
  options: [
    { id: '6f1c1d8e-0000-4000-8000-0000000000a1', label: 'AWS' },
    { id: '6f1c1d8e-0000-4000-8000-0000000000a2', label: 'GCP' },
  ],
}

export const results: PollResults = {
  poll_id: poll.id,
  total_votes: 4,
  options: [
    { option_id: poll.options[0].id, label: 'AWS', votes: 3, percentage: 75 },
    { option_id: poll.options[1].id, label: 'GCP', votes: 1, percentage: 25 },
  ],
}
