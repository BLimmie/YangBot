import os
import psycopg2

DATABASE_URL = os.environ['YANGBOT_DB']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

cur = conn.cursor()

cur.execute("""Drop table Members""")

cur.execute("""
    CREATE TABLE Members (
        id bigint PRIMARY KEY NOT NULL,
        nickname VARCHAR(32) NOT NULL,
        roles VARCHAR(255) NOT NULL
    );
    """)

conn.commit()