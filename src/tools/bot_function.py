from datetime import datetime

class bot_function:
    def __init__(self, bot,timer=None, roles=None, positive_roles=True):
        self.bot = bot
        self.timer = timer
        self.last_time = datetime.now() - timer if timer is not None else datetime.now()
        self.roles = roles
        self.positive_roles = positive_roles
    async def simple_proc(self, message):
        return await self.action(message)
    async def proc(self, message, time, member):
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
        elif self.positive_roles:
            if any(elem.id in self.roles for elem in member.roles):
                role = True
        else:  # self.positive_roles = False
            if not any(elem.id in self.roles for elem in member.roles):
                role = True

        if role:  # and too_soon = False
            message = await self.action(message)
            if message is not None:
                self.last_time = time
            return message
        
    async def action(self, message):
        raise NotImplementedError