import psycopg2

from src.tools.message_return import message_data
from src.modules.db_helper import member_exists
from src.modules.discord_helper import kick_member


def init(bot):
    @bot.command_on_message()
    def catfact(message):
        pass

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
            except:
                conn.rollback()
        else:
            return message_data(message.channel, "User already registered")
        for role in user.roles:
            try:
                cur = conn.cursor()
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
                        (user.id, user.nick if user.nick is not None else user.name))
            conn.commit()
        except:
            conn.rollback()

        for role in user.roles:
            try:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE Members
                    SET role_%s = True
                    WHERE id = '%s' ;
                """,
                            (role.id, user.id))
                conn.commit()
            except psycopg2.Error as e:
                conn.rollback()

        return message_data(message.channel, "User registration reset")
    
    @bot.command_on_message(coro=kick_member)
    def kickme(message):
        conn = bot.conn
        if not member_exists(conn, message.author.id):
            return message_data(message.channel, "You aren't registered in my memory yet. Please register with $register")
        return message_data(message.author, "See you later!",[message.author])
