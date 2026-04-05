from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class Location(SQLModel, table=True):
    __tablename__ = "location"

    LOCATION_ID: str = Field(
        default_factory=lambda: f"ID{uuid.uuid4()}",
        primary_key=True,
    )

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
    entity_type: str = Field(default="location")

    CREATED_AT: datetime = Field(default_factory=datetime.utcnow)
    UPDATED_AT: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"<Location(title={self.CML_LOCATION})>"