import aiohttp

async def get_menus() -> dict:
    '''
    An idea for implementation - Daniel

    This menu will send an HTTP request to UCSB API to grab all the menu information. It will then convert this information into a dictionary and return it.
    I think we should format the dictionary like this:
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
    '''
    pass