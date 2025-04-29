import asyncio

class ProxyManager:
    def __init__(self, proxies):
        self.available = asyncio.Queue()
        for proxy in proxies:
            self.available.put_nowait(proxy)

    async def get_proxy(self, cooldown):
        proxy = await self.available.get()
        # Schedule return after cooldown
        asyncio.create_task(self.release_proxy(proxy, cooldown))
        return proxy

    async def release_proxy(self, proxy, cooldown):
        await asyncio.sleep(cooldown)
        await self.available.put(proxy)