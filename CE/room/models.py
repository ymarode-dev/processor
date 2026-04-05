from sqlmodel import Relationship, SQLModel, Field
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from CE.device.models import Devices
    from CE.floor.models import Floor

class Room(SQLModel, table=True):
    __tablename__ = "room"

    ROOM_ID: str = Field(
        default_factory=lambda: f"ID{uuid.uuid4()}",
        primary_key=True,
    )

    LKEY_VAL: str
    TARGET: str = Field(index=True)
    FLOOR_ID: str = Field(foreign_key="floor.FLOOR_ID", index=True)
    GROUP_ID: str
    CML_TYPE: str
    CML_SUB_TYPE: str
    CML_TITLE: str
    KEY_VAL: str
    SYNC_PENDING_STATUS: int
    KEY_TYPE: str
    SUB_KEY_TYPE: str
    ACTIVE_STATUS: int
    entity_type: str = Field(default="room")
    PROJECT_ID: str
    CREDENTIAL_ID: str
    INTERFACE_ID: str
    INDEX_NO: str
    CUSTOM_USER_NAME: str

    CREATED_AT: datetime = Field(default_factory=datetime.utcnow)
    UPDATED_AT: datetime = Field(default_factory=datetime.utcnow)

    floor: Optional["Floor"] = Relationship(back_populates="rooms")
    devices: List["Devices"] = Relationship(back_populates="room")

    def __repr__(self):
        return f"<Room(title={self.CML_TITLE})>"