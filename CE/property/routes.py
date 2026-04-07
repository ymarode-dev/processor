from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from .schemas import PropertyRead, PropertyCreate, PropertyUpdate
from connections.sqlite import get_core_session
from .service import PropertyService   

property_router = APIRouter()
property_service = PropertyService()

@property_router.get("/", response_model=PropertyRead, status_code=status.HTTP_200_OK)
async def get_property(session: AsyncSession = Depends(get_core_session)) -> PropertyRead:
    property = await property_service.get_property(session)

    if not property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    return property

@property_router.post("/", response_model=PropertyRead, status_code=status.HTTP_201_CREATED)
async def create_property(property_data: PropertyCreate, session: AsyncSession = Depends(get_core_session)) -> PropertyRead:
    new_property = await property_service.create_property(session, property_data)
    return new_property

@property_router.patch("/", response_model=PropertyRead, status_code=status.HTTP_200_OK)
async def update_property(property_data: PropertyUpdate, session: AsyncSession = Depends(get_core_session)) -> PropertyRead:
    updated_property = await property_service.update_property(session, property_data)
    if not updated_property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return updated_property   

@property_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(session: AsyncSession = Depends(get_core_session)) -> None:
    success = await property_service.delete_property(session)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    