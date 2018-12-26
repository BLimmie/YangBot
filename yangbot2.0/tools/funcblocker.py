from datetime import datetime, timedelta


class funcblocker:
    def __init__(self, func, timer, roles, positive_roles=True):
        """
        args:
        func (function) = method to run
        timer (timedelta) = time between method procs, None if no timer
        roles (list of string) = list of role names, None if no restriction
        positive_roles (boolean) = True if only proc if user has roles, False if only proc if user has none of the roles
        """
        self.func = func
        self.timer = timer
        self.last_time = datetime.now() - timer if timer is not None else datetime.now()
        self.roles = roles
        self.positive_roles = positive_roles
    
    def proc(self, time, member, *args, **kwargs):
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
            if any(elem in self.roles for elem in member.roles):
                role = True
        else: # self.positive_roles = False
            if not any(elem in self.roles for elem in member.roles):
                role = True

        if role: # and too_soon = False
            return self.func(*args, **kwargs)