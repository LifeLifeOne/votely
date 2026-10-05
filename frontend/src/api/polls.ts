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
