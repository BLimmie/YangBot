import discord
from discord import Interaction, ui, TextStyle
from datetime import datetime, timedelta
from src.tools.state_machines import Machine, Action, State
from src.modules.discord_helper import generate_embed

# Some helper functions for processing the datetime formats

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

# Some classes and constants

class Event:
    active_events = {}

    def __init__(self, *, name: str, desc: str, location: str, start: str, end: str, channel: discord.TextChannel) -> None:
        self.name, self.desc, self.location, self.start, self.end = name, desc, location, start, end
        self.channel = channel

    async def add_user(self, user: discord.Member):
        await self.channel.set_permissions(user, overwrite=discord.PermissionOverwrite(read_messages=False))
    
    async def remove_user(self, user: discord.Member):
        await self.channel.set_permissions(user, overwrite=discord.PermissionOverwrite(read_messages=True))


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

class EventRequest(Machine):
    '''
    A subclass of `state_machines.Machine` that overrides the `on_timeout` method.
    '''

    async def on_timeout(self) -> None:
        timed_out_state = State.from_state(self.state).remove_all_actions()
        timed_out_state.title = 'Expired Event Request'
        timed_out_state.color = 0xff5500
        await self.update_state(timed_out_state)

BASE_REQUEST_STATE = State.make_template(
    author={
        'name': '{display_name} ({discord_name})',
        'icon_url': '{avatar}'
    },
    title='Event Request',
    description='<@{user_id}> would like to create the following event.',
    fields=[
            {
                'name': 'Name',
                'value': '{event_name}'
            },
            {
                'name': 'Description',
                'value': '{event_desc}'
            },
            {
                'name': 'Start Time',
                'value': '{event_start}',
                'inline': True
            },
            {
                'name': 'End Time',
                'value': '{event_end}',
                'inline': True
            },
            {
                'name': 'Location',
                'value': '{event_location}'
            }
    ]
)

JOIN_EVENT_EMOJI = '✔️'
# The bulk of the code. The majority of processing is done in the 'on_submit' method.

