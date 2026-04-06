from pydantic import BaseModel, Field
from typing import List

class TestScenario(BaseModel):
    titulo: str = Field(..., description="Título objetivo del escenario")
    precondiciones: List[str] = Field(..., description="Lista de precondiciones")
    steps: List[str] = Field(..., description="Pasos en formato Gherkin")
    tags: List[str] = Field(default_factory=list, description="Tags del escenario (ej: smoke, regression, critical)")

class TestCaseResponse(BaseModel):
    feature: str = Field(..., description="Nombre de la Feature")
    escenarios: List[TestScenario] = Field(..., min_length=1)