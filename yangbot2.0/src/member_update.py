import psycopg2

from src.tools.message_return import message_data
from src.modules.db_helper import member_exists, fetch_member

def init(bot):
    @bot.on_member_update()
    def update_database(before, after):
        user_id = after.id
        conn = bot.conn
        roles_deleted = [role.id for role in before.roles if role not in after.roles]
        roles_added = [role.id for role in after.roles if role not in before.roles]
        print(roles_deleted)
        print(roles_added)
        if len(roles_deleted) == 0 and len(roles_added) == 0:
            return
        if not member_exists(conn, user_id):
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO Members (id, default_nickname)
                    VALUES (%s, %s) ;
                """,
                (after.id, after.display_name))
                conn.commit()
            except:
                conn.rollback()
        for role in roles_deleted:
            try:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE Members
                    SET role_%s = False
                    WHERE id = '%s' ;
                """,
                (role, user_id))
                conn.commit()
            except psycopg2.Error as e:
                conn.rollback()

        for role in roles_added:
            try:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE Members
                    SET role_%s = True
                    WHERE id = '%s' ;
                """,
                (role, user_id))
                conn.commit()
            except psycopg2.Error as e:
                conn.rollback()
