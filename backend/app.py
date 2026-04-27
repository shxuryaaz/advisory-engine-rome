from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.decision import router as decision_router
from routes.feedback import router as feedback_router
from routes.memory import router as memory_router
from routes.profile import router as profile_router
from routes.dashboard import router as dashboard_router
from config import settings
from services.logging import configure_logging


configure_logging()

app = FastAPI(
    title="Personal Decision Intelligence System",
    version="0.1.0",
    description="Stateful multi-agent decision intelligence API with structured and semantic memory.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(decision_router)
app.include_router(feedback_router)
app.include_router(memory_router)
app.include_router(profile_router)
app.include_router(dashboard_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
