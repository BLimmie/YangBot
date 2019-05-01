from datetime import datetime


class funcblocker:
    def __init__(self, func, timer=None, roles=None, positive_roles=True, coro=None):
        """
        args:
        func (function) = method to run
        timer (timedelta) = time between method procs, None if no timer
        roles (list of string) = list of role ids, None if no restriction
        positive_roles (boolean) = True if only proc if user has roles, False if only proc if user has none of the roles
        coro (couroutine) = couroutine to run after sending message.
        The first argument of the coro should be the message that was sent or None if no message was sent.
        """
        self.func = func
        self.timer = timer
        self.last_time = datetime.now() - timer if timer is not None else datetime.now()
        self.roles = roles
        self.positive_roles = positive_roles
        self.coro = coro

    def simple_proc(self, *args, **kwargs):
        """
        Run the function with the given args
        """
        return self.func(*args, **kwargs)

    def proc(self, time, member, *args, **kwargs):
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
        self.last_time = time

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
            return self.func(*args, **kwargs)
