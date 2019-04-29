import aiohttp
import asyncio

def get_catfact():
    async def _get_catfact():
        async with aiohttp.ClientSession() as session:
            async with session.get('https://catfact.ninja/fact') as resp:
                data = await resp.json()
                return data['fact']
    return asyncio.get_event_loop().run_until_complete(_get_catfact())
    


if __name__ == "__main__":
    print(get_catfact())