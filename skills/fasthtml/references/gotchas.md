# FastHTML: Gotchas & Common Mistakes

## Top LLM Mistakes

### 1. Using `class_=` Instead of `cls=`

```python
# WRONG
Div(class_="container")

# CORRECT
Div(cls="container")
```

### 2. Returning JSON or Using FastAPI Patterns

```python
# WRONG — FastHTML is not FastAPI
@rt('/todos')
def get():
    return {"todos": todos()}    # Never return dicts/JSON

# CORRECT
@rt('/todos')
def get():
    return Ul(*todos())          # Return FT components
```

### 3. Using `uvicorn.run()` Instead of `serve()`

```python
# WRONG
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# CORRECT
serve()                           # or serve(host='0.0.0.0', port=5001)
```

### 4. Thinking Multiple Functions With the Same Name Is an Error

```python
# CORRECT — each handles a different HTTP method
@rt('/')
def get(): return P("GET response")

@rt('/')
def post(): return P("POST response")

@rt('/')
def delete(): return P("DELETE response")
```

### 5. Forgetting `index` Maps to `/`

```python
# CORRECT — no need for @rt('/')
@rt
def index(): return Titled("Home", P("Welcome"))

# Equivalent to:
@rt('/')
def get(): return Titled("Home", P("Welcome"))
```

### 6. Using Deprecated `hx_on` Syntax

```python
# WRONG (deprecated)
Button("Submit", hx_on="htmx:afterRequest:this.textContent='Done'")

# CORRECT (double underscore = colon)
Button("Submit",
       hx_post="/submit",
       hx_on__after_request="this.textContent='Done'")
```

### 7. `fill_form` Matches `name`, Not `id`

```python
# WRONG — fill_form looks at `name` attribute
Input(id="title")           # fill_form won't populate this

# CORRECT
Input(name="title")         # fill_form matches on `name`
Input(id="title", name="title")   # both set = safe
```

### 8. Not Using `hx_swap_oob` for Multi-Region Updates

```python
# WRONG — can't update multiple DOM regions from one HTMX response
@rt('/add')
def post(title: str):
    todo = todos.insert(Todo(title=title))
    counter_update = Span(todos.count)   # This won't reach the counter
    return Li(todo.title), counter_update

# CORRECT — return tuple; OOB elements need id + hx_swap_oob
@rt('/add')
def post(title: str):
    todo = todos.insert(Todo(title=title))
    return (
        Li(todo.title),                                    # → hx_target
        Span(todos.count, id="counter", hx_swap_oob="true")  # → updates #counter
    )
```

### 9. Missing `id` on OOB Elements

```python
# WRONG — OOB elements must have an id
Span("5 todos", hx_swap_oob="true")    # No id = no swap target

# CORRECT
Span("5 todos", id="todo-count", hx_swap_oob="true")
```

### 10. Using `@app.get` When You Need Multiple Methods

```python
# AWKWARD — need separate decorators per method
@app.get('/todos/{id}')
def get_todo(id: int): ...

@app.delete('/todos/{id}')
def delete_todo(id: int): ...

# PREFERRED — @rt with function name convention
@rt('/todos/{id}')
def get(id: int): ...

@rt('/todos/{id}')
def delete(id: int): ...
```

### 11. Misunderstanding the `auth` Parameter

```python
# WRONG — `auth` is NOT from user input; it's injected by Beforeware
@rt('/dashboard')
def get(auth: str):           # auth = whatever Beforeware set in req.scope['auth']
    return Titled(f"Hi, {auth}")

# If Beforeware isn't configured, `auth` is None/missing
# Configure Beforeware to populate it:
def before(req, sess):
    req.scope['auth'] = sess.get('user')

app, rt = fast_app(before=Beforeware(before))
```

### 12. Raw SQL Injection Risk

```python
# DANGEROUS — never interpolate user input directly
@rt('/search')
def get(q: str):
    # SQL injection vulnerability!
    results = db.q(f"SELECT * FROM items WHERE name LIKE '%{q}%'")

# SAFE — use parameterized queries
    results = db.q("SELECT * FROM items WHERE name LIKE ?", [f'%{q}%'])

# SAFE — use MiniDataAPI's where
    results = items(where="name LIKE ?", where_args=[f'%{q}%'])
```

### 13. Confusing `fast_app()` Return Values

```python
# No database → 2 return values
app, rt = fast_app()

# With database → 4 return values (table object + dataclass)
app, rt, todos, Todo = fast_app('app.db', id=int, title=str, pk='id')
#                               ^table   ^dataclass

# With multiple tables → destructure accordingly
app, rt, (users, User), (todos, Todo) = fast_app('app.db', tbls=...)
```

### 14. `from fasthtml.common import *` Is Required

The wildcard import is intentional — all FT tags, fast_app, serve, rt, etc. are loaded this way.

```python
# WRONG
from fasthtml import app, rt, Div, P

# CORRECT
from fasthtml.common import *
```

### 15. Forgetting Status Codes on Redirects After POST

```python
# WRONG — 200 on a redirect causes issues (browser won't redirect)
@rt('/submit')
def post():
    return RedirectResponse('/')

# CORRECT — use 303 See Other for POST → redirect
@rt('/submit')
def post():
    return RedirectResponse('/', status_code=303)
```

### 16. SVG imports — `SvgPath` does not exist; use `Path as SvgPath`

`fasthtml.svg` exports `Path` and `Text` — **not** `SvgPath` or `SvgText`.

- `SvgPath` is NOT a real export — `from fasthtml.svg import SvgPath` will fail
- `Path` shadows `pathlib.Path` if both are imported
- `Text` clashes with common FastHTML component names

**Always alias on import:**

```python
# WRONG — SvgPath does not exist in fasthtml.svg
from fasthtml.svg import Svg, SvgPath

# WRONG — silent shadowing of pathlib.Path
from fasthtml.svg import Svg, Path, Text

# CORRECT — alias to avoid conflicts
from fasthtml.svg import Svg, Path as SvgPath, Text as SvgText
```

Also: SVG components are **not** in `fasthtml.common` — they must be imported explicitly
from `fasthtml.svg`.

---

## Debugging Tips

```python
# Print component structure
from fastcore.xml import to_xml
print(to_xml(MyComponent()))

# Enable debug tracebacks
app, rt = fast_app(debug=True)

# Starlette debug mode shows full traceback in browser
```

## Performance Notes

- FastHTML is single-threaded by default (Uvicorn with 1 worker)
- For concurrency, use `async def` route handlers with `await`
- SQLite is not suited for high write-concurrency — consider PostgreSQL for production
- Live reload (`live=True`) has overhead — disable in production
