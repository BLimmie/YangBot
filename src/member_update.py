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
        for role in roles_deleted:
                cur = conn.cursor()
                db_sql = f"""
                    UPDATE members
                    SET roles = REPLACE(roles,',{role}','')
                    WHERE id = {user_id} ;
                """
                dbfunc_run(db_sql, cur, conn)
                conn.commit()
        for role in roles_added:
                cur = conn.cursor()
                db_sql = f"""
                    UPDATE members
                    SET roles = CONCAT(roles,{role},',')
                    WHERE id = {user_id} AND roles NOT LIKE CONCAT('%%',{role},'%%') ;
                """
                dbfunc_run(db_sql, cur, conn)
                conn.commit()

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
            cur = conn.cursor()
            db_sql = f"""
                    UPDATE members
                    SET nickname = {after.display_name}
                    WHERE id = {after.id} ;
                """
            dbfunc_run(db_sql, cur, conn)
            conn.commit()