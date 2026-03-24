# FastHTML: Components & Routing

## FT Components (FastTags)

All standard HTML tags are Python callables imported via `from fasthtml.common import *`. Positional args = children, keyword args = attributes.

### Attribute Naming Rules

```python
# cls → class (Python reserved word)
Div(cls="container")           # → <div class="container">

# Underscores → hyphens
Div(hx_get="/data")            # → <div hx-get="/data">
Div(data_value="42")           # → <div data-value="42">

# Leading underscore stripped (for reserved words)
Label("Email", _for="email")   # → <label for="email">Email</label>

# Boolean attributes
Input(required=True)           # → <input required>
Input(required=False)          # → <input>  (omitted)

# Dict unpacking for special chars (e.g., Alpine.js)
Div(**{"@click": "open()", ":class": "{'open': isOpen}"})
```

### Available Tags

```python
# All standard HTML — imported from fasthtml.common
Html, Head, Body, Title, Meta, Link, Script, Style
H1, H2, H3, H4, H5, H6
P, Span, Div, Section, Article, Header, Footer, Main, Nav, Aside
A, Button, Form, Input, Label, Select, Option, Textarea
Ul, Ol, Li, Table, Thead, Tbody, Tr, Th, Td
Img, Video, Audio, Source, Canvas, Svg
```

### Reusable Components

Define as PascalCase Python functions:

```python
def Card(title: str, body: str, footer=None):
    parts = [Header(H2(title)), P(body)]
    if footer: parts.append(Footer(footer))
    return Article(*parts, cls="card")

def NavBar(brand: str, links: list[tuple]):
    return Nav(
        A(brand, href="/", cls="brand"),
        Ul(*[Li(A(text, href=href)) for text, href in links]),
        cls="navbar"
    )

def Badge(text, variant="primary"):
    return Span(text, cls=f"badge badge-{variant}")
```

### The `__ft__` Method

Any object with `__ft__` renders automatically when returned from a route:

```python
@dataclass
class Todo:
    id: int
    title: str
    done: bool = False

    def __ft__(self):
        return Li(
            Input(type="checkbox", checked=self.done,
                  hx_post=f"/todos/{self.id}/toggle",
                  hx_target=f"#todo-{self.id}",
                  hx_swap="outerHTML"),
            self.title,
            id=f"todo-{self.id}"
        )
```

### `@patch` for Retroactive `__ft__`

Use when the dataclass is generated (e.g., by fastlite):

```python
from fastcore.basics import patch

@patch
def __ft__(self: Todo):
    return Li(self.title, id=f"todo-{self.id}")
```

### Built-in Convenience Components

```python
# Titled: full page with <title> + <h1> + Container
Titled("My Page", P("Content"))

# AX: anchor with hx_get + target_id
AX("Click", hx_get="/data", target_id="result")
# → <a hx-get="/data" hx-target="#result">Click</a>

# Hidden input
Hidden(id="todo_id", value=42)

# CheckboxX: checkbox with preceding hidden field (reliable form submission)
CheckboxX(id="done", label="Mark done", checked=True)

# NotStr: embed raw HTML without escaping (only use with trusted content)
from fastcore.xml import NotStr
Div(NotStr("<strong>Bold</strong>"))
```

### Rendering to String

```python
from fastcore.xml import to_xml
html = to_xml(Div(P("Hello"), cls="test"))
# → '<div class="test"><p>Hello</p></div>'
```

---

## SVG Elements

SVG elements live in a separate module — **not** `fasthtml.common`.

### Import

```python
from fasthtml.svg import (
    Svg, G, Rect, Circle, Ellipse, Line, Polyline, Polygon,
    Path, Text, Tspan, Image, Use, Defs, Symbol, Marker,
    ClipPath, Mask, Filter, LinearGradient, RadialGradient, Stop,
    Animate, AnimateTransform, Title as SvgTitle, Desc
)
```

