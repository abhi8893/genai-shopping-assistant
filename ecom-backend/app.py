from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.exception_handlers import register_exception_handlers
from api.v1.router import api_v1_router

app = FastAPI(
    title="E-commerce API",
    description="API for the E-commerce"
)

register_exception_handlers(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
