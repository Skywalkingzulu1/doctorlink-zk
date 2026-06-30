import sqlite3, sys

def safe(val):
    if val is None:
        return 'NULL'
    s = str(val)
    if len(s) > 200:
        s = s[:200] + '...'
    # replace non-latin1 chars
    s = s.encode('latin1', errors='replace').decode('latin1')
    return s

conn = sqlite3.connect(r'C:\Users\Doctorsonwheels\zk\doctorlink-health-services\health_services.db')
c = conn.cursor()

tables = ['patients', 'doctors', 'appointments', 'vaccinations', 'contraceptive_records', 'doctor_verifications', 'stellar_sync_queue']
for tbl in tables:
    c.execute(f"SELECT * FROM {tbl}")
    rows = c.fetchall()
    cols = [d[0] for d in c.description]
    print(f'\n=== {tbl} ({len(rows)} rows) ===')
    for r in rows:
        for col, val in zip(cols, r):
            sv = safe(val)
            if sv:
                print(f'  {col}: {sv}')
        print('---')

conn.close()
