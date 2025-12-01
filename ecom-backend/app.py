from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from domains.carts.api.router import router as carts_router
from api.exception_handlers import register_exception_handlers

app = FastAPI(
    title="E-commerce API",
    description="API for the E-commerce",
    version="0.1.0"
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
app.include_router(carts_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the E-commerce API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
