from fastapi import FastAPI

app = FastAPI(
    title="University Super App",
    description="University Management and Smart Campus Platform",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to University Super App",

        "status": "running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy"
    }