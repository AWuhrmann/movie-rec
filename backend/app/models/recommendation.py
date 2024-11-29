from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class Rating(BaseModel):
    imdb_id: str
    rating: float

class MovieRecommendation(BaseModel):
    id: str
    title: str
    # Add other movie fields as needed

class JobStatus(BaseModel):
    status: str
    results: Optional[List[MovieRecommendation]] = None
    error: Optional[str] = None

class AlgorithmType(Enum):
    COLLABORATIVE = "collaborative"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"

class RecommendationRequest(BaseModel):
    ratings: List[Rating]
    algorithm: AlgorithmType = AlgorithmType.COLLABORATIVE  # Default algorithm
