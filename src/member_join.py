import psycopg2
import json

from src.tools.message_return import message_data

from src.modules.db_helper import member_exists, fetch_member
from src.modules.discord_helper import add_roles, change_nickname


def init(bot):
    async def restore(message, user, member_roles, nickname):
        try:
            await add_roles(user, member_roles)
        except:
            pass
        await change_nickname(user, nickname)

    @bot.on_member_join(restore)
    def restore_roles(user):
        conn = bot.conn
        if member_exists(conn, user.id):
            member = fetch_member(conn, user.id)
            roles = sorted(bot.config["roles"].values())
            member_roles = [bot.client.get_guild(int(bot.config["server_id"])).get_role(
                role[0]) for role in zip(roles, member[2:]) if role[1]]
            nickname = member[1]
            return message_data(user, "Your roles have been restored", args=[user, member_roles, nickname])
            
