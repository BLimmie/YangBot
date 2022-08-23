import aiohttp
<<<<<<< HEAD
from datetime import date
from typing import Tuple
from src.tools.state_machines import Machine, Action, State
from src.commands import command_on_message
import json
import requests

def get_menu(*args):
    url= "https://api.ucsb.edu/dining/menu/v1/"
    headers={
        'Accepts':'application/json',
        'ucsb-api-key':'xBFGNoI4JydvsAOz2tdIDouOCXmTdLS8'
    }
    for arg in args:
        url+=arg
        url+='/'
    response = requests.get(url,headers)
    return response.json()

def get_allmenus():
    """
    returns json that later can be loaded to look like
    {
        'carrillo': {
            'brunch': [
                {'name': 'Sliced Turkey', 'station': 'Deli'}, 
            ], 
        }, 
     }
    """
    finalmenu={}
    testurl='https://api.ucsb.edu/dining/menu/v1/2021-09-25'
    open_commons=requests.get(testurl,headers)
    open_commons=open_commons.json()
    for common in open_commons:
        open_mealtimes=requests.get(testurl+'/'+common['code'],headers)
        open_mealtimes=open_mealtimes.json()
        singlemenu={}
        for mealtime in open_mealtimes:
            open_menu=requests.get(testurl+'/'+common['code']+'/'+mealtime['code'],headers)
            open_menu=open_menu.json()
            singlemenu[mealtime['code']]=open_menu
        finalmenu[common['code']]=singlemenu
    return finalmenu

async def get_menus() -> Tuple[dict, date]:
<<<<<<< HEAD
    '''
    An idea for implementation - Daniel
    This will return two separate values as a tuple.
=======
import asyncio
import os

testinputmenu=[{'name': 'Baked Potato (vgn)', 'station': 'Greens & Grains'}, {'name': 'Jasmine Rice (vgn)', 'station': 'Greens & Grains'}, {'name': 'Chicken Noodle Soup', 'station': 'Greens & Grains'}, {'name': 'Watermelon Salad (vgn)', 'station': 'Salad Bar Featured Items'}, {'name': 'Orange Pickled Carrot Coins (vgn)', 'station': 'Salad Bar Featured Items'}, {'name': 'Bulgur Wheat (vgn)', 'station': 'Salad Bar Featured Items'}, {'name': 'Sausage Mushroom Pizza', 'station': 'The Brick'}, {'name': 'Alfredo Sauce', 'station': 'The Brick'}, {'name': 'Fettuccine Pasta (vgn)', 'station': 'The Brick'}, {'name': 'Fresh Tomato Basil Garlic Pasta (vgn)', 'station': 'The Brick'}, {'name': 'German Chocolate Cake (w/nuts) (v)', 'station': 'Bakery'}, {'name': 'Whole Wheat Sourdough Bread (v)', 'station': 'Bakery'}, {'name': 'BBQ Chicken Thigh', 'station': "Chef's Choice"}, {'name': 'Tangy Apple Cabbage Slaw (vgn)', 'station': "Chef's Choice"}, {'name': 'Chili Beans (vgn)', 'station': "Chef's Choice"}, {'name': 'Fresh Sauteed Spinach (vgn)', 'station': "Chef's Choice"}, {'name': 'Asian Beef Bowl', 'station': 'International'}, {'name': 'Sticky Rice (vgn)', 'station': 'International'}, {'name': 'Tofu Teriyaki Bowl (vgn)', 'station': 'International'}, {'name': 'Spinach with Fresh Garlic & Ginger (vgn)', 'station': 'International'}, {'name': 'Calamari Roll', 'station': 'International'}, {'name': 'Vegetable Roll (vgn)', 'station': 'International'}]
url = "https://api.ucsb.edu/dining/menu/v1/"
headers={
    'Accepts':'application/json',
    'ucsb-api-key':os.environ['UCSB-API-KEY']
}
>>>>>>> 3e1d4b9 (Removed API key and fixed bug with DLG)
=======
    return json.loads(get_allmenus()), date.today().day
>>>>>>> af97c91 (draft of processing api json objects)

def reformat_allmenus() -> dict:
    """
    ideally want to return a dict with foods grouped by station
    {
        'dlg': {
            'breakfast': {
                'grill': ['eggs', 'waffles']
            },
            'lunch': {
                'white table': [...]
            }
        }
        'carrillo': {
            ...
        }
    }
    
    """
    menu = get_allmenus()
    new_menu = {}
    for common in menu.keys():
        new_menu[common] = {}
        for time in menu[common].keys():
            new_menu[common][time] = reformat_menu(date.today().day, common, time)
    return new_menu

<<<<<<< HEAD
def reformat_menu(*args) -> dict:
    """
    @param entrees in form of [{'name': 'food_name', 'station': 'station_name'}, {...}]
    
    given a list of dictionaries, group names to stations
    """
    menu = get_menu(args)
    fields = {}
    for entree_dict in menu:
        for entree in entree_dict:
            if entree['station'] not in fields.keys():
                fields[entree['station']] = menu['name']
            else:
                fields[entree['station']].append(menu['name'])
    return fields
=======

async def get_menuaio(*args):
    endpoint='/'.join(args)
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url+endpoint) as response:
            return ( await response.json())


async def reformat_menu(inputmenu) -> dict:
    menu_dict = {}
    for item in inputmenu:
        station = item['station']
        menu_dict[station] = menu_dict.get(station, []) # Grabs the existing list or creates a new one
        menu_dict[station].append(item['name'])

    return menu_dict
    # stationlist=[]
    # stationcurrent=inputmenu[0]['station']
    # stationdict={stationcurrent:[]}
    # for entrees in inputmenu:
    #     if entrees['station'] == stationcurrent:
    #         stationdict[stationcurrent].append(entrees['name'])
    #     else:
    #         stationlist.append(stationdict)
    #         stationcurrent=entrees['station']
    #         stationdict={stationcurrent:[]}
    #         stationdict[stationcurrent].append(entrees['name'])
    # stationlist.append(stationdict)  
    # return stationlist
>>>>>>> b958771 (Menu command is now in a workable state.)
