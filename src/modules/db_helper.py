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
    
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("""
            INSERT INTO {} (id, nickname)
            VALUES (%s, %s) ;
        """)
                    .format(sql.Identifier(table)),
                    (member.id, member.display_name))
        conn.commit()

        refresh_member_in_db(conn, member, bot.roles)
        return SUCCESS
    except psycopg2.Error as e:
        connection_error(e, conn)

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

    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT id FROM {} where id = '%s'").format(sql.Identifier(table)), (id,))
        return cur.fetchone() is not None
    except psycopg2.Error as e:
        connection_error(e, conn)

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

    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT * FROM {} where id = '%s'").format(sql.Identifier(table)), (id,))
        return cur.fetchone()
    except psycopg2.Error as e:
        connection_error(e, conn)

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

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql.SQL("SELECT * FROM {} where id = '%s'").format(sql.Identifier(table)), (id,))
        member = cur.fetchone()
        member_roles= []
        for role in roles:
            if member["roles"] is None:
                return None
            elif str(role) in member["roles"].split(","):
                member_roles.append(role)
        return member_roles
    except psycopg2.Error as e:
        connection_error(e, conn)

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

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql.SQL("SELECT * FROM {} where id = '%s'").format(sql.Identifier(table)), (id,))
        member = cur.fetchone()
        return member["nickname"]
    except psycopg2.Error as e:
        connection_error(e, conn)

def refresh_member_in_db(conn, member, bot_roles, debug = False):
    """
    Refresh a member's database data

    args:
    conn = database connection. Typically bot.conn
    member = member object to refresh
    bot_roles = get from bot.roles in roles refactor
    debug = debug bool from bot.debug
    """
    # Debug Table or Members Table
    table = get_table(debug)
    
    if member_exists(conn, member.id):
        try:
            cur = conn.cursor()
            cur.execute(sql.SQL("""
                    UPDATE {}
                    SET nickname = %s
                    WHERE id = '%s' ;
                """).format(sql.Identifier(table)),
                (member.display_name, member.id)
            )
            conn.commit()
        except psycopg2.Error as e:
            connection_error(e, conn)

        member_roles = [role.id for role in member.roles]
        for role in bot_roles.values():
            if int(role) in member_roles:
                try:
                    cur = conn.cursor()
                    if int(role) != member_roles[-1]:
                        # Comma Separated Roles            
                        cur.execute(sql.SQL("""
                                UPDATE {}
                                SET roles = CONCAT(roles,'%s',',')
                                WHERE id = '%s' ;
                            """).format(sql.Identifier(table)),
                            (int(role), member.id))
                    elif int(role) == member_roles[-1]:
                        # No comma for last value
                        cur.execute(sql.SQL("""
                                UPDATE {}
                                SET roles = CONCAT(roles,'%s','')
                                WHERE id = '%s' ;
                            """).format(sql.Identifier(table)),
                            (int(role), member.id))
                    conn.commit()           
                except psycopg2.Error as e:
                    connection_error(e, conn)

def remove_role(conn, role_id):
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("""
            UPDATE {}
            SET roles = REPLACE(roles,',%s','')
        """).format(sql.Identifier(get_table(debug = False))),
        (int(role_id),))
        conn.commit()
    except psycopg2.Error as e:
        connection_error(e, conn)

# I don't know if this function is necessary anymore with the updated table format. 
def add_role(conn, role_id):
    try:
        cur = conn.cursor()
        cur.execute("""
            ALTER TABLE Members
            ADD COLUMN role_%s bool DEFAULT False;
        """,
        (int(role_id),))
        conn.commit()
    except psycopg2.Error as e:
        connection_error(e, conn)

if __name__ == "__main__":
    import os
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--id')
    parser.add_argument('--delete', action='store_true')
    args = parser.parse_args()
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print(DATABASE_URL)
    if args.delete:
        remove_role(conn, args.id)
    else:
        add_role(conn, args.id)
