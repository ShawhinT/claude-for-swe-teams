# FastHTML: Auth & Sessions

## Sessions

FastHTML uses signed cookies for sessions (via Starlette's `SessionMiddleware`).

```python
app, rt = fast_app(secret_key='your-secret-key-here')

@rt('/login')
def post(sess, username: str, password: str):
    if check_password(username, password):
        sess['user'] = username
        return RedirectResponse('/', status_code=303)
    return P("Invalid credentials", cls="error")

@rt('/logout')
def get(sess):
    del sess['user']
    return RedirectResponse('/login', status_code=303)

@rt('/profile')
def get(sess):
    user = sess.get('user')
    if not user:
        return RedirectResponse('/login', status_code=303)
    return Titled(f"Profile: {user}", P(f"Welcome, {user}"))
```

## Beforeware (Middleware for Auth)

`Beforeware` runs before every request, setting `auth` in the route's scope.

```python
def auth_check(req, sess):
    """Return None to allow, or a Response to redirect/block."""
    public_paths = {'/', '/login', '/register'}
    if req.url.path in public_paths:
        return  # allow
    user = sess.get('user')
    if not user:
        return RedirectResponse('/login', status_code=303)
    # Set auth so route handlers can use it
    req.scope['auth'] = user

app, rt = fast_app(
    before=Beforeware(auth_check, skip=[r'/static/.*'])
)

# `auth` is now available as an injected parameter
@rt('/dashboard')
def get(auth):
    return Titled(f"Dashboard", P(f"Hello, {auth}"))
```

`skip` accepts regex patterns for paths that bypass the Beforeware.

## Database-Backed Auth

Full example with user table:

```python
app, rt, users, User = fast_app(
    'data/app.db',
    tbls=dict(users=dict(id=int, name=str, email=str, pwd=str, pk='id'))
)

import hashlib

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def auth_check(req, sess):
    public = {'/', '/login', '/register'}
    if req.url.path in public: return
    uid = sess.get('user_id')
    if not uid: return RedirectResponse('/login', status_code=303)
    try:
        req.scope['auth'] = users[uid]
    except:
        return RedirectResponse('/login', status_code=303)

app, rt = fast_app('data/app.db', before=Beforeware(auth_check, skip=[r'/static/.*']),
                    tbls=dict(users=dict(id=int, name=str, email=str, pwd=str, pk='id')))

@rt('/register')
def post(sess, name: str, email: str, pwd: str):
    try:
        user = users.insert(User(name=name, email=email, pwd=hash_pwd(pwd)))
        sess['user_id'] = user.id
        return RedirectResponse('/', status_code=303)
    except:
        return P("Email already taken")

@rt('/login')
def post(sess, email: str, pwd: str):
    matches = users(where=f"email='{email}' AND pwd='{hash_pwd(pwd)}'")
    if not matches:
        return P("Invalid credentials")
    sess['user_id'] = matches[0].id
    return RedirectResponse('/', status_code=303)
```

## HTTP Basic Auth (Simple)

```python
import base64

def basic_auth(req, sess):
    auth_header = req.headers.get('Authorization', '')
    if not auth_header.startswith('Basic '):
        return Response(
            "Unauthorized",
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="App"'}
        )
    credentials = base64.b64decode(auth_header[6:]).decode()
    username, _, password = credentials.partition(':')
    if username != 'admin' or password != 'secret':
        return Response("Forbidden", status_code=403)
    req.scope['auth'] = username
```

## Cookies (Direct)

```python
from starlette.responses import Response

@rt('/set-cookie')
def get():
    response = Response("Cookie set!")
    response.set_cookie('theme', 'dark', max_age=86400, httponly=True)
    return response

@rt('/read-cookie')
def get(req):
    theme = req.cookies.get('theme', 'light')
    return P(f"Theme: {theme}")
```

## Secret Key Best Practice

Never hardcode the secret key in production:

```python
import os
from fasthtml.common import *

SECRET = os.environ.get('SESSION_SECRET', 'dev-only-secret')
app, rt = fast_app(secret_key=SECRET)
```
