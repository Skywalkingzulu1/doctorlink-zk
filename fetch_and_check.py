import json, base64, urllib.request, sqlite3

# Fetch Stellar txs
url = 'https://horizon-testnet.stellar.org/accounts/GCLJMFKL3CFWJKZS6UM5BF5KWG67UMVL7TCSDAM4L3JIFWNMV3LSIFL7/transactions?limit=10&order=desc'
resp = urllib.request.urlopen(url, timeout=15)
d = json.loads(resp.read())

recs = d['_embedded']['records']
print(f'\n=== Stellar Transactions ({len(recs)} most recent) ===')
print(f'{"#":<3} {"HASH":<68} {"CREATED":<22} {"FUNCTION":<22}')
print('-' * 120)
for i, r in enumerate(recs):
    h = r['hash']
    created = r['created_at']
    ops_url = r['_links']['operations']['href'].split('{')[0]
    func_name = '(?)'
    try:
        resp2 = urllib.request.urlopen(ops_url, timeout=5)
        od = json.loads(resp2.read())
        for op in od['_embedded']['records']:
            params = op.get('parameters', [])
            if len(params) > 1:
                fb = base64.b64decode(params[1]['value'])
                func_name = fb.decode('utf-8', errors='replace').strip('\x00').strip()
                if func_name:
                    break
    except Exception:
        func_name = '(err)'
    succ = 'OK' if r['successful'] else 'FAIL'
    print(f'{i+1:<3} {h:<68} {created:<22} {func_name:<22} {succ}')

# Check DB
conn = sqlite3.connect(r'C:\Users\Doctorsonwheels\zk\doctorlink-health-services\health_services.db')
c = conn.cursor()

c.execute("SELECT * FROM stellar_sync_queue ORDER BY id DESC")
rows = c.fetchall()
cols = [d[0] for d in c.description]
print(f'\n=== Sync Queue ({len(rows)} rows) ===')
for r in rows:
    for col, val in zip(cols, r):
        if val is None: val = 'NULL'
        s = str(val)
        if len(s) > 80: s = s[:80] + '...'
        try:
            print(f'  {col}: {s}')
        except:
            print(f'  {col}: <encoding err>')
    print()

c.execute("SELECT * FROM doctor_verifications ORDER BY id DESC")
rows = c.fetchall()
cols2 = [d[0] for d in c.description]
print(f'\n=== Doctor Verifications ({len(rows)} rows) ===')
for r in rows:
    for col, val in zip(cols2, r):
        if val is None: val = 'NULL'
        s = str(val)
        if len(s) > 100: s = s[:100] + '...'
        try:
            print(f'  {col}: {s}')
        except:
            print(f'  {col}: <encoding err>')
    print()

c.execute("SELECT * FROM verifications ORDER BY id DESC" if any('verifications' in str(t) for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()) else "SELECT 1 WHERE 0")
try:
    rows = c.fetchall()
    if rows:
        cols3 = [d[0] for d in c.description]
        print(f'=== Verifications table ({len(rows)} rows) ===')
        for r in rows:
            for col, val in zip(cols3, r):
                print(f'  {col}: {val}')
            print()
except:
    print('(no verifications table)')

conn.close()
