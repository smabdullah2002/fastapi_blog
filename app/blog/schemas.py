from enum import Enum
from pydantic import BaseModel, HttpUrl
from typing import Optional


class Category(str, Enum):
    technology = "technology"
    health = "health"
    lifestyle = "lifestyle"
    education = "education"
    entertainment = "entertainment"
    Artificial_Intelligence = "Artificial Intelligence"
    Machine_Learning = "Machine Learning"
    Data_Science = "Data Science"


class BlogSchema(BaseModel):
    title: str
    content: str
    category: Category
    img_url: Optional[HttpUrl] = None
