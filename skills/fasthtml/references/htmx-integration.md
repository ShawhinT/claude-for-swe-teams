# FastHTML: HTMX Integration

HTMX is the interactivity engine. The browser never fetches JSON — it sends requests and swaps in the HTML fragments the server returns.

## Core Pattern

```
User action → HTMX sends HTTP request → Server returns HTML fragment → HTMX swaps into DOM
```

## Essential `hx_*` Attributes

```python
# Trigger a GET on click (default trigger for most elements)
Button("Load", hx_get="/data", hx_target="#result")

# Trigger a POST on click
Button("Submit", hx_post="/submit", hx_target="#msg", hx_swap="innerHTML")

# Trigger on form submit
Form(Input(name="q"), Button("Search"),
     hx_post="/search", hx_target="#results")

# Trigger on input change (with debounce)
Input(name="q", hx_get="/search", hx_target="#results",
      hx_trigger="keyup changed delay:300ms")

# Delete with confirmation
Button("Delete", hx_delete=f"/todos/{todo.id}",
       hx_target=f"#todo-{todo.id}", hx_swap="outerHTML",
       hx_confirm="Are you sure?")
```

## Swap Strategies (`hx_swap`)

| Value | Effect |
|-------|--------|
| `innerHTML` (default) | Replace target's inner content |
| `outerHTML` | Replace the entire target element |
| `beforebegin` | Insert before target |
| `afterbegin` | Insert as first child |
| `beforeend` | Insert as last child |
| `afterend` | Insert after target |
| `delete` | Remove the target element |
| `none` | Do nothing with the response |

```python
# Common pattern: update a list by prepending a new item
Button("Add", hx_post="/todos", hx_target="#todo-list", hx_swap="afterbegin")

# Replace an item in-place
Button("Edit", hx_get=f"/todos/{id}/edit",
       hx_target=f"#todo-{id}", hx_swap="outerHTML")
```

## Targets

```python
# By ID (most common)
hx_target="#result"

# Closest ancestor matching selector
hx_target="closest li"
hx_target="closest .card"

# The element itself
hx_target="this"

# Find within response
hx_target="find .content"
```

## OOB (Out-of-Band) Swaps — Update Multiple Regions

Return a **tuple** from the handler. The first item is the main response; additional items with `hx_swap_oob="true"` update other parts of the page:

```python
@rt('/todos')
def post(title: str):
    new_todo = todos.insert(Todo(title=title, done=False))
    return (
        Li(new_todo.title, id=f"todo-{new_todo.id}"),        # swaps into hx_target
        Span(f"{len(todos())} total", id="count",              # updates #count anywhere on page
             hx_swap_oob="true"),
        Input(name="title", value="", id="new-todo-input",    # clears the input
              hx_swap_oob="true")
    )
```

The OOB elements **must have an `id`** matching an existing element on the page.

## Triggers

```python
# Default triggers: click (buttons/links), submit (forms), change (inputs)

# Custom triggers
hx_trigger="mouseenter"
hx_trigger="keyup changed delay:500ms"     # debounced keyup
hx_trigger="every 2s"                      # polling
hx_trigger="load"                          # on page load (lazy loading)
hx_trigger="intersect"                     # when element enters viewport
hx_trigger="click from:body"               # event on different element
hx_trigger="custom-event"                  # custom JS event
```

## Detecting HTMX Requests Server-Side

```python
@rt('/')
def get(htmx: HtmxHeaders):
    if htmx.request:
        # HTMX partial request — return just the fragment
        return P("Partial content")
    # Full page request — wrap in layout
    return Titled("Page", P("Full page content"))
```

## `hx_push_url` — Update Browser URL

```python
# Update the URL bar without a full page load
Button("Load page 2",
       hx_get="/page/2",
       hx_target="#content",
       hx_push_url="true")
```

## Loading Indicators

```python
# Show spinner while request is in flight
Div(
    Button("Submit", hx_post="/process"),
    Div(cls="htmx-indicator", id="spinner"),  # shown during request
)
```

## HTMX Extensions

Enable in `fast_app()`:

```python
app, rt = fast_app(exts='ws')            # WebSocket extension
app, rt = fast_app(exts='head-support')  # <head> management
app, rt = fast_app(exts='preload')       # Link preloading
```

## Common Interaction Patterns

### Inline Edit

```python
def TodoItem(todo):
    return Li(
        Span(todo.title, id=f"title-{todo.id}",
             hx_get=f"/todos/{todo.id}/edit",
             hx_target=f"#todo-{todo.id}",
             hx_swap="outerHTML"),
        id=f"todo-{todo.id}"
    )

@rt('/todos/{id}/edit')
def get(id: int):
    todo = todos[id]
    return Form(
        Input(name="title", value=todo.title),
        Button("Save", type="submit"),
        hx_put=f"/todos/{id}",
        hx_target=f"#todo-{id}",
        hx_swap="outerHTML"
    )
```

### Delete and Remove

```python
@rt('/todos/{id}')
def delete(id: int):
    todos.delete(id)
    return ""   # empty response + hx_swap="outerHTML" removes the element
```

### Infinite Scroll / Pagination

```python
def TodoList(todos_page, next_page):
    return Ul(
        *[Li(t.title) for t in todos_page],
        Li(
            Button("Load more",
                   hx_get=f"/todos?page={next_page}",
                   hx_target="closest ul",
                   hx_swap="beforeend"),
            id="load-more"
        )
    )
```
