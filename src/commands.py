import psycopg2

from src.tools.message_return import message_data
from src.modules.db_helper import member_exists, refresh_member_in_db
from src.modules.discord_helper import change_nickname, kick_member
from src.modules.catfact_helper import get_catfact

def init(bot):
    @bot.command_on_message()
    def catfact(message):
        return message_data(message.channel, get_catfact())

    @bot.command_on_message()
    def register(message):
        print("Registering")
        user = message.author
        conn = bot.conn
        if not member_exists(conn, user.id):
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO Members (id, default_nickname)
                    VALUES (%s, %s) ;
                """,
                            (user.id, user.display_name))
                conn.commit()
                refresh_member_in_db(conn,user,bot.config["roles"])
            except:
                conn.rollback()
        else:
            return message_data(message.channel, "User already registered")
        return message_data(message.channel, "User registered")

    @bot.command_on_message()
    def resetregister(message):
        user = message.author
        conn = bot.conn
        if not member_exists(conn, user.id):
            return message_data(message.channel, "User not registered. Use $register to register.")

        try:
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM Members
                WHERE id = '%s' ;
            """,
                        (user.id,))
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()

        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Members (id, default_nickname)
                VALUES (%s, %s) ;
            """,
                        (user.id, user.display_name))
            conn.commit()
            refresh_member_in_db(conn, user, bot.config["roles"])
        except:
            conn.rollback()

        return message_data(message.channel, "User registration reset")
    
    @bot.command_on_message(coro=kick_member)
    def kickme(message):
        conn = bot.conn
        if not member_exists(conn, message.author.id):
            return message_data(message.channel, "You aren't registered in my memory yet. Please register with $register first")
        return message_data(message.author, "See you later! Rejoin at http://ucsbfriendos.org", args=[message.author])

    async def nickname_request(message, member, new_nickname):
        if new_nickname == None:
            return
        await member.send("Your nickname request has been submitted")
        await message.add_reaction('✅')
        await message.add_reaction('❎')
        def check(reaction, user):
            return reaction.message.id == message.id and not user.bot and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❎')

        reaction, user = await bot.client.wait_for("reaction_add", check=check)
        if str(reaction.emoji) == '✅':
            try:
                await change_nickname(member, new_nickname)
            except:
                await member.send("Nickname can't be changed")
                return
            await member.send("Your nickname request has been approved")
        else:
            await member.send("Your nickname request has been rejected")

    @bot.command_on_message(coro=nickname_request)
    def nickname(message):
        user = message.author
        content = message.content
        if len(content.split()) < 2:
            return message_data(
                message.channel,
                message= "No nickname requested, usage is $nickname [new nickname]",
                args=[user, None]
            )
        nickname = " ".join(content.split()[1:])
        if len(nickname) > 32:
            return message_data(
                message.channel,
                message= "Nickname requested is too long",
                args=[user, None]
            )
        return message_data(
            bot.client.get_channel(bot.config["requests_channel"]),
            message= "Member {} is requesting a nickname change\nNew nickname: {}".format(user.display_name, nickname),
            args=[user, nickname]
        )

    async def remove_message(message, command):
        await command.delete()

    send_roles = [
        bot.config["roles"]["Club Officers"],
        bot.config["roles"]["Admins"],
        bot.config["roles"]["Yangbot Devs"],
        bot.config["roles"]["Server Legacy"]
    ]
    @bot.command_on_message(roles=send_roles,positive_roles=True,coro=remove_message)
    def send(message):
        content = message.content
        if len(message.channel_mentions) > 0:
            return message_data(
                message.channel_mentions[0],
                content[content.find('>')+1:],
                args=[message]
            )