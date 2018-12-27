import psycopg2
import os

DATABASE_URL = os.environ['YANGBOT_DB']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

cur.execute("select * from members")
print(cur.fetchall())