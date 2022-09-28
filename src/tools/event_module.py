from datetime import datetime
from discord import Member, TextChannel, PermissionOverwrite

'''
The purpose of this module is to allow storage of events 
in a single place without having to worry about recursion errors.
'''

def two_digit(input: int) -> str:
    '''
    Convert a single digit number into two digits, and leave two digit numbers unchanged.\n
    ```
    two_digit(1) = '01'
    two_digit(12) = '12'
    ```
    '''
    return str(input) if input >=10 else '0' + str(input)

def get_12_hour_time(hour: int, minute: int) -> str:
    '''
    Converts 24 hour time to 12 hour time.
    '''
    if hour < 12:
        hour = 12 if hour == 0 else hour # reassign 0 to 12
        return f'{two_digit(hour)}:{two_digit(minute)} AM'
    else:
        hour = 12 if hour == 12 else hour - 12 # make sure 12 corresponds to 12 PM, 13 = 1 PM, ...
        return f'{two_digit(hour)}:{two_digit(minute)} PM'

def str_to_datetime(date_str: str) -> datetime:
    '''
    Converts MM/DD/YYYY @ HH:MM AM/PM into a datetime object. May raise an IndexError or ValueError.
    '''
    full_tab = date_str.split(' ')
    dates = full_tab[0].split('/')
    timestampt = full_tab[2].split(':')
    tod = full_tab[3].lower()
    if tod not in ('am', 'pm'): raise ValueError

    month, day, year = int(dates[0]), int(dates[1]), int(dates[2])
    hour = int(timestampt[0])
    if tod == 'am':
        hour = 0 if hour == 12 else hour
    else:
        hour = 12 if hour == 12 else hour + 12
    minute = int(timestampt[1])

    return datetime(month=month, day=day, year=year, hour=hour, minute=minute)

def datetime_to_str(dt: datetime) -> str:
    '''
    Converts a datetime object into MM/DD/YYYY @ HH:MM AM/PM.
    '''
    return f'{two_digit(dt.month)}/{two_digit(dt.day)}/{dt.year} @ {get_12_hour_time(dt.hour, dt.minute)}'

class Event:
    '''
    
    '''
    active_events = {}

    def __init__(self, *, name: str, desc: str, location: str, start: str, end: str, channel: TextChannel, owner: int) -> None:
        self.name, self.desc, self.location, self.start, self.end = name, desc, location, start, end
        self.channel = channel
        self.owner = owner

    async def add_user(self, user: Member):
        await self.channel.set_permissions(user, overwrite=PermissionOverwrite(read_messages=True))
    
    async def remove_user(self, user: Member):
        await self.channel.set_permissions(user, overwrite=PermissionOverwrite(read_messages=False))


    @property
    def start_datetime(self) -> datetime:
        '''
        Converts `start` to a datetime object. May be reassigned, which will also reassign start.
        '''
        return str_to_datetime(self.start)

    @start_datetime.setter
    def start_datetime(self, dt: datetime) -> None:
        self.start = datetime_to_str(dt)

    @property
    def end_datetime(self) -> datetime:
        '''
        Converts `end` to a datetime object. May be reassigned, which will also reassign end.
        '''
        return str_to_datetime(self.end)

    @end_datetime.setter
    def end_datetime(self, dt: datetime):
        self.end = datetime_to_str(dt)
