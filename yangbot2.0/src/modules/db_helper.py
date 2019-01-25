import psycopg2

def member_exists(conn, id):
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM Members where id = '%s'", (id,))
        return cur.fetchone() is not None
    except:
        conn.rollback()

def fetch_member(conn, id):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Members where id = '%s'", (id,))
        return cur.fetchone()
    except:
        conn.rollback()