import json, base64, urllib.request

with open(r'C:\Users\Doctorsonwheels\zk\txs.json') as f:
    d = json.load(f)

print(f'{"#":<4} {"HASH":<68} {"CREATED (UTC)":<22} {"FUNCTION":<22}')
print('=' * 120)

for i, r in enumerate(d['_embedded']['records']):
    h = r['hash']
    created = r['created_at']
    ops_url = r['_links']['operations']['href'].split('{')[0]

    func_name = '(unknown)'
    try:
        resp = urllib.request.urlopen(ops_url, timeout=5)
        od = json.loads(resp.read())
        for op in od['_embedded']['records']:
            params = op.get('parameters', [])
            if len(params) > 1:
                func_b64 = params[1]['value']
                fb = base64.b64decode(func_b64)
                func_name = fb.decode('utf-8', errors='replace').strip('\x00').strip()
                if func_name:
                    break
    except Exception:
        func_name = '(fetch error)'

    print(f'{i+1:<4} {h:<68} {created:<22} {func_name:<22}')
