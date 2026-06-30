import sqlite3
conn = sqlite3.connect(r'C:\Users\Doctorsonwheels\zk\doctorlink-health-services\health_services.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print('Tables:', tables)
for tbl in tables:
    try:
        c.execute(f'SELECT * FROM {tbl}')
        rows = c.fetchall()
        cols = [d[0] for d in c.description]
        print(f'\n=== {tbl} ({len(rows)} rows) ===')
        print('cols:', cols)
        for r in rows:
            print(r)
    except Exception as e:
        print(f'{tbl}: {e}')
conn.close()
