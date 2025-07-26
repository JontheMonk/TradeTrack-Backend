from pydantic import BaseModel, Field
from typing import List

class QueryEmbedding(BaseModel):
    embedding: List[float] = Field(..., min_items=512, max_items=512)