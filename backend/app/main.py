import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.demo_auth import add_demo_auth

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_DIR = BACKEND_DIR.parent


def get_frontend_dist_dir() -> Path | None:
    configured_path = os.getenv("FRONTEND_DIST_DIR")
    candidates = [
        Path(configured_path) if configured_path else None,
        BACKEND_DIR / "frontend_dist",
        REPOSITORY_DIR / "frontend" / "dist",
    ]

    for candidate in candidates:
        if candidate and (candidate / "index.html").exists():
            return candidate

    return None


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["GET", "PATCH", "POST"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    add_demo_auth(app)
    app.include_router(api_router)

    frontend_dist_dir = get_frontend_dist_dir()
    if frontend_dist_dir:
        assets_dir = frontend_dist_dir / "assets"
        if assets_dir.exists():
            app.mount(
                "/assets",
                StaticFiles(directory=assets_dir),
                name="frontend-assets",
            )

        index_file = frontend_dist_dir / "index.html"

        @app.get("/", include_in_schema=False)
        async def serve_frontend_root() -> FileResponse:
            return FileResponse(index_file)

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_frontend_route(full_path: str) -> FileResponse:
            if full_path.startswith(settings.API_V1_PREFIX.lstrip("/")):
                raise HTTPException(status_code=404, detail="API endpoint not found")

            requested_file = (frontend_dist_dir / full_path).resolve()
            if (
                requested_file.is_file()
                and frontend_dist_dir.resolve() in requested_file.parents
            ):
                return FileResponse(requested_file)

            return FileResponse(index_file)

    return app


app = create_app()
