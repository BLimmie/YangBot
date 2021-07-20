from src.tools.message_return import message_data
from src.modules.db_helper import member_exists, fetch_member_roles, fetch_member_nickname
from src.modules.discord_helper import add_roles, change_nickname
from src.tools.botfunction import BotFunction

class on_member_join(BotFunction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, message, *args, **kwargs):
        raise NotImplementedError

class restore_roles(on_member_join):
    """
    Restores roles and nickname on member join if member exists in database
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def restore(message, user, member_roles, nickname):
        try:
            await add_roles(user, member_roles)
        except:
            print("Roles cannot be added to user: {}".format(user.name))
        await change_nickname(user, nickname)

    async def action(self, user):
        conn = self.bot.conn
        if member_exists(conn, user.id):
            roles = sorted(self.bot.roles.items(), key=lambda x: x[1])
            member = fetch_member_roles(conn, user.id, roles)
            member_roles = [self.bot.client.get_guild(int(self.bot.config["server_id"])).get_role(
                role) for role in member]
            nickname = fetch_member_nickname(conn, user.id)
            return message_data(user, "Your roles have been restored", args=[user, member_roles, nickname])
