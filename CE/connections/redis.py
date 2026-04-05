import redis.asyncio as redis
from CE.config import settings
import json

class RedisClient:
    def __init__(self, db: int = 0):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=db,
            decode_responses=True
        )
    
    async def delete(self, key) -> None:
        await self.client.delete(key)

    async def flushdb(self) -> None:
        await self.client.flushdb()

    async def hdel(self, name, key) -> None:
        await self.client.hdel(name, key)

    async def hget(self, name, key) -> str:
        return await self.client.hget(name, key)
    
    async def hset(self, name, key, value) -> None:
        await self.client.hset(name, key, json.dumps(value))

class RedisClientRegistry:
    db_client: redis.Redis = None
    control_client: redis.Redis = None

    @classmethod
    def set_db_client(cls, client: RedisClient):
        cls.db_client = client

    @classmethod
    def set_control_client(cls, client: RedisClient):
        cls.control_client = client

    @classmethod
    def get_db_client(cls) -> RedisClient:
        if not cls.db_client:
            raise RuntimeError("DB Redis client not initialized")
        return cls.db_client

    @classmethod
    def get_control_client(cls) -> RedisClient:
        if not cls.control_client:
            raise RuntimeError("Control Redis client not initialized")
        return cls.control_client


async def init_redis():
    db_client = RedisClient(db=0)
    control_client = RedisClient(db=1)

    RedisClientRegistry.set_db_client(db_client)
    RedisClientRegistry.set_control_client(control_client)

    await db_client.flushdb()