from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List
import uuid
from floor.models import Floor

class Property(SQLModel, table=True):
    __tablename__ = "property"

    PROPERTY_ID: str = Field(
        default_factory=lambda: f"ID{uuid.uuid4()}",
        primary_key=True,
    )

    LKEY_VAL: str
    KEY_VAL: str
    CML_TYPE: int
    TARGET: str
    SYNC_PENDING_STATUS: int
    CML_TITLE: str
    KEY_TYPE: str
    SUB_KEY_TYPE: str
    ACTIVE_STATUS: int
    CML_RETROFIT: str
    LOCATION_ID: str
    entity_type: str = Field(default="property")
    PROPERTY_TYPE: str
    CML_IMAGE_PATH: str
    CML_LOCAL_IMG_PATH: str
    linkPrpKey: str
    PROJECT_ID: str
    orgTitle: str
    isRestored: int
    CML_CATEGORY: str

    CREATED_AT: datetime = Field(default_factory=datetime.utcnow)
    UPDATED_AT: datetime = Field(default_factory=datetime.utcnow)

    floors: List["Floor"] = Relationship(back_populates="property")

    def __repr__(self):
        return f"<Property(title={self.CML_TITLE})>"