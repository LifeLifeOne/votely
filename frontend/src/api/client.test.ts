import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'

import { server } from '../test/server'
import { ApiError, request } from './client'

describe('request', () => {
  it('returns the JSON body on success', async () => {
    server.use(http.get('/api/v1/ping', () => HttpResponse.json({ pong: true })))

    await expect(request('/ping')).resolves.toEqual({ pong: true })
  })

  it('returns undefined for 204 responses', async () => {
    server.use(http.post('/api/v1/ping', () => new HttpResponse(null, { status: 204 })))

    await expect(request('/ping', { method: 'POST' })).resolves.toBeUndefined()
  })

  it('exposes the API error message and status', async () => {
    server.use(
      http.get('/api/v1/ping', () => HttpResponse.json({ detail: 'poll closed' }, { status: 409 })),
    )

    await expect(request('/ping')).rejects.toEqual(new ApiError(409, 'poll closed'))
  })

  it('uses the first message of a validation error', async () => {
    server.use(
      http.get('/api/v1/ping', () =>
        HttpResponse.json({ detail: [{ msg: 'field required' }] }, { status: 422 }),
      ),
    )

    await expect(request('/ping')).rejects.toThrow('field required')
  })

  it('falls back to the status when the body is not JSON', async () => {
    server.use(http.get('/api/v1/ping', () => new HttpResponse('Bad gateway', { status: 502 })))

    await expect(request('/ping')).rejects.toMatchObject({ status: 502 })
  })
})
