from typing import Text
from discord import Interaction, ui, TextStyle
from datetime import datetime
import asyncio

def two_digit(input: int) -> str:
    '''
    Convert a single digit number into two digits, and leave two digit numbers unchanged.\n
    ```
    two_digit(1) = '01'
    two_digit(12) = '12'
    ```
    '''
    return str(input) if input >=10 else '0' + str(input)

def get_12_hour_time(hour: int, minute: int):
    if hour < 12:
        hour = 12 if hour == 0 else hour # reassign 0 to 12
        return f'{two_digit(hour)}:{two_digit(minute)} AM'
    else:
        hour = 12 if hour == 12 else hour - 12 # make sure 12 corresponds to 12 PM, 13 = 1 PM, ...
        return f'{two_digit(hour)}:{two_digit(minute)} PM'

class EventPrompt(ui.Modal, title='Create Event'):
    name = ui.TextInput(label='Event Name', style=TextStyle.short, placeholder='Cool Event', required=True)
    start_time = ui.TextInput(label='Start Time', style=TextStyle.short, placeholder='MM/DD/YYYY @ HH:MM AM/PM', required=True)
    end_time = ui.TextInput(label='End Time', style=TextStyle.short, placeholder='MM/DD/YYYY @ HH:MM AM/PM', required=True)
    location = ui.TextInput(label='Location', style=TextStyle.short, placeholder='UCSB, Del Playa, Isla Vista, ...', required=True)
    description = ui.TextInput(label='Event Description', style=TextStyle.paragraph, placeholder='To have fun!', required=True)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        current_time = datetime.now()
        self.start_time.default = f'{two_digit(current_time.month)}/{two_digit(current_time.day)}/{current_time.year} @ {get_12_hour_time(current_time.hour, current_time.minute)}'

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.send_message('Submitted!', ephemeral=True)