class EventPrompt(ui.Modal, title='Create Event'):
    name = ui.TextInput(label='Event Name', style=TextStyle.short, placeholder='Cool Event', required=True)
    start_time = ui.TextInput(label='Start Time', style=TextStyle.short, placeholder='MM/DD/YYYY @ HH:MM AM/PM', required=True)
    end_time = ui.TextInput(label='End Time', style=TextStyle.short, placeholder='MM/DD/YYYY @ HH:MM AM/PM', required=True)
    location = ui.TextInput(label='Location', style=TextStyle.short, placeholder='UCSB, Del Playa, Isla Vista, ...', required=True)
    description = ui.TextInput(label='Event Description', style=TextStyle.paragraph, placeholder='To have fun!', required=True)
    __input_history: dict[int, dict] = {} # Saves failed inputs and to be used as default. Double underscore is used to prevent Modal's init from touching it.

    def __init__(self, *, banner: discord.Attachment | None, user_id: int, color: int, bot) -> None:
        super().__init__()
        self._banner = banner.url if banner is not None else None
        
        self._request: discord.TextChannel = bot.client.get_channel(bot.config['requests_channel'])
        self._event: discord.TextChannel = bot.client.get_channel(bot.config['events_channel'])
        self._events_category: discord.CategoryChannel = bot.client.get_channel(bot.config['events_category'])
        self._guild: discord.Guild = bot.guild
        self._color = color

        current_time = datetime.now() + timedelta(days=1)
        # There can only be an entry in the dictionary if there's a failed attempt. Successful attempts automatically delete them.
        if user_id not in self.__input_history:
            self.start_time.default = datetime_to_str(current_time)
        else:
            working_dict = self.__input_history[user_id]
            self.name.default = working_dict['name']
            self.start_time.default = working_dict['start']
            self.end_time.default = working_dict['end']
            self.location.default = working_dict['location']
            self.description.default = working_dict['description']
        

    async def on_submit(self, interaction: Interaction) -> None:
        name, start, end, location, desc = self.name.value, self.start_time.value, self.end_time.value, self.location.value, self.description.value
        self.__input_history[interaction.user.id] = {
            'name': name,
            'start': start,
            'end': end,
            'location': location,
            'description': desc
        }

        # sanity check the start times, namely:
        # 1. is the provided input valid (i.e can it be converted into a datetime object successfully)
        # 2. is the event going to occur in the future
        # 3. is start before (or equal to) end
        try:
            start_datetime = str_to_datetime(start)
            end_datetime = str_to_datetime(end)
        except (ValueError, IndexError):
            return await interaction.response.send_message(f"You formatted `{start}` or `{end}` incorrectly, or provided an invalid date-time.\nThe proper format is `MM/DD/YYYY @ HH:MM AM/PM` (e.g `01/01/2000 @ 12:00 AM`)", ephemeral=True)
        now = datetime.now()
        if now > start_datetime or now > end_datetime:
            return await interaction.response.send_message("You can't set an event in the past.", ephemeral=True)
        if start_datetime >= end_datetime:
            return await interaction.response.send_message("The start time can't be after the end time.", ephemeral=True)
        
        # create request embed and send it
        del self.__input_history[interaction.user.id] # no need to keep it if everything was fine.
        initial_state = State.from_state(BASE_REQUEST_STATE).format(
            display_name=interaction.user.display_name,
            discord_name=f'{interaction.user.name}#{interaction.user.discriminator}',
            avatar=interaction.user.display_avatar.url,
            user_id=interaction.user.id,
            event_name=name,
            event_desc=desc,
            event_start=start,
            event_end=end,
            event_location=location,
            color=0xf1dd00,
            image=self._banner,
            timestamp=end_datetime
        )
        
        @Action.new(label='Approve', style=discord.ButtonStyle.green, emoji='👍')
        async def approve(machine: Machine, button_inter: Interaction):
            approved_state = State.from_state(initial_state).remove_all_actions()
            approved_state.color = 0x04ff00
            approved_state.title = 'Approved Event Request'
            approved_state.description = f'This event was approved by <@{button_inter.user.id}>'

            # publish event here
            embed = generate_embed({
                'author': machine.state.author,
                'title': name,
                'description': desc,
                'color': self._color,
                'image': self._banner,
                'fields': [
                    {
                        'name': 'Start Time',
                        'value': start,
                        'inline': True
                    },
                    {
                        'name': 'End Time',
                        'value': end,
                        'inline': True
                    },
                    {
                        'name': 'Location',
                        'value': location
                    }
                ],
                'timestamp': end_datetime
            })
            msg = await self._event.send(embed=embed)
            await msg.add_reaction(JOIN_EVENT_EMOJI)
            channel = await self._events_category.create_text_channel(name=name, overwrites={
                self._guild.default_role: discord.PermissionOverwrite(read_messages=False),
                self._guild.me: discord.PermissionOverwrite(read_messages=True)
            })
            print(channel, self._events_category)
            Event.active_events[msg.id] = Event(name=name, desc=desc, location=location, start=start, end=end, channel=channel)
            # add listener here
            await machine.update_state(approved_state, button_inter)

        @Action.new(label='Reject', style=discord.ButtonStyle.red, emoji='👎')
        async def reject(machine: Machine, interaction: Interaction):
            rejected_state = State.from_state(initial_state).remove_all_actions()
            rejected_state.color = 0xff0000
            rejected_state.title = 'Rejected Event Request'
            rejected_state.description = f'This event was rejected by <@{interaction.user.id}>'
            await machine.update_state(rejected_state, interaction)

        initial_state.add_action(approve, reject)

        await EventRequest.create(initial_state, channel=self._request, whitelist=None, history=None) #, timeout=86400)

        await interaction.response.send_message('Your event request was submitted! If approved, it will be posted within 24 hours.', ephemeral=True)
