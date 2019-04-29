import aiohttp
import asyncio

def get_catfact():
    async def _get_catfact():
        async with aiohttp.ClientSession() as session:
            async with session.get('https://catfact.ninja/fact') as resp:
                data = await resp.json()
                return data['fact']
    main_loop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(_get_catfact())
    loop.close()
    asyncio.set_event_loop(main_loop)
    return result
    


if __name__ == "__main__":
    print(get_catfact())