import json, base64, urllib.request, sqlite3

# Check DB
conn = sqlite3.connect(r'C:\Users\Doctorsonwheels\zk\doctorlink-health-services\health_services.db')
c = conn.cursor()
c.execute("SELECT * FROM stellar_sync_queue")
rows = c.fetchall()
cols = [d[0] for d in c.description]
print('=== Sync Queue ===')
for r in rows:
    for col, val in zip(cols, r):
        if val is None: val = 'NULL'
        s = str(val)
        if len(s) > 100: s = s[:100] + '...'
        s = s.encode('latin1', errors='replace').decode('latin1')
        print(f'  {col}: {s}')
    print()

c.execute("SELECT * FROM doctor_verifications ORDER BY id DESC")
rows = c.fetchall()
cols2 = [d[0] for d in c.description]
print('=== Doctor Verifications ===')
for r in rows:
    for col, val in zip(cols2, r):
        if val is None: val = 'NULL'
        s = str(val)
        if len(s) > 100: s = s[:100] + '...'
        s = s.encode('latin1', errors='replace').decode('latin1')
        print(f'  {col}: {s}')
    print()
conn.close()

# Check Stellar
print('=== Stellar Transactions (newest) ===')
with open(r'C:\Users\Doctorsonwheels\zk\txs_new.json') as f:
    d = json.load(f)

for r in d['_embedded']['records'][:3]:
    h = r['hash']
    created = r['created_at']
    ops_url = r['_links']['operations']['href'].split('{')[0]
    try:
        resp = urllib.request.urlopen(ops_url, timeout=5)
        od = json.loads(resp.read())
        for op in od['_embedded']['records']:
            params = op.get('parameters', [])
            if len(params) > 1:
                fb = base64.b64decode(params[1]['value'])
                fn = fb.decode('utf-8', errors='replace').strip('\x00').strip()
                print(f'{created} | {fn} | {h[:20]}...')
    except Exception as e:
        print(f'{created} | (err: {e}) | {h[:20]}...')
