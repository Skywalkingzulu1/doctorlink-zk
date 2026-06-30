import sqlite3
conn = sqlite3.connect(r'C:\Users\Doctorsonwheels\zk\doctorlink-health-services\health_services.db')
c = conn.cursor()
c.execute("SELECT id, status, error_message, tx_hash, created_at FROM stellar_sync_queue")
for r in c.fetchall():
    print(f'id={r[0]} status={r[1]} tx_hash={r[3]} created={r[4]}')
    raw = r[2]
    if raw:
        print(f'error_message raw bytes: {raw.encode("utf-8", errors="replace")[:200]}')
        print(f'error_message repr: {repr(raw)[:200]}')
conn.close()
