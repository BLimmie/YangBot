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
        'dlg': {
            'breakfast': {
                ...
            },
            'lunch': {
                ...
            }
            'dinner': {
                'Main Entrees': [
                    'Chicken',
                    'Potatoes'
                ],
                'Soups': [
                    'Chicken Noodle',
                    'Matzah Ball'
                ]
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
    In other words, the outer dictionary contains each of the dining commons, each of the dining commons contain the mealtimes, and each mealtime contains lists of its food.
    Assuming the UCSB API is standard, we'll probably need to deal with JSON objects.

    The second item to return will time information. This may be a part of the info grabbed from the API, but for now let's say it's the current date.
    '''
    return {
        'dlg': {
            'breakfast': {
                'Main Entres': [
                    'Eggs'
                ]
            },
            'lunch': {
                'Main Entres': [
                    'Chicken Sandwich'
                ]
            },
            'dinner': {
                'Main Entrees': [
                    'Chicken',
                    'Potatoes'
                ],
                'Soups': [
                    'Chicken Noodle',
                    'Matzah Ball'
                ]
            }
        },
        'ortega': {
            'breakfast': {
                'Main Entres': [
                    'Eggs'
                ]
            },
            'lunch': {
                'Main Entres': [
                    'Chicken Sandwich'
                ]
            },
            'dinner': {
                'Main Entrees': [
                    'Steak',
                    'Broccoli'
                ],
                'Salads': [
                    'Caesar Salad',
                    'Peanut Salad'
                ]
            }
        },
        'portolla': {
            'breakfast': {
                'Main Entres': [
                    'Eggs'
                ]
            },
            'lunch': {
                'Main Entres': [
                    'Chicken Sandwich'
                ]
            },
            'dinner': {
                'Main Entrees': [
                    'Beef Broth Soup',
                    'Spaghetti'
                ],
                'Pizza': [
                    'Mushroom Pizza',
                    'Cheese Pizza'
                ]
            }
        },
        'carrillo': {
            'breakfast': {
                'Main Entres': [
                    'Eggs'
                ]
            },
            'lunch': {
                'Main Entres': [
                    'Chicken Sandwich'
                ]
            },
            'dinner': {
                'Main Entrees': [
                    'Straganoff'
                ],
                'Dessert': [
                    'Ice Cream',
                    'Brownies'
                ]
            }
        }
    }, date.today().day