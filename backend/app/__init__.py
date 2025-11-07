from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import note, provider, model, config, auth, subscription
from .core.config import settings


def create_app(lifespan) -> FastAPI:
    app = FastAPI(
        title="BiliNote SaaS",
        version="2.0.0",
        description="AI-powered video notes generation platform",
        lifespan=lifespan
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    # Authentication & Subscription (new SaaS features)
    app.include_router(auth.router)  # /api/auth/*
    app.include_router(subscription.router)  # /api/subscription/*

    # Legacy routers (existing functionality)
    app.include_router(note.router, prefix="/api")
    app.include_router(provider.router, prefix="/api")
    app.include_router(model.router, prefix="/api")
    app.include_router(config.router, prefix="/api")

    return app
