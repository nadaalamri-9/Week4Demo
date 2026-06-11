// The page every logged-in user can see. The user object was already
// loaded by AuthContext (via GET /users/me), so there's nothing to
// fetch here -- just display it.

import { useAuth } from '../AuthContext'

export default function Dashboard() {
  const { user } = useAuth()

  return (
    <div className="card">
      <h1>Dashboard</h1>
      <p>You are logged in. This page is behind a protected route.</p>
      <ul>
        <li><strong>ID:</strong> {user.id}</li>
        <li><strong>Email:</strong> {user.email}</li>
        <li><strong>Role:</strong> {user.role}</li>
      </ul>
      {user.role !== 'admin' && (
        <p>
          Try visiting <code>/admin</code> by typing it in the URL bar --
          you'll be redirected back here, and the API would refuse you
          anyway.
        </p>
      )}
    </div>
  )
}
