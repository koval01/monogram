from redis import asyncio as aioredis

from decorators import async_timer

import config


class RedisStorage:
    cursor = None
    
    def __init__(self) -> None:
        """
        Initializes a RedisStorage instance.
        """

        self.redis_url: str = config.REDIS_URL
    
    def create_cursor(self) -> None:
        """
        Creates a connection cursor to the Redis database.
        """

        RedisStorage.cursor = aioredis.from_url(self.redis_url)
        
    @staticmethod
    async def shutdown() -> None:
        """
        Closes the connection cursor to the Redis database.
        """

        await RedisStorage.cursor.close()
        
    @async_timer
    async def get(self, key: str) -> str | None:
        """
        Retrieves the value associated with the specified key from the Redis database.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            str | None: The value associated with the key or None if the key is not found.
        """

        data = await self.cursor.get(key)
        return data.decode("utf-8") if data else None
    
    @async_timer
    async def set(self, key: str, value: str, ex: int = None) -> bool:
        """
        Sets the value associated with the specified key in the Redis database.

        Args:
            key (str): The key to set the value for.
            value (str): The value to be associated with the key.
            ex (int): Optional. Expiry time for the key-value pair in seconds.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """

        return await self.cursor.set(key, value, ex=ex)

    @async_timer
    async def forget(self, key: str) -> bool:
        """
        Deletes the specified key-value pair from the Redis database.

        Args:
            key (str): The key to delete from the Redis database.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """

        return await self.cursor.delete(key)
