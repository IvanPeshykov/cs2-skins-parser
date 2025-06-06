import asyncio

# Class for managing proxies in an asynchronous environment
class ProxyManager:
    def __init__(self, proxies):
        self.available = asyncio.Queue()
        for proxy in proxies:
            self.available.put_nowait(proxy)

    async def get_proxy(self):
        proxy = await self.available.get()
        return proxy

    async def schedule_release(self, proxy, cooldown):
        # Schedule the release of the proxy after cooldown
        asyncio.create_task(self.release_proxy(proxy, cooldown))

    async def release_proxy(self, proxy, cooldown):
        await asyncio.sleep(cooldown)
        await self.available.put(proxy)