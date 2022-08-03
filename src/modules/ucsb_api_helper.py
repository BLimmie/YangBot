import aiohttp
from datetime import date
from typing import Tuple

async def get_menus() -> Tuple[dict, date]:
    '''
    An idea for implementation - Daniel
    This will return two separate values as a tuple.

    The first value will be the menu itself. We will most likely have to run some logic with the output from the UCSB API.
    I think we should format the menu like this:
    {
        'DLG': {
            'Main Entrees': [
                'Chicken',
                'Potatoes'
            ],
            'Soups': {
                'Chicken Noodle',
                'Matzah Ball'
            }
        },
        'Ortega': {
            ...
        },
        'Portolla': {
            ...
        },
        'Carillo': {
            ...
        }
    }
    In other words, the outer dictionary contains each of the dining commons, and each of the dining commons are dictionaries of lists, where each list is some dish type.
    Assuming the UCSB API is standard, we'll probably need to deal with JSON objects.

    The second item to return will time information. This may be a part of the info grabbed from the API, but for now let's say it's the current date.
    '''
    return {
        'dlg': {
            'Main Entrees': [
                'Chicken',
                'Potatoes'
            ],
            'Soups': {
                'Chicken Noodle',
                'Matzah Ball'
            }
        },
        'ortega': {
            'Main Entrees': [
                'Steak',
                'Broccoli'
            ],
            'Salads': {
                'Caesar Salad',
                'Peanut Salad'
            }
        },
        'portolla': {
            'Main Entrees': [
                'Beef Broth Soup',
                'Spaghetti'
            ],
            'Pizza': {
                'Mushroom Pizza',
                'Cheese Pizza'
            }
        },
        'carillo': {
            'Main Entrees': [
                'Straganoff'
            ],
            'Dessert': {
                'Ice Cream',
                'Brownies'
            }
        }
    }, date.today().day