// One small wrapper around fetch so every page doesn't repeat the same
// boilerplate: JSON headers, attaching the token, error handling.

const BASE_URL = 'http://localhost:8000'

export async function apiRequest(path, { method = 'GET', body, token } = {}) {
  const headers = { 'Content-Type': 'application/json' }

  // TODO(6): if we were given a token, add it to the headers as
  //   Authorization: Bearer <token>
  // This single header is what makes protected routes work -- the
  // backend's HTTPBearer dependency reads exactly this. Until you add
  // it, every protected call comes back 403 even when you're logged in.

  if (token) {
  headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  // fetch only rejects on network failure -- a 401 or 403 still
  // "succeeds" as far as fetch is concerned. We convert non-2xx
  // responses into thrown errors so callers can use try/catch.
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    // FastAPI puts its error message in a "detail" field.
    throw new Error(data.detail || `Request failed (${response.status})`)
  }

  return response.json()
}