⚠️ **Name conflicts** — `Path` and `Text` clash with FastHTML and Python builtins.
Always alias them on import:

```python
from fasthtml.svg import Path as SvgPath, Text as SvgText
```

### Basic SVG

```python
from fasthtml.svg import Svg, Circle, Rect

Svg(
    Circle(cx="50", cy="50", r="40", fill="#087CA7"),
    Rect(x="10", y="10", width="80", height="80", fill="none", stroke="white"),
    viewBox="0 0 100 100",
    width="200",
    height="200",
)
```

### Attribute rules

Same rules as FT components — underscores become hyphens:
- `stroke_width` → `stroke-width`
- `fill_opacity` → `fill-opacity`
- `text_anchor` → `text-anchor`
- `font_family` → `font-family`

### Path fluent API

`Path` (alias `SvgPath`) supports a method-chaining API for `d` commands:

```python
from fasthtml.svg import Path as SvgPath

path = (SvgPath(fill="none", stroke="#087CA7", stroke_width="2")
        .M(10, 80)          # Move to
        .C(40, 10, 65, 10, 95, 80)  # Cubic Bezier
        .S(150, 150, 180, 80))      # Smooth Bezier

# Supported commands: M, m, L, l, H, h, V, v, C, c, S, s,
#                     Q, q, T, t, A, a, Z
```

Each method appends to the `d` attribute and returns `self`, so chains work inline.

### Responsive SVG

Use `viewBox` + `width="100%"` for responsive behaviour. Set `style="min-width:…"` when
you need a minimum render size inside a scrollable container:

```python
Div(
    Svg(..., viewBox="0 0 900 140", style="min-width:700px;width:100%"),
    cls="overflow-x-auto"
)
```

---

## Routing

### The `@rt` Decorator — Three Styles

```python
app, rt = fast_app()

# Style 1: Explicit path — function name sets HTTP method
@rt('/')
def get(): return P("GET /")

@rt('/')
def post(): return P("POST /")

@rt('/')
def delete(): return P("DELETE /")

# Style 2: No argument — function name becomes the path
@rt
def about(): return P("About")    # → GET /about

@rt
def index(): return P("Home")     # → GET /  (special case)

# Style 3: app.get / app.post / etc.
@app.get('/users')
def list_users(): return Ul(*[Li(u.name) for u in users()])
```

### Path Parameters

```python
@rt('/users/{user_id}')
def get(user_id: int):     # Type enforced; 404 on wrong type
    return users[user_id].__ft__()

@rt('/posts/{slug}')
def get(slug: str):
    return P(slug)

@rt('/orgs/{org}/repos/{repo}')
def get(org: str, repo: str):
    return Div(f"{org}/{repo}")
```

### Query Parameters

```python
# Extracted by name + type conversion
@rt('/search')
def get(q: str = '', page: int = 1, limit: int = 20):
    results = items(where=f"name LIKE '%{q}%'", limit=limit, offset=(page-1)*limit)
    return Ul(*[Li(r.name) for r in results])

# Optional typed params
@rt('/items')
def get(idx: int | None = None):
    if idx is None: return show_all()
    return show_one(idx)
```

### Special Injected Parameters

FastHTML injects these by name — no import needed:

```python
@rt('/example')
def get(
    req,       # Starlette Request object (also accepts 'request')
    sess,      # Signed session dict (also accepts 'session')
    auth,      # Current user (set by Beforeware)
    htmx,      # HtmxHeaders dataclass
    app,       # The FastHTML app instance
):
    user_agent = req.headers.get('user-agent')
    sess['visits'] = sess.get('visits', 0) + 1
    if htmx.request:
        return P("Partial response")
    return Titled("Full page")
```

### Redirects

```python
from fasthtml.common import RedirectResponse

@rt('/old-path')
def get(): return RedirectResponse('/new-path', status_code=301)

# Or use Redirect shorthand
return Redirect('/')
```
