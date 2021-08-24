import psycopg2
import psycopg2.extras
from psycopg2 import sql

SUCCESS = 0
FAIL = None

def get_table(debug):
    if debug:
        return "test"
    else:
        return "members"

def connection_error(e, conn):
    if e is ConnectionError:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            return FAIL
    else:
        conn.rollback()
        return FAIL

def dbfunc_run(sql, cur, conn, tries = 2):
    for i in range(tries):
        try:
            cur.execute(sql)
            break
        except psycopg2.Error as e:
            if e is ConnectionError:
                DATABASE_URL = os.environ['DATABASE_URL']
                conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                continue
            else:
                conn.rollback()
                return FAIL
    return cur


def all_members(conn, client, bot):
    guild = client.get_guild(bot.config["server_id"]) # UCSB Server ID
    print(f"{guild}")
    memberList = guild.members
    cur = conn.cursor()
    for member in memberList:
        print(member.display_name)
        member_roles = []
        for role in member.roles:
            if role.id in bot.roles.values():
                member_roles.append(role.id)

        if not member_exists(conn, member.id, debug = False):
            if bot.roles.get('Gaucho') in member_roles: 
                # str(member_roles)[1:-1]
                if "'" in member.display_name: 
                    # Helps to insert display names containing apostrophes
                    cur.execute(f"""INSERT INTO Members
                            VALUES ('{member.id}','{member.display_name.replace("'", "''")}', '{','.join(map(str, member_roles))}')
                            """)
                else: 
                    cur.execute(f"""INSERT INTO Members
                            VALUES ('{member.id}','{member.display_name}', '{','.join(map(str, member_roles))}')
                            """)       
                conn.commit()

def insert_member(conn, bot, member):
    # Debug Table or Members Table
    table = get_table(bot.debug)
    cur = conn.cursor()
    db_sql = f"""INSERT INTO {table} (id, nickname) VALUES ({member.id}, '{member.display_name}')"""
    dbfunc_run(db_sql, cur, conn)
    conn.commit()

    refresh_member_in_db(conn, member, bot.roles)
    return SUCCESS

def member_exists(conn, id, debug = False):
    """
    Check if a member exists in the database

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    debug = debug bool from bot.debug
    """
    # Debug Table or Members Table
    table = get_table(debug)
    cur = conn.cursor()
    db_sql = f"""SELECT id FROM {table} where id = {id}"""

    dbfunc_run(db_sql, cur, conn)
    return cur.fetchone() is not None

def fetch_member(conn, id, debug = False):
    """
    Return a member from the database as a tuple. Schema can be inferred from YangBot class roles

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    debug = debug bool from bot.debug
    """
    # Debug Table or Members Table
    table = get_table(debug)
    cur = conn.cursor()
    db_sql = f"""SELECT * FROM {table} where id = {id}"""
    cur = dbfunc_run(db_sql, cur, conn)
    return cur.fetchone()

def fetch_member_roles(conn, id, roles, debug = False):
    """
    Return all the member role objects of a member

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    roles = list of all role ids within the server -- get from bot.roles
    debug = debug bool from bot.debug
    """
    # Debug Table or Members Table
    table = get_table(debug)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    db_sql = f"""SELECT * FROM {table} where id = {id}"""
    cur = dbfunc_run(db_sql, cur, conn)
    member = cur.fetchone()
    member_roles= []
    for role in roles:
        if member["roles"] is None:
            return None
        elif str(role) in member["roles"].split(","):
            member_roles.append(role)
    return member_roles

def fetch_member_nickname(conn, id, debug = False):
    """
    Return the nickname of the member

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    debug = debug bool from bot.debug
    """
    # Debug Table or Members Table
    table = get_table(debug)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    db_sql = f"""SELECT * FROM {table} where id = {id}"""
    cur = dbfunc_run(db_sql, cur, conn)
    member = cur.fetchone()
    return member["nickname"]

def refresh_member_in_db(conn, member, bot_roles, debug = False):
    """
    Refresh a member's database data

    args:
    conn = database connection. Typically bot.conn
    member = member object to refresh
    bot_roles = get from bot.roles (dictionary {name, id})
    debug = debug bool from bot.debug
    """
    # Debug Table or Members Table
    table = get_table(debug)
    
    if member_exists(conn, member.id):
            cur = conn.cursor()
            db_sql = f"""UPDATE {table} SET nickname = '{member.display_name}' WHERE id = {member.id} ;"""
            dbfunc_run(db_sql, cur, conn)
            conn.commit()

    member_roles = [role.id for role in member.roles]
    for role in bot_roles.values():
        if int(role) in member_roles:
            cur = conn.cursor()
            if int(role) != member_roles[-1]:
                # Comma Separated Roles            
                db_sql = f"""UPDATE {table} SET roles = CONCAT(roles,{int(role)},',') WHERE id = {member.id} ;"""
                dbfunc_run(db_sql, cur, conn)
            elif int(role) == member_roles[-1]:
                # No comma for last value
                db_sql = f"""UPDATE {table} SET roles = CONCAT(roles,{int(role)},'') WHERE id = {member.id} ;"""
                dbfunc_run(db_sql, cur, conn)
            conn.commit()           

# def remove_role(conn, role_id):
#     cur = conn.cursor()
#     # db_sql = (sql.SQL("""
#     #     UPDATE {}
#     #     SET roles = REPLACE(roles,',%s','')
#     # """).format(sql.Identifier(get_table(debug = False))),
#     # (int(role_id),))
#     db_sql = f"""UPDATE {get_table(debug = False)} SET roles = REPLACE(roles, ',{int(role_id)}','')"""
#     dbfunc_run(db_sql, cur, conn)
#     conn.commit()

# def add_role(conn, role_id):
#     cur = conn.cursor()
#     # cur.execute(f"""UPDATE '{get_table(debug = False)}'
#     #                 SET roles = CONCAT(roles, '{role_id}')""")
#     db_sql = f"""UPDATE '{get_table(debug = False)}' SET roles = CONCAT(roles, ',{role_id}')"""
#     dbfunc_run(db_sql, cur, conn)
#     conn.commit()

if __name__ == "__main__":
    import os
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--id')
    # parser.add_argument('--delete', action='store_true')
    # args = parser.parse_args()
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print(DATABASE_URL)
    # if args.delete:
    #     remove_role(conn, args.id)
    # else:
    #     add_role(conn, args.id)
