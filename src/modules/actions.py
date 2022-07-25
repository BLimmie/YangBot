from types import coroutine
from discord.ui import Button
from discord import ButtonStyle, Emoji

async def _DefaultCallback(machine, interaction): # Instead of a print statement, call machine.update_state and change the embed message to the content inside the print statement.
    print('Button was pressed by', interaction.user.name, 'in channel', interaction.channel.name)

class action(Button):
    '''
    An object representing a button within discord. Designed to work with the machine class.

    ## Parameters
    All of the following parameters (except machine) are keyword-only and optional. Unless otherwise specified, all optional parameters default to `None`.

    `machine`: The machine object this button is attached to.

    `callback`: The coroute that will be invoked when the button is pressed. The action's machine and a `discord.Interaction` object is passed onto this callback as parameters. Defaults to a print statement.

    It is expected that `callback` will generate a state object and call `update_state` onto its passed machine.

    `style`: The style for the button. Defaults to `discord.ButtonStyle.blurple`.

    `label`: The label (text) of the button.

    `emoji`: A `discord.Emoji` object, representing the emoji of the button.

    `row`: The row the button should be placed in, must be between 0 and 4 (inclusive). If this isn't specified, then automatic ordering will be applied.

    `url`: A string representing the url that this button should send to. Note that specifying this changes some functionality (see discord.py docs).

    `disabled`: Whether the button should invoke `callback` whenever pressed. Defaults to `False`.

    ## Attributes

    `machine`: The machine tied to this action.
    '''
    def __init__(self, machine, *, callback = _DefaultCallback , style: ButtonStyle=ButtonStyle.blurple, label: str=None, emoji: Emoji=None, row: int=None, url: str=None, disabled: bool=False):
        super().__init__(style=style, label=label, emoji=emoji, row=row, url=url, disabled=disabled)
        self.machine = machine
        self._callback = callback

    async def callback(self, interaction):
        await self._callback(self.machine, interaction)