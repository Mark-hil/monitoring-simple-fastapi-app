from fastapi import FastAPI, Request, HTTPException
from starlette.responses import Response
from prometheus_client import REGISTRY, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import random
import asyncio

app = FastAPI()

# Prometheus metrics
REQUEST_COUNT = Counter(
    name="http_requests_total",
    documentation="Total number of HTTP requests",
    labelnames=["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    name="http_request_duration_seconds",
    documentation="Histogram of response time for requests",
    labelnames=["endpoint"]
)

# Simulated in-memory "database"
FAKE_TASKS = {1: "Monitor Prometheus", 2: "Create Grafana Dashboard"}
NEXT_TASK_ID = 3

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise e
    finally:
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, http_status=status_code).inc()
        REQUEST_LATENCY.labels(endpoint=request.url.path).observe(duration)
    return response

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Monitoring App"}

@app.get("/hello")
def hello():
    return {"message": "Hello, world!"}

@app.get("/error")
def error():
    raise HTTPException(status_code=500, detail="This is a simulated 500 error")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

# Realistic endpoints

@app.get("/tasks")
async def get_tasks():
    await asyncio.sleep(random.uniform(0.1, 0.5))  # simulate DB delay
    return {"tasks": FAKE_TASKS}

@app.post("/tasks")
async def create_task(task: str):
    global NEXT_TASK_ID
    await asyncio.sleep(random.uniform(0.2, 0.6))  # simulate write delay
    FAKE_TASKS[NEXT_TASK_ID] = task
    NEXT_TASK_ID += 1
    return {"message": "Task created", "id": NEXT_TASK_ID - 1}

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    await asyncio.sleep(random.uniform(0.1, 0.3))  # simulate lookup
    task = FAKE_TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "task": task}

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    await asyncio.sleep(random.uniform(0.3, 1.0))  # simulate slower delete
    if task_id in FAKE_TASKS:
        del FAKE_TASKS[task_id]
        return {"message": "Task deleted"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

@app.get("/users")
async def get_users():
    await asyncio.sleep(random.uniform(0.2, 0.5))  # simulate fetching users
    return {"users": ["alice", "bob", "charlie"]}

@app.post("/login")
async def login(username: str, password: str):
    await asyncio.sleep(random.uniform(0.3, 0.7))  # simulate auth delay
    if username == "admin" and password == "admin":
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
