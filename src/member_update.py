import psycopg2
from src.modules.db_helper import member_exists, insert_member, connection_error
from src.tools.botfunction import BotFunction

class on_member_update(BotFunction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, message, *args, **kwargs):
        raise NotImplementedError

class update_database_roles(on_member_update):
    """
    Updates the member roles in the database after member is updated
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, before, after):
        user_id = after.id
        conn = self.bot.conn
        roles_deleted = [role.id for role in before.roles if role not in after.roles]
        roles_added = [role.id for role in after.roles if role not in before.roles]
        if len(roles_deleted) == 0 and len(roles_added) == 0:
            return
        if not member_exists(conn, user_id):
            insert_member(conn, self.bot, after)
        for role in roles_deleted:
            try:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE members
                    SET roles = REPLACE(roles,',%s','')
                    WHERE id = '%s' ;
                """,
                            (role, user_id))
                conn.commit()
            except psycopg2.Error as e:
                connection_error(e, conn)

        for role in roles_added:
            try:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE members
                    SET roles = CONCAT(roles,%s,',')
                    WHERE id = '%s' AND roles NOT LIKE CONCAT('%%',%s,'%%') ;
                """,
                            (role, user_id,role))
                conn.commit()
            except psycopg2.Error as e:
                connection_error(e, conn)

class update_database_name(on_member_update):
    """
    Updates the member nickname in the database after member is updated
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, before, after):
        if before.display_name == after.display_name:
            return
        conn = self.bot.conn
        if not member_exists(conn, after.id):
            insert_member(conn, self.bot, after)
        else:
            try:
                cur = conn.cursor()
                cur.execute("""
                        UPDATE members
                        SET nickname = %s
                        WHERE id = '%s' ;
                    """,
                    (after.display_name, after.id)
                )
                conn.commit()
            except psycopg2.Error as e:
                connection_error(e, conn)   