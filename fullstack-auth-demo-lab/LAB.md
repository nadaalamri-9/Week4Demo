# Lab: JWT Authentication + RBAC, Step by Step

This is the lab version of the full-stack auth demo. The structure,
routes, and pages are all in place -- but eight key pieces of the auth
flow are missing, marked `TODO(1)` through `TODO(8)`. You'll fill them
in during class, in order. Each step ends with a checkpoint you can
verify yourself, so if you fall behind you'll know exactly where you
stand.

The app runs from the very first step. Endpoints whose TODO isn't done
yet return a 500 (`NotImplementedError`) -- that's the lab telling you
which step you're on, not a bug.

## Setup (before class)

Backend, in one terminal:

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend, in another:

```
cd frontend
npm install
npm run dev
```

Backend: http://localhost:8000/docs -- Frontend: http://localhost:5173

`--reload` matters: uvicorn restarts itself every time you save, so you
see each TODO take effect immediately. Vite does the same for the
frontend.

---

## Part 1 -- Backend (`backend/security.py`)

Test these with the interactive docs at http://localhost:8000/docs.
The frontend can wait until Part 2.

### TODO(1) -- `hash_password`

Why we never store passwords: if the database leaks, plain-text
passwords burn every user (and every other site where they reused the
password). bcrypt hashes can't be reversed.

**Checkpoint:** in /docs, `POST /auth/register` with an email, a
password, and role `"user"` returns **201** and a user object with no
password in it. Before this step it returned 500.

### TODO(2) -- `verify_password`

The other half: comparing a login attempt against the stored hash.

**Checkpoint:** none on its own -- login also needs TODO(3). Do them
back to back.

### TODO(3) -- `create_access_token`

Build the JWT: who the token is about (`sub`), what they're allowed to
do (`role`), and when it dies (`exp`).

**Checkpoint:** `POST /auth/login` with the account from TODO(1)
returns **200** and an `access_token`. Paste that token into
https://jwt.io and look at the payload -- there are your three claims,
readable by anyone. Try logging in with a wrong password: **401**.

### TODO(4) -- `get_current_user`

The gatekeeper. Every protected route depends on this function: it
decodes the token, checks the signature and expiry, and loads the user
from the database.

**Checkpoint:** in /docs, click **Authorize** (top right), paste your
token, then call `GET /users/me` -- **200** with your account. Log out
of Authorize and try again -- **403** (no header at all). Authorize
with the token plus a typo -- **401** (bad signature). That's the
tamper-proofing in action.

### TODO(5) -- `require_admin`

RBAC in five lines. The dependency chain runs get_current_user first,
then checks one column.

**Checkpoint:** with your regular user's token, `GET /admin/stats`
returns **403**. Register a second account with role `"admin"`, log in
as it, authorize with the new token -- now it's **200**. One line of
difference in the route (`require_admin` vs `get_current_user`) is the
entire feature.

---

## Part 2 -- Frontend (`src/api.js`, `src/AuthContext.jsx`)

Open http://localhost:5173 with DevTools (Network tab) visible.

### TODO(6) -- attach the Authorization header (`api.js`)

The backend half is done; now the frontend has to actually send the
token with each request.

**Checkpoint:** indirect -- registering in the UI logs you in but the
dashboard would fail to load your user without this header. Finish
TODO(7) and come back if anything 403s.

### TODO(7) -- `login` (`AuthContext.jsx`)

Wire the login form to `POST /auth/login`, store the token, update
state.

**Checkpoint:** the big one. Log in through the UI -- you land on the
dashboard with your email and role showing. Refresh the page: still
logged in (that's localStorage). In DevTools > Network, click the
request to `/users/me` and find the `Authorization: Bearer ...` header
you added in TODO(6).

### TODO(8) -- `logout` (`AuthContext.jsx`)

**Checkpoint:** the Log out button actually logs you out -- you're
redirected to /login, and refreshing doesn't bring the session back.
Check DevTools > Application > Local Storage: the token is gone.

---

## Finished?

Full RBAC tour: register one account with role `user` and one with
role `admin`. As the user, note there's no Admin link in the navbar --
then type `/admin` into the URL bar anyway. You get bounced to the
dashboard by `ProtectedRoute`, and even if you bypassed that, the API
returns 403. As the admin, the link appears and `/admin` shows stats
plus every account.

The completed version of this code lives in `fullstack-auth-demo` --
same files, with every TODO filled in. Use it to check your work, not
to copy from.
