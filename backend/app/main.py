import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import recommendations
from app.services.recommendation_engine import init_data, init_data
import os

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ada.wuhrmann.art", "http://localhost:5173", "http://127.0.0.1:5173"],  # Your Svelte site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommendations.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


init_data(app)
