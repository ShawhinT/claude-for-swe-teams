---
name: fasthtml
description: Expert FastHTML (python-fasthtml) assistant. Use when the user is building, reviewing, or asking about a FastHTML web application — including components, routing, HTMX integration, forms, database, styling, auth, or deployment. FastHTML is a Python hypermedia framework, not FastAPI.
---

# FastHTML Expert

FastHTML is a Python web framework where the server returns **HTML fragments, not JSON**. It uses HTMX for interactivity. There is no JavaScript frontend, no Jinja2, no React — just Python functions that return HTML.

## The Foundational Stack

```
FastHTML → Starlette (ASGI) → Uvicorn
         → HTMX (browser interactivity, ~14KB)
         → fastcore (FT component system)
         → fastlite / MiniDataAPI (SQLite)
         → Tailwind CSS + DaisyUI (styling)
```

## Critical Rules (What LLMs Get Wrong)

1. **`cls=`, never `class_=`** — `cls` is the CSS class attribute
2. **Underscores → hyphens in attribute names** — `hx_get` → `hx-get`, `data_value` → `data-value`
3. **Use `serve()`, not uvicorn.run()** — `if __name__ == "__main__": serve()`
4. **`index` maps to `/`** — `@rt def index(): ...` routes to GET /
5. **Multiple same-name functions are fine** — each handles a different HTTP method via its function name (`get`, `post`, `delete`, etc.)
6. **Never return JSON** — always return FT components or HTML strings
7. **`fill_form` matches on `name` attribute** — not `id`
8. **Always set `pico=False`** — never use PicoCSS; Tailwind + DaisyUI is the required stack

## Minimal App

```python
from fasthtml.common import *

app, rt = fast_app()

@rt('/')
def get():
    return Titled("Hello", P("World"))

serve()
```

Run with: `python main.py` (starts at http://localhost:5001)

## Core Component Pattern

```python
# Positional args = children | keyword args = attributes
Div(P("hello"), cls="container", id="main")
# → <div class="container" id="main"><p>hello</p></div>

# Reusable components are plain Python functions (PascalCase by convention)
def Card(title, body):
    return Article(Header(H2(title)), P(body), cls="card")

# Return multiple elements as a tuple (HTMX OOB swaps)
@rt('/update')
def post():
    return Div("updated main"), Div("updated sidebar", hx_swap_oob="true", id="sidebar")
```

## fast_app() Quick Reference

```python
# No database
app, rt = fast_app()

# With database table
app, rt, todos, Todo = fast_app('data/app.db', id=int, title=str, done=bool, pk='id')

# With multiple tables
app, rt, (users, User), (todos, Todo) = fast_app(
    'data/app.db',
    tbls=dict(
        users=dict(id=int, name=str, email=str, pk='id'),
        todos=dict(id=int, title=str, done=bool, user_id=int, pk='id')
    )
)

# Standard setup with Tailwind + DaisyUI
app, rt = fast_app(
    pico=False,         # Always — never use PicoCSS
    hdrs=(Link(rel='stylesheet', href='/static/output.css'),),
    live=True,          # Live reload (dev only)
    secret_key='...',   # For sessions
)
```

## Reference Files

Load these as needed based on the task:

| Task | Reference File |
|------|---------------|
| Building components, routing, path/query params | [`references/components-and-routing.md`](references/components-and-routing.md) |
| HTMX interactivity, partial updates, OOB swaps | [`references/htmx-integration.md`](references/htmx-integration.md) |
| Forms, validation, database CRUD | [`references/forms-and-data.md`](references/forms-and-data.md) |
| Styling (Tailwind + DaisyUI), static files, JS | [`references/styling-and-ui.md`](references/styling-and-ui.md) |
| Auth, sessions, cookies, Beforeware | [`references/auth-and-sessions.md`](references/auth-and-sessions.md) |
| WebSockets, testing, deployment, middleware | [`references/advanced.md`](references/advanced.md) |
| Debugging, common mistakes, gotchas | [`references/gotchas.md`](references/gotchas.md) |
