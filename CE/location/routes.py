from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from CE.connections.sqlite import get_core_session
from .service import LocationService
from .schemas import LocationCreate, LocationRead, LocationUpdate


location_router = APIRouter()
location_service = LocationService()

@location_router.get("/", response_model=LocationRead, status_code=status.HTTP_200_OK)
async def get_location(session: AsyncSession = Depends(get_core_session)) -> LocationRead:
    location = await location_service.get_location(session)

    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    return location

@location_router.post("/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(location_data: LocationCreate, session: AsyncSession = Depends(get_core_session)) -> LocationRead:
    new_location = await location_service.create_location(session, location_data)
    return new_location

@location_router.patch("/", response_model=LocationRead, status_code=status.HTTP_200_OK)
async def update_location(location_data: LocationUpdate, session: AsyncSession = Depends(get_core_session)) -> LocationRead:
    updated_location = await location_service.update_location(session, location_data)
    if not updated_location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return updated_location   

@location_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(session: AsyncSession = Depends(get_core_session)) -> None:
    success = await location_service.delete_location(session)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    