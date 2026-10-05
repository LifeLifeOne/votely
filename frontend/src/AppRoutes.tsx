import { Route, Routes } from 'react-router'

import { Layout } from './components/Layout'
import { RequireAuth } from './components/RequireAuth'
import { LoginPage } from './pages/LoginPage'
import { NewPollPage } from './pages/NewPollPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { PollListPage } from './pages/PollListPage'
import { PollPage } from './pages/PollPage'
import { RegisterPage } from './pages/RegisterPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<PollListPage />} />
        <Route
          path="polls/new"
          element={
            <RequireAuth>
              <NewPollPage />
            </RequireAuth>
          }
        />
        <Route path="polls/:pollId" element={<PollPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
