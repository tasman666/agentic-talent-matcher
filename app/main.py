from fastapi import FastAPI
from app.routes import router
from app.config import get_settings

app = FastAPI(title="Agentic Talent Matcher")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)