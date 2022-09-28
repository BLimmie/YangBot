import discord
from discord import Interaction, ui, TextStyle
from datetime import datetime, timedelta
from src.tools.state_machines import Machine, Action, State
from src.modules.discord_helper import generate_embed
import src.tools.event_module as event_module
str_to_datetime, datetime_to_str, Event = event_module.str_to_datetime, event_module.datetime_to_str, event_module.Event


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

# The code will be largely identical. 
# The big difference is __init__, approve, and a message is editted instead of created.
# All differences will be marked by comments to distinguish them.
# However, this is NOT a subclass to prevent conflict among the class instances.
class ModifyModal(ui.Modal, title='Modify Event'):
    name = ui.TextInput(label='Event Name', style=TextStyle.short, placeholder='Cool Event', required=True)
    start_time = ui.TextInput(label='Start Time', style=TextStyle.short, placeholder='MM/DD/YYYY @ HH:MM AM/PM', required=True)
    end_time = ui.TextInput(label='End Time', style=TextStyle.short, placeholder='MM/DD/YYYY @ HH:MM AM/PM', required=True)
    location = ui.TextInput(label='Location', style=TextStyle.short, placeholder='UCSB, Del Playa, Isla Vista, ...', required=True)
    description = ui.TextInput(label='Event Description', style=TextStyle.paragraph, placeholder='To have fun!', required=True)

    def __init__(self, *, banner: discord.Attachment | None, user_id: int, color: int, bot) -> None:
        '''
        1. save important instance variables
        2. set defauls
        '''
        super().__init__()
        self._banner = banner.url if banner is not None else None
        
        self._request: discord.TextChannel = bot.client.get_channel(bot.config['requests_channel'])
        self._event: discord.TextChannel = bot.client.get_channel(bot.config['events_channel'])
        self._events_category: discord.CategoryChannel = bot.client.get_channel(bot.config['events_category'])
        self._guild: discord.Guild = bot.guild
        self._color = color        