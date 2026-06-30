import sqlite3
conn = sqlite3.connect(r'C:\Users\Doctorsonwheels\zk\doctorlink-health-services\health_services.db')
c = conn.cursor()

# Check stellar_sync_queue
c.execute("SELECT * FROM stellar_sync_queue")
rows = c.fetchall()
cols = [d[0] for d in c.description]
print('=== stellar_sync_queue ===')
for r in rows:
    for col, val in zip(cols, r):
        if val is None:
            val = 'NULL'
        if isinstance(val, str) and len(val) > 80:
            val = val[:80] + '...'
        print(f'  {col}: {val}')
    print()

# Check verifications from June 28
c.execute("SELECT * FROM doctor_verifications WHERE created_at LIKE '2026-06-28%'")
rows = c.fetchall()
print('=== doctor_verifications (Jun 28) ===')
for r in rows:
    for col, val in zip(cols, r):
        if val is None:
            val = 'NULL'
        if isinstance(val, str) and len(val) > 80:
            val = val[:80] + '...'
        print(f'  {col}: {val}')
    print()

# Check vaccinations from June 28
cols2 = [d[0] for d in conn.execute("SELECT * FROM vaccinations").description]
c.execute("SELECT * FROM vaccinations WHERE administered_date LIKE '2026-06-28%'")
rows = c.fetchall()
print('=== vaccinations (Jun 28) ===')
for r in rows:
    for col, val in zip(cols2, r):
        if val is None:
            val = 'NULL'
        if isinstance(val, str) and len(val) > 80:
            val = val[:80] + '...'
        print(f'  {col}: {val}')
    print()

conn.close()
