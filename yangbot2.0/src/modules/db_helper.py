import psycopg2


SUCCESS = 0
FAIL = None

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
        return FAIL


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
        return FAIL


def refresh_member_in_db(conn, member, config_roles):
    """
    Refresh a member's database data

    args:
    conn = database connection. Typically bot.conn
    member = member object to refresh
    """
    if member_exists(conn, member.id):
        print(config_roles)
        print("Member found")
        try:
            cur = conn.cursor()
            cur.execute("""
                    UPDATE Members
                    SET default_nickname = %s
                    WHERE id = '%s' ;
                """, 
                (member.display_name, member.id)
            )
            conn.commit()
        except:
            conn.rollback()
            return FAIL
        
        member_roles = [role.id for role in member.roles]
        for role in config_roles.values():
            if int(role) in member_roles:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                            UPDATE Members
                            SET role_%s = True
                            WHERE id = '%s' ;
                        """, 
                        (int(role), member.id)
                    )
                    conn.commit()
                    print(int(role), "True")
                except:
                    conn.rollback()
                    return FAIL
            else:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                            UPDATE Members
                            SET role_%s = False
                            WHERE id = '%s' ;
                        """, 
                        (int(role), member.id)
                    )
                    conn.commit()
                    print(int(role), "False")
                except:
                    conn.rollback()
                    return FAIL