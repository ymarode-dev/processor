from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FloorRead(BaseModel):
    FLOOR_ID: str
    LKEY_VAL: str
    TARGET: str
    PROPERTY_ID: str
    GROUP_ID: str
    CML_TYPE: str
    CML_SUB_TYPE: str
    CML_TITLE: str
    KEY_VAL: str
    SYNC_PENDING_STATUS: int
    KEY_TYPE: str
    SUB_KEY_TYPE: str
    ACTIVE_STATUS: int
    entity_type: str
    PROJECT_ID: str
    CREDENTIAL_ID: str
    INTERFACE_ID: str
    INDEX_NO: str
    CUSTOM_USER_NAME: str
    CREATED_AT: datetime
    UPDATED_AT: datetime

    model_config = {"from_attributes": True}


class FloorCreate(BaseModel):
    LKEY_VAL: str
    TARGET: str
    PROPERTY_ID: str
    GROUP_ID: str
    CML_TYPE: str
    CML_SUB_TYPE: str
    CML_TITLE: str
    KEY_VAL: str
    SYNC_PENDING_STATUS: int
    KEY_TYPE: str
    SUB_KEY_TYPE: str
    ACTIVE_STATUS: int
    entity_type: str
    PROJECT_ID: str
    CREDENTIAL_ID: str
    INTERFACE_ID: str
    INDEX_NO: str
    CUSTOM_USER_NAME: str


class FloorUpdate(BaseModel):
    LKEY_VAL: Optional[str] = None
    TARGET: Optional[str] = None
    PROPERTY_ID: Optional[str] = None
    GROUP_ID: Optional[str] = None
    CML_TYPE: Optional[str] = None
    CML_SUB_TYPE: Optional[str] = None
    CML_TITLE: Optional[str] = None
    KEY_VAL: Optional[str] = None
    SYNC_PENDING_STATUS: Optional[int] = None
    KEY_TYPE: Optional[str] = None
    SUB_KEY_TYPE: Optional[str] = None
    ACTIVE_STATUS: Optional[int] = None
    entity_type: Optional[str] = None
    PROJECT_ID: Optional[str] = None
    CREDENTIAL_ID: Optional[str] = None
    INTERFACE_ID: Optional[str] = None
    INDEX_NO: Optional[str] = None
    CUSTOM_USER_NAME: Optional[str] = None


class FloorFilter(BaseModel):
    FLOOR_ID: Optional[str] = None
    PROPERTY_ID: Optional[str] = None
    TARGET: Optional[str] = None