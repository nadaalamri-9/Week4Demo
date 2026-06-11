// Route map for the whole app. Three kinds of routes here:
//   public            -> /login, /register
//   logged-in only    -> /dashboard  (wrapped in ProtectedRoute)
//   admins only       -> /admin      (ProtectedRoute with adminOnly)

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import Admin from './pages/Admin'

export default function App() {
  return (
    // AuthProvider wraps the router so every page and the navbar can
    // read auth state. BrowserRouter uses real URLs (/dashboard, not
    // /#/dashboard) via the browser's history API.
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <main className="container">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* ProtectedRoute renders its children only when someone
                is logged in; otherwise it redirects to /login. */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            {/* Another protected page -- once ProtectedRoute exists,
                guarding a new route is just a matter of wrapping it. */}
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />

            {/* Same wrapper, one extra prop. adminOnly adds the role
                check on top of the login check. */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute adminOnly>
                  <Admin />
                </ProtectedRoute>
              }
            />

            {/* Anything else, including "/", lands on the dashboard --
                which itself redirects to /login if you're logged out. */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </BrowserRouter>
    </AuthProvider>
  )
}
