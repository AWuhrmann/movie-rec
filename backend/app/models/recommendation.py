from enum import Enum
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class Rating(BaseModel):
    imdb_id: str
    rating: float

class MovieRecommendation(BaseModel):
    id: str
    title: str
    year: Optional[int] = None
    # Add other movie fields as needed

class JobStatus(BaseModel):
    status: str
    results: Optional[List[MovieRecommendation]] = None
    error: Optional[str] = None

class AlgorithmType(Enum):
    KNN_USER = "knn_user"
    KNN_ITEM = "knn_item"
    CONTENT_BASED = "content_based"
    SVD="svd"

class RecommendationRequest(BaseModel):
    ratings: List[Rating]
    algorithm: AlgorithmType = AlgorithmType.CONTENT_BASED  # Default algorithm
    params: Optional[Dict[str, Any]] = None  # Flexible dictionary for any parameters

class MovieRequest(BaseModel):
    movies: List[str] # List of movie imdb_ids.