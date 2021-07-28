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

def insert_member(conn, bot, member):
    table = get_table(bot.debug)
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("""
            INSERT INTO {} (id, default_nickname)
            VALUES (%s, %s) ;
        """)
                    .format(sql.Identifier(table)),
                    (member.id, member.display_name))
        conn.commit()
        refresh_member_in_db(conn, member, bot.roles)
        return SUCCESS
    except:
        conn.rollback()
        return FAIL

def member_exists(conn, id, debug):
    """
    Check if a member exists in the database

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    debug = debug bool from bot.debug
    """
    table = get_table(debug)
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT id FROM {} where id = '%s'").format(sql.Identifier(table)), (id,))
        return cur.fetchone() is not None
    except:
        conn.rollback()
        return FAIL


def fetch_member(conn, id, debug):
    """
    Return a member from the database as a tuple. Schema can be inferred from config.json

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    debug = debug bool from bot.debug
    """
    table = get_table(debug)
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT * FROM {} where id = '%s'").format(sql.Identifier(table)), (id,))
        return cur.fetchone()
    except:
        conn.rollback()
        return FAIL

def fetch_member_roles(conn,id,roles,debug):
    """
    Return all the member role objects of a member

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    roles = list of all role ids within the server -- get from bot.roles
    debug = debug bool from bot.debug
    """
    table = get_table(debug)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql.SQL("SELECT * FROM {} where id = '%s'").format(sql.Identifier(table)), (id,))
        member = cur.fetchone()
        member_roles= []
        for role in roles:
            if str(role) in member["roles"].split(","):
                member_roles.append(role)
        return member_roles
    except:
        conn.rollback()
        return FAIL

def fetch_member_nickname(conn,id,debug):
    """
    Return the nickname of the member

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    debug = debug bool from bot.debug
    """
    table = get_table(debug)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql.SQL("SELECT * FROM {} where id = '%s'").format(sql.Identifier(table)), (id,))
        member = cur.fetchone()
        return member["nickname"]
    except:
        conn.rollback()
        return FAIL

def refresh_member_in_db(conn, member, bot_roles,debug):
    """
    Refresh a member's database data

    args:
    conn = database connection. Typically bot.conn
    member = member object to refresh
    bot_roles = get from bot.roles in roles refactor
    debug = debug bool from bot.debug
    """
    table = get_table(debug)
    if member_exists(conn, member.id):
        try:
            cur = conn.cursor()
            cur.execute(sql.SQL("""
                    UPDATE {}
                    SET default_nickname = %s
                    WHERE id = '%s' ;
                """).format(sql.Identifier(table)),
                (member.display_name, member.id)
            )
            conn.commit()
        except:
            conn.rollback()
            return FAIL

        member_roles = [role.id for role in member.roles]
        for role in bot_roles.values():
            if int(role) in member_roles:
                try:
                    cur = conn.cursor()
                    cur.execute(sql.SQL("""
                            UPDATE {}
                            SET roles = CONCAT(roles,'%s'+',')
                            WHERE id = '%s' ;
                        """).format(sql.Identifier(table)),
                        (int(role), member.id)
                    )
                    conn.commit()
                except:
                    conn.rollback()
                    return FAIL

def remove_role(conn, role_id):
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("""
            UPDATE {}
            SET roles = REPLACE(roles,'%s','')
        """).format(sql.Identifier(get_table)),
        (int(role_id),))
        conn.commit()
    except:
        conn.rollback()

def add_role(conn, role_id):
    try:
        cur = conn.cursor()
        cur.execute("""
            ALTER TABLE Members
            ADD COLUMN role_%s bool DEFAULT False;
        """,
        (int(role_id),))
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()

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