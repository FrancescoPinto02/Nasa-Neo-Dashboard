from fastapi import FastAPI

app = FastAPI(
    title="NASA NEO Dashboard API",
    description="Backend API for NASA Near Earth Objects dashboard.",
    version="0.1.0",
)


@app.get("/api/v1/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}