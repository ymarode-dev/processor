from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from CE.property.models import Property
    from CE.room.models import Room

class Floor(SQLModel, table=True):
    __tablename__ = "floor"

    FLOOR_ID: str = Field(
        default_factory=lambda: f"ID{uuid.uuid4()}",
        primary_key=True,
    )

    LKEY_VAL: str
    TARGET: str = Field(index=True)
    PROPERTY_ID: str = Field(foreign_key="property.PROPERTY_ID", index=True)
    GROUP_ID: str
    CML_TYPE: str
    CML_SUB_TYPE: str
    CML_TITLE: str
    KEY_VAL: str
    SYNC_PENDING_STATUS: int
    KEY_TYPE: str
    SUB_KEY_TYPE: str
    ACTIVE_STATUS: int
    entity_type: str = Field(default="floor")
    PROJECT_ID: str
    CREDENTIAL_ID: str
    INTERFACE_ID: str
    INDEX_NO: str
    CUSTOM_USER_NAME: str

    CREATED_AT: datetime = Field(default_factory=datetime.utcnow)
    UPDATED_AT: datetime = Field(default_factory=datetime.utcnow)

    property: Optional["Property"] = Relationship(back_populates="floors")
    rooms: List["Room"] = Relationship(back_populates="floor")

    def __repr__(self):
        return f"<Floor(title={self.CML_TITLE})>"