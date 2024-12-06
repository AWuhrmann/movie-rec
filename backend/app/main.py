import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import recommendations
from app.services.recommendation_engine import init_data
import resource
import os

# Set resource limit
resource.setrlimit(resource.RLIMIT_AS, (2**32, 2**32))  # 1GB limit

app = FastAPI()

# In production with Apache, you might not need CORS at all
# but if you want to keep it for development:
if os.getenv("ENVIRONMENT") == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(recommendations.router, prefix="/api")

# Initialize data
def init_data(app: FastAPI):
    # Your initialization code here
    pass

if __name__ == "__main__":
    init_data(app)
    uvicorn.run(app, host="0.0.0.0", port=8000)
