import aiohttp
import os

url = "https://api.ucsb.edu/dining/menu/v1/"
headers={
    'Accepts':'application/json',
    'ucsb-api-key': os.environ['UCSB_API_KEY']
}

async def get_allmenusaio(date):
    finalmenu={}
    open_commons= await get_menuaio(date)
    for common in open_commons:
        open_mealtimes=await get_menuaio(date,common['code'])
        singlemenu={}
        for mealtime in open_mealtimes:
            open_menu=await get_menuaio(date,common['code'],mealtime['code'])
            open_menu=reformat_menu(open_menu)
            singlemenu[mealtime['code']]=open_menu
        finalmenu[common['code']]=singlemenu
    return finalmenu


async def get_menuaio(*args):
    endpoint='/'.join(args)
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url+endpoint) as response:
            return ( await response.json())


def reformat_menu(inputmenu) -> dict:
    menu_dict = {}
    for item in inputmenu:
        station = item['station']
        menu_dict[station] = menu_dict.get(station, []) # Grabs the existing list or creates a new one
        menu_dict[station].append(item['name'])

    return menu_dict
