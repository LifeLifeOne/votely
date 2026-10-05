import { Route, Routes } from 'react-router'

import { Layout } from './components/Layout'
import { NotFoundPage } from './pages/NotFoundPage'
import { PollListPage } from './pages/PollListPage'
import { PollPage } from './pages/PollPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<PollListPage />} />
        <Route path="polls/:pollId" element={<PollPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
