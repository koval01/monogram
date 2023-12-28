from redis import asyncio as aioredis
import config


class RedisStorage:
    cursor = None
    
    def __init__(self) -> None:
        self.redis_url: str = config.REDIS_URL
    
    def create_cursor(self) -> None:
        RedisStorage.cursor = aioredis.from_url(self.redis_url)
        
    @staticmethod
    async def shutdown() -> None:
        await RedisStorage.cursor.close()
        
    async def get(self, key: str) -> str | None:
        data = await self.cursor.get(key)
        return data.decode("utf-8") if data else None
    
    async def set(self, key: str, value: str, ex: int = None) -> bool:
        return await self.cursor.set(key, value, ex=ex)

    async def forget(self, key: str) -> bool:
        return await self.cursor.delete(key)
