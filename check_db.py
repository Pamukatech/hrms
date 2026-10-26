import sqlite3
conn = sqlite3.connect('hrms.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
for r in cur.fetchall():
    print(r[0])
conn.close()
