from discord import Interaction, ui, TextStyle
from datetime import datetime, timedelta
# from src.modules.discord_helper import generate_embed

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

def convert_to_datetime(date_str: str) -> datetime:
    '''
    Converts MM/DD/YYYY @ HH:MM AM/PM into a datetime object. May raise an IndexError.
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

class EventPrompt(ui.Modal, title='Create Event'):
    name = ui.TextInput(label='Event Name', style=TextStyle.short, placeholder='Cool Event', required=True)
    start_time = ui.TextInput(label='Start Time', style=TextStyle.short, placeholder='MM/DD/YYYY @ HH:MM AM/PM', required=True)
    end_time = ui.TextInput(label='End Time', style=TextStyle.short, placeholder='MM/DD/YYYY @ HH:MM AM/PM', required=True)
    location = ui.TextInput(label='Location', style=TextStyle.short, placeholder='UCSB, Del Playa, Isla Vista, ...', required=True)
    description = ui.TextInput(label='Event Description', style=TextStyle.paragraph, placeholder='To have fun!', required=True)

    def __init__(self, *, banner, **kwargs) -> None:
        super().__init__(**kwargs)
        self._banner = banner
        current_time = datetime.now() + timedelta(days=1)
        self.start_time.default = f'{two_digit(current_time.month)}/{two_digit(current_time.day)}/{current_time.year} @ {get_12_hour_time(current_time.hour, current_time.minute)}'

    async def on_submit(self, interaction: Interaction) -> None:
        name, start, end, location, desc = self.name.value, self.start_time.value, self.end_time.value, self.location.value, self.description.value
        # make sure the start/end times are good
        try:
            start_datetime = convert_to_datetime(start)
            end_datetime = convert_to_datetime(end)
        except (ValueError, IndexError):
            return await interaction.response.send_message(f"You formatted `{start}` or `{end}` incorrectly. The date format is `MM/DD/YYYY @ HH:MM AM/PM` (e.g `01/01/2000 @ 12:00 AM`)\nFor easy copy-and-paste, here was your inputs:\nName: `{name}`\nStart Time: `{start}`\nEnd Time: `{end}`\nLocation: `{location}`\nDescription```{desc}```", ephemeral=True)
        now = datetime.now()
        if now > start_datetime or now > end_datetime:
            return await interaction.response.send_message(f"You can't set an event in the past.\nFor easy copy-and-paste, here was your inputs:\nName: `{name}`\nStart Time: `{start}`\nEnd Time: `{end}`\nLocation: `{location}`\nDescription```{desc}```", ephemeral=True)
        if start_datetime >= end_datetime:
            return await interaction.response.send_message(f"The start time can't be after the end time.\nFor easy copy-and-paste, here was your inputs:\nName: `{name}`\nStart Time: `{start}`\nEnd Time: `{end}`\nLocation: `{location}`\nDescription```{desc}```", ephemeral=True)

        # create request embed and send it
        await interaction.response.send_message('Your event request was submitted! If approved, it will be posted within 24 hours.', ephemeral=True)
