# FastHTML: Styling & UI

## Tailwind CSS + DaisyUI (Standard Setup)

PicoCSS is FastHTML's default but must **never** be used — always disable with `pico=False`.

```python
# Standard fast_app setup — always use this
app, rt = fast_app(
    pico=False,
    hdrs=(Link(rel='stylesheet', href='/static/output.css'),),
)
```

Install (Tailwind v4 + DaisyUI v5):
```bash
npm install -D tailwindcss@latest @tailwindcss/cli daisyui@latest
```

Build (uses `@tailwindcss/cli`, not `tailwindcss`):
```bash
npx @tailwindcss/cli -i ./static/input.css -o ./static/output.css --watch
```

No `tailwind.config.js` needed — all configuration is in CSS.

`static/input.css`:
```css
@import "tailwindcss";
@plugin "daisyui";
```

Content scanning is automatic in Tailwind v4.

### DaisyUI Component Patterns

Use `cls=` with DaisyUI class names:

```python
# Buttons
Button("Primary", cls="btn btn-primary")
Button("Outline", cls="btn btn-outline btn-sm")
Button("Secondary", cls="btn btn-secondary")

# Badge
Span("New", cls="badge badge-secondary")

# Card
Div(
    Div(
        H2("Card Title", cls="card-title"),
        P("Card body text."),
        cls="card-body"
    ),
    cls="card bg-base-200 shadow-xl"
)

# Hero
Div(
    Div(
        H1("Hero Title", cls="text-5xl font-bold"),
        P("Subtitle text.", cls="py-6"),
        Button("Get Started", cls="btn btn-primary"),
        cls="hero-content text-center"
    ),
    cls="hero min-h-screen"
)

# Navbar
Nav(
    Div(A("Brand", cls="btn btn-ghost text-xl"), cls="flex-1"),
    Div(Button("Login", cls="btn btn-outline btn-sm"), cls="flex-none"),
    cls="navbar bg-base-100"
)

# Alert
Div(Span("Info message"), cls="alert alert-info")
Div(Span("Error!"), cls="alert alert-error")

# Form controls
Div(
    Label("Email", cls="label"),
    Input(type="email", name="email", placeholder="you@example.com",
          cls="input input-bordered w-full"),
    cls="form-control"
)

# Modal — DaisyUI v5 uses <dialog> element
Dialog(
    Div(
        H3("Modal Title", cls="font-bold text-lg"),
        P("Modal content here."),
        cls="modal-box"
    ),
    cls="modal",
    id="my-modal"
)
# Open via JS: document.getElementById('my-modal').showModal()
Button("Open", onclick="document.getElementById('my-modal').showModal()", cls="btn")
```

### DaisyUI Custom Theme

In DaisyUI v5, themes are defined in CSS using `@plugin "daisyui/theme"` — not in `tailwind.config.js`:

`static/input.css`:
```css
@import "tailwindcss";
@plugin "daisyui";

@plugin "daisyui/theme" {
  name: "ABA";
  default: false;
  prefersdark: false;
  color-scheme: "dark";
  --color-base-100: #010413;
  --color-base-200: oklch(20% 0.042 265.755);
  --color-base-300: oklch(27% 0.041 260.031);
  --color-base-content: oklch(100% 0 0);
  --color-primary: #087CA7;
  --color-primary-content: #ffffff;
  --color-secondary: #B80C09;
  --color-secondary-content: oklch(100% 0 0);
  --color-accent: #8FC93A;
  --color-accent-content: oklch(0% 0 0);
}
```

Apply via `data-theme` on the `Html` element:
```python
Html(Head(...), Body(...), data_theme="ABA")
```

## Adding Custom CSS

```python
# Inline style tag
app, rt = fast_app(hdrs=(Style("""
    body { font-family: system-ui; }
    .hero { min-height: 100vh; }
"""),))

# External stylesheet
app, rt = fast_app(hdrs=(
    Link(rel='stylesheet', href='/static/app.css'),
))

# Multiple headers
app, rt = fast_app(hdrs=(
    Link(rel='stylesheet', href='/static/app.css'),
    Link(rel='preconnect', href='https://fonts.googleapis.com'),
    Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap'),
    Style("body { font-family: 'Inter', sans-serif; }")
))
```

## Static Files

FastHTML serves static files from the working directory by default.

```python
# Serve from current directory (default)
app, rt = fast_app(static_path='.')

# Reference in HTML
Link(rel='stylesheet', href='/static/app.css')
Img(src='/static/logo.png', alt='Logo')
Script(src='/static/app.js')
```

File structure:
```
my_app/
├── main.py
└── static/
    ├── app.css
    ├── app.js
    └── images/
        └── logo.png
```

## JavaScript

### Inline Scripts

```python
# Script tag in headers (runs once on load)
app, rt = fast_app(hdrs=(
    Script("""
        document.addEventListener('DOMContentLoaded', () => {
            console.log('Ready');
        });
    """),
))

# Script tag inline in page
Div(
    Button("Click me", id="btn"),
    Script("document.getElementById('btn').onclick = () => alert('Hi')")
)
```

### surreal.js (Included by Default)

FastHTML includes `surreal.js` — a tiny jQuery-like utility. Use with `me()` and `any()`:

```python
Script("""
    me('#btn').on('click', ev => {
        me('#result').innerHTML = 'Clicked!';
    });
""")
```

Disable surreal: `fast_app(surreal=False)`

### HTMX Events (JavaScript)

```python
# Listen for HTMX events
Script("""
    document.body.addEventListener('htmx:afterSwap', (evt) => {
        console.log('Swapped:', evt.detail.target);
    });
""")
```

### hx_on (Inline HTMX event handlers)

```python
# Modern syntax (double underscore = colon in event name)
Button("Submit",
       hx_post="/submit",
       hx_on__after_request="this.textContent = 'Done!'")
# → hx-on:htmx:after-request="..."

# NOT the deprecated: hx_on="htmx:afterRequest:..."
```

## Page Layout Patterns

### Full Page with Layout

```python
def Layout(title: str, *content):
    return Html(
        Head(
            Title(title),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
        ),
        Body(
            Nav(A("Home", href="/"), A("About", href="/about")),
            Main(*content, cls="container"),
            Footer(P("© 2025"))
        )
    )

@rt('/')
def get():
    return Layout("Home", H1("Welcome"), P("Hello world"))
```

### Using `Titled` (Quick Full Page)

```python
@rt('/')
def get():
    return Titled("My App",
        P("Content here"),
        # Titled wraps in a full HTML page with <title> + <h1>
    )
```

### HTMX Partial vs Full Page

```python
@rt('/')
def get(htmx: HtmxHeaders):
    content = Div(H1("Dashboard"), P("Content"), id="main")
    if htmx.request:
        return content   # partial: just the fragment
    return Layout("Dashboard", content)   # full: wrapped in layout
```
