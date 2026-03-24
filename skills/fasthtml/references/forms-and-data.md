# FastHTML: Forms & Data

## Form Handling

### Basic Form

```python
# Form fields map to route handler parameters by `name` attribute
Form(
    Label("Title", _for="title"),
    Input(id="title", name="title", type="text", placeholder="Enter title"),
    Button("Submit", type="submit"),
    hx_post="/todos",
    hx_target="#todo-list",
    hx_swap="beforeend"
)

@rt('/todos')
def post(title: str):         # `title` matches Input(name="title")
    todo = todos.insert(Todo(title=title, done=False))
    return Li(todo.title, id=f"todo-{todo.id}")
```

### `fill_form` — Populate Form Fields

`fill_form` populates a form from a dataclass or dict by matching **`name` attributes** (not `id`):

```python
from fasthtml.common import fill_form

def EditForm(todo):
    form = Form(
        Input(name="title"),       # name must match dataclass field
        Input(name="done", type="hidden"),
        Button("Save", type="submit"),
        hx_put=f"/todos/{todo.id}"
    )
    return fill_form(form, todo)   # populates Input(name="title") with todo.title
```

### Form with Dataclass

```python
@dataclass
class TodoForm:
    title: str
    priority: int = 1
    done: bool = False

@rt('/todos')
def post(todo: TodoForm):          # FastHTML deserializes form fields into the dataclass
    new = todos.insert(todo)
    return Li(new.title)
```

### Multi-Value Fields (Checkboxes, Multi-Select)

```python
@rt('/tags')
def post(req):
    tags = req.query_params.getlist('tag')  # ['python', 'web']
    return P(f"Tags: {', '.join(tags)}")
```

---

## Database: MiniDataAPI / fastlite

`fast_app()` sets up SQLite via `fastlite`, exposing a table object and dataclass.

### Setup

```python
# Single table
app, rt, todos, Todo = fast_app('data/app.db', id=int, title=str, done=bool, pk='id')

# Multiple tables
app, rt, (users, User), (todos, Todo) = fast_app(
    'data/app.db',
    tbls=dict(
        users=dict(id=int, name=str, email=str, pwd=str, pk='id'),
        todos=dict(id=int, title=str, done=bool, user_id=int, pk='id')
    )
)
```

`todos` = table object (CRUD methods)
`Todo` = dataclass (with `__ft__` via `@patch` or direct definition)

### CRUD Operations

```python
# CREATE
todo = todos.insert(Todo(title="Buy milk", done=False))
todo = todos.insert(title="Buy milk", done=False)  # kwargs also work

# READ all
all_todos = todos()                           # list of Todo instances
all_todos = todos(order_by='title')
active    = todos(where="done=0")
active    = todos(where="done=0 AND user_id=?", where_args=[user_id])

# READ one
todo = todos[1]                               # by primary key; raises NotFoundError if missing
todo = todos.get(1)                           # returns None if missing

# UPDATE
todo.title = "Buy oat milk"
todos.update(todo)                            # returns updated Todo
# Or update by fields
todos.update(Todo(id=1, title="Buy oat milk", done=False))

# DELETE
todos.delete(1)                               # by primary key
todos.delete_where("done=1")                  # bulk delete

# UPSERT
todos.upsert(Todo(id=1, title="Updated", done=True))

# COUNT
n = todos.count
n = todos.count(where="done=0")
```

### Raw SQL

```python
from fastlite import database

db = database('data/app.db')
results = db.q("SELECT * FROM todos WHERE done=? ORDER BY id DESC", [0])
```

### Dataclass + `__ft__` Pattern

```python
app, rt, todos, Todo = fast_app('data/app.db', id=int, title=str, done=bool, pk='id')

@patch
def __ft__(self: Todo):
    checkbox = Input(
        type="checkbox", checked=self.done,
        hx_post=f"/todos/{self.id}/toggle",
        hx_target=f"#todo-{self.id}",
        hx_swap="outerHTML"
    )
    delete_btn = Button(
        "×",
        hx_delete=f"/todos/{self.id}",
        hx_target=f"#todo-{self.id}",
        hx_swap="outerHTML"
    )
    return Li(checkbox, self.title, delete_btn, id=f"todo-{self.id}")

@rt('/')
def get():
    return Titled("Todos",
        Ul(*todos(), id="todo-list"),
        Form(Input(name="title"), Button("Add"),
             hx_post="/todos", hx_target="#todo-list", hx_swap="beforeend")
    )

@rt('/todos')
def post(title: str):
    return todos.insert(Todo(title=title, done=False)).__ft__()

@rt('/todos/{id}/toggle')
def post(id: int):
    todo = todos[id]
    todo.done = not todo.done
    return todos.update(todo).__ft__()

@rt('/todos/{id}')
def delete(id: int):
    todos.delete(id)
    return ""
```

### Error Handling

```python
from fastlite import NotFoundError

@rt('/todos/{id}')
def get(id: int):
    try:
        return todos[id].__ft__()
    except NotFoundError:
        return P("Not found", cls="error"), 404
```
