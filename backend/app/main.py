from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.runtime import engine

app = FastAPI(title=settings.app_name, debug=settings.debug)

# 允许前端 Vite 开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes_reports import router as reports_router  # noqa: E402
from app.api.routes_simulation import router as simulation_router  # noqa: E402
from app.api.routes_state import router as state_router  # noqa: E402
from app.api.routes_frontend import router as frontend_router  # noqa: E402
from app.api.routes_debug import router as debug_router  # noqa: E402

app.include_router(state_router)
app.include_router(simulation_router)
app.include_router(reports_router)
app.include_router(frontend_router)
app.include_router(debug_router)


@app.get("/")
def root() -> dict:
    return {
        "app": settings.app_name,
        "status": "ok",
        "day": engine.world.day,
        "slot": engine.world.current_slot,
    }