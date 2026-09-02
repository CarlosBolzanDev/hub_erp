from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, dashboard, orders, users

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(orders.router)
app.include_router(users.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
