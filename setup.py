import os
import psycopg2
import json

config = json.load(open('config.json'))

roles = config["roles"]
DATABASE_URL = os.environ['YANGBOT_DB']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

cur.execute("""Drop table Members""")

cur.execute("""
    CREATE TABLE Members (
        id VARCHAR(20) PRIMARY KEY,
        default_nickname TEXT NOT NULL
    );
    """)

conn.commit()

for _, role in roles.items():
    cur.execute("""
    ALTER TABLE Members
    ADD COLUMN role_%s bool DEFAULT False;
    """,
                (role,))

conn.commit()
