import json, base64, urllib.request

with open(r'C:\Users\Doctorsonwheels\zk\txs_new.json') as f:
    d = json.load(f)

recs = d['_embedded']['records']
print(f'Found {len(recs)} most recent transactions')

for r in recs:
    h = r['hash']
    created = r['created_at']
    ops_url = r['_links']['operations']['href'].split('{')[0]
    func_name = '(?)'
    try:
        resp = urllib.request.urlopen(ops_url, timeout=5)
        od = json.loads(resp.read())
        for op in od['_embedded']['records']:
            params = op.get('parameters', [])
            if len(params) > 1:
                fb = base64.b64decode(params[1]['value'])
                func_name = fb.decode('utf-8', errors='replace').strip('\x00').strip()
                if func_name:
                    break
    except Exception:
        func_name = '(fetch err)'
    
    succ = 'OK' if r['successful'] else 'FAIL'
    print(f'{created} | {func_name:<22} | {succ} | {h[:20]}...')
