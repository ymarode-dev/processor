from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceRead(BaseModel):
    DEVICE_ID: str
    LKEY_VAL: str
    ROOM_ID: str
    TARGET: str
    CML_TYPE: str
    CML_SUB_TYPE: str
    CML_TITLE: str
    KEY_VAL: str
    CML_WIRED: bool
    SYNC_PENDING_STATUS: int
    CML_MANUFACTURER_NAME: str
    CML_SERIAL_ID: str
    CML_NAME: str
    CML_INSTALLATION_DATE: str
    CML_EXPIRY_DATE: str
    CML_SUPPORTED_TYPE: str
    CML_DEVICE_FIRMWARE: str
    MODEL_NUMBER: str
    OWNER_ID: str
    concept: str
    CML_DEVICE_REF: str
    CREDENTIAL_ID: str
    INTERFACE_ID: str
    entity_type: str
    PRODUCT_ID: str
    WATT: int
    CML_CATEGORY: str
    CML_COMFORT: str
    ACTIONS_PROPERTIES: str
    CREATED_AT: datetime 
    UPDATED_AT: datetime 

    model_config = {"from_attributes": True}


class DeviceCreate(BaseModel):
    LKEY_VAL: str
    ROOM_ID: str
    TARGET: str
    CML_TYPE: str
    CML_SUB_TYPE: str
    CML_TITLE: str
    KEY_VAL: str
    CML_WIRED: bool
    SYNC_PENDING_STATUS: int
    CML_MANUFACTURER_NAME: str
    CML_SERIAL_ID: str
    CML_NAME: str
    CML_INSTALLATION_DATE: str
    CML_EXPIRY_DATE: str
    CML_SUPPORTED_TYPE: str
    CML_DEVICE_FIRMWARE: str
    MODEL_NUMBER: str
    OWNER_ID: str
    concept: str
    CML_DEVICE_REF: str
    CREDENTIAL_ID: str
    INTERFACE_ID: str
    entity_type: str
    PRODUCT_ID: str
    WATT: int
    CML_CATEGORY: str
    CML_COMFORT: str
    ACTIONS_PROPERTIES: str


class DeviceUpdate(BaseModel):
    LKEY_VAL: Optional[str] = None
    ROOM_ID: Optional[str] = None
    TARGET: Optional[str] = None
    CML_TYPE: Optional[str] = None
    CML_SUB_TYPE: Optional[str] = None
    CML_TITLE: Optional[str] = None
    KEY_VAL: Optional[str] = None
    CML_WIRED: Optional[bool] = None
    SYNC_PENDING_STATUS: Optional[int] = None
    CML_MANUFACTURER_NAME: Optional[str] = None
    CML_SERIAL_ID: Optional[str] = None
    CML_NAME: Optional[str] = None
    CML_INSTALLATION_DATE: Optional[str] = None
    CML_EXPIRY_DATE: Optional[str] = None
    CML_SUPPORTED_TYPE: Optional[str] = None
    CML_DEVICE_FIRMWARE: Optional[str] = None
    MODEL_NUMBER: Optional[str] = None
    OWNER_ID: Optional[str] = None
    concept: Optional[str] = None
    CML_DEVICE_REF: Optional[str] = None
    CREDENTIAL_ID: Optional[str] = None
    INTERFACE_ID: Optional[str] = None
    entity_type: Optional[str] = None
    PRODUCT_ID: Optional[str] = None
    WATT: Optional[int] = None
    CML_CATEGORY: Optional[str] = None
    CML_COMFORT: Optional[str] = None
    ACTIONS_PROPERTIES: Optional[str] = None

class DeviceFilter(BaseModel):
    DEVICE_ID: Optional[str] = None
    TARGET: Optional[str] = None
    ROOM_ID: Optional[str] = None
    CML_SERIAL_ID: Optional[str] = None
    OWNER_ID: Optional[str] = None