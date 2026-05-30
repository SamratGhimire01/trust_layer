import os
from dotenv import load_dotenv  # <--- Added
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import router

# SECURITY: Load the .env file into the system environment immediately on boot
load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI(
        title="TrustLayer Engine - Secured",
        description="Rule-Based Credit Scoring & Network Graph Analytics Backend",
        version="1.0.0",
        docs_url="/docs" if os.getenv("ENV") != "production" else None,
        redoc_url=None
    )
    
    # allowed_origins = [
    #     "http://localhost:3000",
    #     "http://localhost:5173",
    #     "http://127.0.0.1:5173"
    # ]
    allowed_origins = [
        "*"
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=False,  # <--- CHANGED TO FALSE
        allow_methods=["*"],      # <--- CHANGED TO "*" (allows everything)
        allow_headers=["*"],      # <--- CHANGED TO "*" (allows everything)
    )
    
    @app.exception_handler(Exception)
    async def global_execution_exception_handler(request: Request, exc: Exception):
        import logging
        logging.error(f"Internal System Fault on {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred while processing the operational request."
            }
        )

    app.include_router(router)
    
    @app.get("/health")
    async def health_check():
        return {"status": "operational"}
        
    return app

app = create_app()