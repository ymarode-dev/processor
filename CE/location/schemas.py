from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LocationRead(BaseModel):
    LOCATION_ID: str 
    LKEY_VAL: str
    ADDRESS_LINE1: str
    ADDRESS_LINE2: str
    CML_ZIPCODE: int
    CML_CONTINENT: str
    CML_LOCATION: str
    CML_COUNTRY: str
    CML_CITY: int
    CML_TIMEZONE: str
    CML_STATE: str
    CML_COUNTRY_CODE: int
    CML_LATITUDE: str
    CML_LONGITUDE: str
    entity_type: str
    CREATED_AT: datetime
    UPDATED_AT: datetime

class LocationCreate(BaseModel):
    LKEY_VAL: str
    ADDRESS_LINE1: str
    ADDRESS_LINE2: str
    CML_ZIPCODE: int
    CML_CONTINENT: str
    CML_LOCATION: str
    CML_CITY: int
    CML_TIMEZONE: str
    CML_STATE: str
    CML_COUNTRY: str
    CML_COUNTRY_CODE: int
    CML_LATITUDE: str
    CML_LONGITUDE: str
    entity_type: str

class LocationUpdate(BaseModel):
    LKEY_VAL: Optional[str] = None
    ADDRESS_LINE1: Optional[str] = None
    ADDRESS_LINE2: Optional[str] = None
    CML_ZIPCODE: Optional[int] = None
    CML_CONTINENT: Optional[str] = None
    CML_LOCATION: Optional[str] = None
    CML_CITY: Optional[int] = None
    CML_TIMEZONE: Optional[str] = None
    CML_STATE: Optional[str] = None
    CML_COUNTRY: Optional[str] = None
    CML_COUNTRY_CODE: Optional[int] = None
    CML_LATITUDE: Optional[str] = None
    CML_LONGITUDE: Optional[str] = None