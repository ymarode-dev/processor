from sqlmodel import Relationship, SQLModel, Field
from datetime import datetime
from typing import Dict, Optional, Any
from sqlalchemy import Column, JSON
import uuid
from room.models import Room

class Devices(SQLModel, table=True):
    __tablename__ = "devices"

    DEVICE_ID: str = Field(
        default_factory=lambda: f"ID{uuid.uuid4()}",
        primary_key=True,
    )

    LKEY_VAL: str
    ROOM_ID: str = Field(foreign_key="room.ROOM_ID", index=True)
    TARGET: str = Field(index=True)
    CML_TYPE: str
    CML_SUB_TYPE: str
    CML_TITLE: str
    KEY_VAL: str
    CML_WIRED: bool
    SYNC_PENDING_STATUS: int
    CML_MANUFACTURER_NAME: str
    CML_SERIAL_ID: str = Field(index=True)
    CML_NAME: str
    CML_INSTALLATION_DATE: str
    CML_EXPIRY_DATE: str
    CML_SUPPORTED_TYPE: str
    CML_DEVICE_FIRMWARE: str
    MODEL_NUMBER: str
    OWNER_ID: str = Field(index=True)
    concept: str
    CML_DEVICE_REF: str
    CREDENTIAL_ID: str
    INTERFACE_ID: str
    entity_type: str = Field(default="device")
    PRODUCT_ID: str
    WATT: int
    CML_CATEGORY: str
    CML_COMFORT: str
    ACTIONS_PROPERTIES: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )
    CREATED_AT: datetime = Field(default_factory=datetime.utcnow)
    UPDATED_AT: datetime = Field(default_factory=datetime.utcnow)

    room: Optional[Room] = Relationship(back_populates="devices")

    def __repr__(self):
        return f"<Device(title={self.CML_TITLE})>"