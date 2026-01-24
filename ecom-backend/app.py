from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.exception_handlers import register_exception_handlers
from api.v1.router import api_v1_router

# Main app with no docs
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Create versioned API apps
api_v1 = FastAPI(
    title="E-commerce API - v1",
    description="Version 1 of the E-commerce API",
    version="v1"
)

# Register exception handlers for each versioned app
register_exception_handlers(api_v1)

# Configure CORS for each versioned app
api_v1.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include versioned routers
api_v1.include_router(api_v1_router)

# Mount versioned apps
app.mount("/api/v1", api_v1)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
