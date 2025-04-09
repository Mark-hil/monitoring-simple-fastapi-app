from fastapi import FastAPI, Request
from starlette.responses import Response
from prometheus_client import REGISTRY, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

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

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    endpoint = request.url.path
    method = request.method
    status_code = response.status_code

    REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)

    return response

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Monitoring App"}

@app.get("/hello")
def hello():
    return {"message": "Hello, world!"}

@app.get("/error")
def error():
    raise Exception("This is a test error")

@app.get("/tasks")
def tasks():
    return {"tasks": ["monitor", "debug", "scale"]}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
# uvicorn main:app --host 0.0.0.0 --port 8000
