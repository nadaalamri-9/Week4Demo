// A second protected page, this one fetching data on mount instead of
// reading it from context. Good one to demo with DevTools open: the
// request to /users/profile carries the Authorization header, and the
// response only exists because the token checked out.

import { useEffect, useState } from 'react'
import { apiRequest } from '../api'
import { useAuth } from '../AuthContext'

export default function Profile() {
  const { token } = useAuth()
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    apiRequest('/users/profile', { token })
      .then(setProfile)
      .catch((err) => setError(err.message))
  }, [token])

  return (
    <div className="card">
      <h1>Profile</h1>
      {error && <p className="error">{error}</p>}
      {profile ? (
        <>
          <p>{profile.message}</p>
          <ul>
            <li><strong>Role:</strong> {profile.your_role}</li>
          </ul>
          <p>{profile.tip}</p>
        </>
      ) : (
        !error && <p>Loading...</p>
      )}
    </div>
  )
}
