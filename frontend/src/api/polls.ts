import { request } from './client'
import type { Poll, PollResults } from './types'

export function listPolls(): Promise<Poll[]> {
  return request<Poll[]>('/polls?limit=50')
}

export function getPoll(id: string): Promise<Poll> {
  return request<Poll>(`/polls/${id}`)
}

export function getResults(id: string): Promise<PollResults> {
  return request<PollResults>(`/polls/${id}/results`)
}

export interface NewPoll {
  question: string
  options: string[]
  closes_at?: string
}

export function createPoll(poll: NewPoll): Promise<Poll> {
  return request<Poll>('/polls', { method: 'POST', body: JSON.stringify(poll) })
}

export function vote(pollId: string, optionId: string): Promise<void> {
  return request<void>(`/polls/${pollId}/votes`, {
    method: 'POST',
    body: JSON.stringify({ option_id: optionId }),
  })
}
