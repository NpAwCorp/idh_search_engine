from pydantic import BaseModel

class SearchRequest(BaseModel):
    company: str
    country: str
    website: str