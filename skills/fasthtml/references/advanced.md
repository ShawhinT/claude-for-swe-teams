# FastHTML: Advanced Patterns

## WebSockets

```python
from fasthtml.common import *

app, rt = fast_app(exts='ws')

@rt('/')
def get():
    return Titled("Chat",
        Div(id="messages"),
        Form(
            Input(name="msg", id="msg-input", autocomplete="off"),
            Button("Send"),
            ws_send=True,    # sends form data over WebSocket on submit
            hx_ext="ws",
            ws_connect="/ws"
        )
    )

@app.ws('/ws')
async def ws(msg: str, send):
    await send(Div(P(msg), hx_swap_oob="beforeend", id="messages"))
```

## Live Reload (Development)

```python
app, rt = fast_app(live=True)   # Hot reloads on file change
```

Only enable in development — never in production.

## Testing

Use Starlette's `TestClient`:

```python
from starlette.testclient import TestClient
from main import app

client = TestClient(app)

def test_homepage():
    r = client.get('/')
    assert r.status_code == 200
    assert 'Hello' in r.text

def test_create_todo():
    r = client.post('/todos', data={'title': 'Test todo'})
    assert r.status_code == 200
    assert 'Test todo' in r.text

def test_redirect():
    r = client.get('/old', allow_redirects=False)
    assert r.status_code == 301
    assert r.headers['location'] == '/new'
```

## Starlette Middleware

```python
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

app, rt = fast_app(
    middleware=[
        Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*']),
        Middleware(GZipMiddleware, minimum_size=1000),
    ]
)
```

## Custom Error Pages

```python
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse
from fastcore.xml import to_xml

@app.exception_handler(404)
async def not_found(req, exc):
    page = Titled("404 — Not Found", P("The page you're looking for doesn't exist."),
                   A("Go home", href="/"))
    return HTMLResponse(to_xml(page), status_code=404)

@app.exception_handler(500)
async def server_error(req, exc):
    page = Titled("500 — Server Error", P("Something went wrong."))
    return HTMLResponse(to_xml(page), status_code=500)
```

## Returning Raw Responses

```python
from starlette.responses import JSONResponse, FileResponse, StreamingResponse

@rt('/api/data')
def get():
    return JSONResponse({'key': 'value'})   # JSON (rare in FastHTML)

@rt('/download')
def get():
    return FileResponse('data/report.pdf', filename='report.pdf')

@rt('/stream')
async def get():
    async def generate():
        for i in range(10):
            yield f"data: {i}\n\n"
    return StreamingResponse(generate(), media_type='text/event-stream')
```

## Multi-File Apps (APIRouter Pattern)

```python
# routes/todos.py
from fasthtml.common import *

router = APIRouter(prefix='/todos')

@router.get('/')
def list_todos(): ...

@router.post('/')
def create_todo(title: str): ...

# main.py
from fasthtml.common import *
from routes.todos import router

app, rt = fast_app()
app.include_router(router)
serve()
```

## Background Tasks

```python
from starlette.background import BackgroundTask

def send_email(email: str):
    # runs after response is sent
    ...

@rt('/register')
def post(email: str):
    task = BackgroundTask(send_email, email=email)
    return Response("Registered!", background=task)
```

## Deployment

### Railway / Render / Fly.io

```python
# main.py
serve(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
```

`Procfile`:
```
web: python main.py
```

### Modal (Serverless)

```python
import modal
from fasthtml.common import *

app, rt = fast_app()

@rt('/')
def get(): return P("Hello from Modal")

modal_app = modal.App("my-fasthtml-app")

@modal_app.function(image=modal.Image.debian_slim().pip_install("python-fasthtml"))
@modal.asgi_app()
def fastapi_app():
    return app
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["python", "main.py"]
```

`requirements.txt`:
```
python-fasthtml
```

### Environment Variables Pattern

```python
import os
from fasthtml.common import *

app, rt = fast_app(
    secret_key=os.environ['SESSION_SECRET'],
    db_file=os.environ.get('DATABASE_URL', 'data/app.db'),
)

serve(
    host='0.0.0.0',
    port=int(os.environ.get('PORT', 5001)),
    reload=os.environ.get('ENV') == 'development'
)
```

## Server-Sent Events (SSE)

```python
import asyncio
from starlette.responses import StreamingResponse

@rt('/events')
async def get():
    async def event_generator():
        for i in range(10):
            yield f"data: Update {i}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type='text/event-stream')

# Client-side
Div(
    hx_ext="sse",
    sse_connect="/events",
    sse_swap="message",
    hx_target="#log",
    hx_swap="beforeend",
    id="log"
)
```
