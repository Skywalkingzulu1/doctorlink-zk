import sqlite3
conn = sqlite3.connect(r'C:\Users\Doctorsonwheels\zk\doctorlink-health-services\health_services.db')
c = conn.cursor()
c.execute("SELECT id, status, error_message, public_signals FROM stellar_sync_queue WHERE id=2")
r = c.fetchone()
print(f'id={r[0]} status={r[1]}')
err = r[2]
if err:
    print(f'error bytes: {err.encode("utf-8", errors="replace")}')
    print(f'error repr: {repr(err)}')
ps = r[3]
if ps:
    print(f'public_signals: {ps}')
conn.close()
