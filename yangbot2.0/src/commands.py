import psycopg2

from src.yangbot import YangBot
from src.tools.message_return import message_data

def init(bot, config, conn):
    @bot.command_on_message()
    def catfact(message):
        pass

    @bot.command_on_message()
    def register(message):
        print("Registering")
        user = message.author
        cur = bot.cur
        try:
            cur.execute("""
                INSERT INTO Members (id, default_nickname)
                VALUES (%s, %s) ;
            """,
            (user.id, user.nick if user.nick is not None else user.name))
        except:
            conn.rollback()
        conn.commit()
        for role in user.roles:
            try:
                cur.execute("""
                    UPDATE Members
                    SET role_%s = True
                    WHERE id = '%s' ;
                """,
                (role.id, user.id))
                conn.commit()
            except psycopg2.Error as e:
                conn.rollback()

        return message_data(message.channel, "User registered")