import sqlite3, json
from datetime import datetime

conn = sqlite3.connect(r'C:\Users\Doctorsonwheels\zk\doctorlink-health-services\health_services.db')
c = conn.cursor()

# Map proof hashes to tx hashes
updates = {
    'f5c85e2a41824ce34d064e6b00181fc14b7db5534033696e6b48e26d60f8b11f': '4623e73b2b55cb1a3a39638b7374e16b6b808f6ff9653b8d5e30e78205fcc0b3',
    '11e16d19ca6be12819c1dda51c8d65a3be461b0398625ca3badd1a163aff2a54': '9f24f96ffe5a84f60e9078afd4941e97f1cae1ee67704564566d6cdc9644f5b0',
}

for ph, txh in updates.items():
    c.execute(
        "UPDATE stellar_sync_queue SET status='synced', tx_hash=?, synced_at=? WHERE proof_hash=?",
        (txh, datetime.utcnow(), ph)
    )
    print(f'Updated queue for {ph[:20]}... -> {txh[:20]}... ({c.rowcount} row)')

    # Also update linked doctor_verification
    if ph == 'f5c85e2a41824ce34d064e6b00181fc14b7db5534033696e6b48e26d60f8b11f':
        c.execute("UPDATE doctor_verifications SET status='verified' WHERE zk_proof_hash=?", (ph,))
    elif ph == '11e16d19ca6be12819c1dda51c8d65a3be461b0398625ca3badd1a163aff2a54':
        c.execute("UPDATE doctor_verifications SET status='verified' WHERE zk_proof_hash=?", (ph,))
    print(f'Updated verification for {ph[:20]}... ({c.rowcount} row)')

conn.commit()
conn.close()
print('Done')
