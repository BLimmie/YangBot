import psycopg2
import json

from src.yangbot import YangBot
from src.tools.message_return import message_data

from src.modules.db_helper import member_exists, fetch_member
from src.modules.discord_helper import add_roles, change_nickname

def init(bot, config):
    async def restore(user, member_roles, nickname):
        try:
            await add_roles(user, member_roles)
        except:
            pass
        await change_nickname(user, nickname)
    @bot.on_member_join(None,None,True,restore)
    def restore_roles(user):
        conn = bot.conn
        if member_exists(conn, user.id):
            member = fetch_member(conn, user.id)
            roles = config["roles"].values()
            member_roles = [bot.client.get_guild(int(config["server_id"])).get_role(role[0]) for role in zip(roles, member[2:]) if role[1]]
            nickname = member[1]
            # if user.dm_channel is None:
            #     dm = user.create_dm()
            # else:
            #     dm = user.dm_channel
            return message_data(None, None, [user, member_roles, nickname])
            
