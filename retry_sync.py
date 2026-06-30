import sqlite3, json
conn = sqlite3.connect(r'C:\Users\Doctorsonwheels\zk\doctorlink-health-services\health_services.db')
c = conn.cursor()

# Reset failed items to pending
c.execute("UPDATE stellar_sync_queue SET status='pending', error_message=NULL WHERE status='failed'")
print(f'Reset {c.rowcount} items to pending')
conn.commit()

# Check current queue
c.execute("SELECT id, entity_type, proof_hash, status FROM stellar_sync_queue")
for r in c.fetchall():
    print(f'  id={r[0]} type={r[1]} hash={r[2][:20]}... status={r[3]}')

conn.close()
