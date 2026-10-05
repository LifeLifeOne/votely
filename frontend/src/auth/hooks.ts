import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { getCurrentUser, login, logout, register, type Credentials } from '../api/auth'

const ME = ['me']

export function useCurrentUser() {
  return useQuery({ queryKey: ME, queryFn: getCurrentUser, staleTime: 60_000 })
}

// Logging in or out changes user-specific data (e.g. has_voted): refetch everything.

export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: login,
    onSuccess: () => queryClient.invalidateQueries(),
  })
}

export function useRegister() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (credentials: Credentials) => {
      await register(credentials)
      await login(credentials)
    },
    onSuccess: () => queryClient.invalidateQueries(),
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.setQueryData(ME, null)
      return queryClient.invalidateQueries()
    },
  })
}
