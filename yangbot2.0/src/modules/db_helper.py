import psycopg2


def member_exists(conn, id):
    """
    Check if a member exists in the database

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    """
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM Members where id = '%s'", (id,))
        return cur.fetchone() is not None
    except:
        conn.rollback()


def fetch_member(conn, id):
    """
    Return a member from the database as a tuple. Schema can be inferred from config.json

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    """
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Members where id = '%s'", (id,))
        return cur.fetchone()
    except:
        conn.rollback()
