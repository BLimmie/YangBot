import psycopg2
from src.modules.db_helper import member_exists, insert_member, connection_error, dbfunc_run
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
        def db_action1():
                cur = conn.cursor()
                cur.execute("""
                    UPDATE members
                    SET roles = REPLACE(roles,',%s','')
                    WHERE id = '%s' ;
                """,
                            (role, user_id))
                conn.commit()
        for role in roles_deleted:
            dbfunc_run(db_action1)
        def db_action2():
                cur = conn.cursor()
                cur.execute("""
                    UPDATE members
                    SET roles = CONCAT(roles,%s,',')
                    WHERE id = '%s' AND roles NOT LIKE CONCAT('%%',%s,'%%') ;
                """,
                            (role, user_id,role))
                conn.commit()
        for role in roles_added:
            dbfunc_run(db_action2)

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
        def db_action():
            cur = conn.cursor()
            cur.execute("""
                    UPDATE members
                    SET nickname = %s
                    WHERE id = '%s' ;
                """,
                (after.display_name, after.id)
            )
            conn.commit()
        if not member_exists(conn, after.id):
            insert_member(conn, self.bot, after)
        else:
            dbfunc_run(db_action)