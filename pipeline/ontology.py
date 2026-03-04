from pydantic import BaseModel, Field
from typing import List, Optional

class Entity(BaseModel):
    id: str = Field(..., description="A unique, normalized identifier for the entity (e.g., 'john d', 'memory_system' or 'issue_34')")
    type: str = Field(..., description="The type of the entity: 'Person', 'Topic', 'Artifact', or 'Decision'")
    display_name: str = Field(..., description="Human-readable name")

class Evidence(BaseModel):
    source_url: str = Field(..., description="The URL or exact identifier from the GitHub issue/comment")
    quote: str = Field(..., description="The exact text quote that supports this claim")

class Claim(BaseModel):
    source_entity_id: str = Field(..., description="The ID of the source entity")
    target_entity_id: str = Field(..., description="The ID of the target entity")
    relationship: str = Field(..., description="E.g., 'Discussed', 'Proposed', 'Disagreed_With', 'Owned_By', 'Relies_On', 'Mentioned'")
    evidence: Evidence

class GraphExtraction(BaseModel):
    entities: List[Entity] = Field(default_factory=list, description="All meaningful entities identified in the chunk")
    claims: List[Claim] = Field(default_factory=list, description="All relationships or facts connecting the entities")
