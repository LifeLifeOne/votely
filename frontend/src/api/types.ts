// Mirrors the backend response schemas (backend/app/api/schemas.py).

export interface User {
  id: string
  email: string
  created_at: string
}

export interface Option {
  id: string
  label: string
}

export interface Poll {
  id: string
  author_id: string | null
  question: string
  closes_at: string | null
  created_at: string
  is_closed: boolean
  has_voted: boolean
  options: Option[]
}

export interface OptionResult {
  option_id: string
  label: string
  votes: number
  percentage: number
}

export interface PollResults {
  poll_id: string
  total_votes: number
  options: OptionResult[]
}
