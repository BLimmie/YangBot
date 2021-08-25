from datetime import datetime, timedelta
from typing import List


class BotFunction:
    def __init__(self, bot = None, timer: timedelta = None, roles: List[int] = None, role_whitelist: bool = True):
        self.bot = bot
        self.timer = timer
        self.last_time = datetime.now() - timer if timer is not None else datetime.now()
        self.roles = roles
        self.role_whitelist = role_whitelist

    def debug_reset(self):
        pass

    async def simple_proc(self, *args, **kwargs):
        return await self.decide_action(*args, **kwargs)

    async def proc(self, message, time, member, *args, **kwargs):
        """
        Run the function with the given time, member, and args.
        Use this when a function has restrictions (i.e. not for on_member_update/join)
        """
        role = False
        too_soon = True

        # Check timer condition
        if self.timer is None:
            too_soon = False
        elif (time - self.last_time) > self.timer:
            too_soon = False

        # Save computation time if role condition not satisfied
        if too_soon:
            return

        # Check role condition
        if self.roles is None:
            role = True
        elif self.role_whitelist:
            if any(elem.id in self.roles for elem in member.roles):
                role = True
        else:  # self.positive_roles = False
            if not any(elem.id in self.roles for elem in member.roles):
                role = True

        if role:  # and too_soon = False
            if self.bot is None:
                raise AttributeError("No Yangbot instance found in function")
            message = await self.decide_action(message, *args, **kwargs)
            if message is not None:
                self.last_time = time
            return message

    async def action(self, *args, **kwargs):
        raise NotImplementedError

    async def debug_action(self, *args, **kwargs):
        return self.action(*args, **kwargs)

    async def decide_action(self, message, *args, **kwargs):
        if self.bot.debug:
            return await self.debug_action(*args, **kwargs)
        else:
            return await self.action(message, *args, **kwargs)