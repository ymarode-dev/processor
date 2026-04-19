from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from .schemas import DeviceRead, DeviceCreate, DeviceUpdate, DeviceFilter
from connections.sqlite import get_core_session
from .service import DeviceService   
from connections.redis import RedisClientRegistry, RedisClient
from connections.mqtt import MqttClientRegistry, MqttClient
from typing import List

device_router = APIRouter()
device_service = DeviceService()

@device_router.get("/", response_model=List[DeviceRead], status_code=status.HTTP_200_OK)
async def get_devices(
    filters: DeviceFilter = Depends(),
    session: AsyncSession = Depends(get_core_session),
    redis_client: RedisClient = Depends(RedisClientRegistry.get_db_client)
) -> List[DeviceRead]:
    
    filter_dict = filters.model_dump(exclude_none=True)
    return await device_service.get_devices(session, filter_dict, redis_client)


@device_router.post("/", response_model=List[DeviceRead], status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: List[DeviceCreate], 
    session: AsyncSession = Depends(get_core_session),
    redis_client: RedisClient = Depends(RedisClientRegistry.get_db_client),
    hub_mqtt_client: MqttClient = Depends(MqttClientRegistry.get_hub)
    ) -> List[DeviceRead]:

    new_devices = await device_service.create_device(session, device_data, redis_client, hub_mqtt_client)
    return new_devices


@device_router.patch("/", response_model=List[DeviceRead], status_code=status.HTTP_200_OK)
async def update_device(
    device_data: DeviceUpdate, 
    filters: DeviceFilter = Depends(), 
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client),
    hub_mqtt_client: MqttClient = Depends(MqttClientRegistry.get_hub)
    ) -> List[DeviceRead]:

    filter_dict = filters.model_dump(exclude_none=True)
    updated_device = await device_service.update_device(session, filter_dict, device_data, redis_client, hub_mqtt_client)
    if not updated_device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return updated_device   


@device_router.delete("/", response_model=List[DeviceRead], status_code=status.HTTP_200_OK)
async def delete_device(
    filters: DeviceFilter = Depends(), 
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client),
    hub_mqtt_client: MqttClient = Depends(MqttClientRegistry.get_hub)
    ) -> List[DeviceRead]:

    filter_dict = filters.model_dump(exclude_none=True)
    device = await device_service.delete_device(session, filter_dict, redis_client, hub_mqtt_client)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device
    