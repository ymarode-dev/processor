from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PropertyRead(BaseModel):
    PROPERTY_ID: str
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
    entity_type: str
    PROPERTY_TYPE: str
    CML_IMAGE_PATH: str
    CML_LOCAL_IMG_PATH: str
    linkPrpKey: str
    PROJECT_ID: str
    orgTitle: str
    isRestored: int
    CML_CATEGORY: str
    CREATED_AT: datetime
    UPDATED_AT: datetime

    model_config = {"from_attributes": True}


class PropertyCreate(BaseModel):
    LKEY_VAL: str
    KEY_VAL: str
    CML_TYPE: int
    SYNC_PENDING_STATUS: int
    CML_TITLE: str
    KEY_TYPE: str
    SUB_KEY_TYPE: str
    ACTIVE_STATUS: int
    CML_RETROFIT: str
    LOCATION_ID: str
    entity_type: str
    PROPERTY_TYPE: str
    CML_IMAGE_PATH: str
    CML_LOCAL_IMG_PATH: str
    linkPrpKey: str
    PROJECT_ID: str
    orgTitle: str
    isRestored: int
    CML_CATEGORY: str

class PropertyUpdate(BaseModel):
    LKEY_VAL: Optional[str] = None
    KEY_VAL: Optional[str] = None
    CML_TYPE: Optional[int] = None
    SYNC_PENDING_STATUS: Optional[int] = None
    CML_TITLE: Optional[str] = None
    KEY_TYPE: Optional[str] = None
    SUB_KEY_TYPE: Optional[str] = None
    ACTIVE_STATUS: Optional[int] = None
    CML_RETROFIT: Optional[str] = None
    LOCATION_ID: Optional[str] = None
    PROPERTY_TYPE: Optional[str] = None
    CML_IMAGE_PATH: Optional[str] = None
    CML_LOCAL_IMG_PATH: Optional[str] = None
    linkPrpKey: Optional[str] = None
    PROJECT_ID: Optional[str] = None
    orgTitle: Optional[str] = None
    isRestored: Optional[int] = None
    CML_CATEGORY: Optional[str] = None

class PropertyFilter(BaseModel):
    PROPERTY_ID: Optional[str] = None
    TARGET: Optional[str] = None