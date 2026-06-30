import json, base64

with open('/tmp/txs2.json') as f:
    d = json.load(f)

recs = [r for r in d['_embedded']['records'] if r['created_at'].startswith('2026-06-28')]
print(f'Found {len(recs)} transactions on 2026-06-28')
print()
print(f'{"#":<4} {"HASH":<68} {"TIME":<22} {"FUNCTION":<22}')
print('=' * 120)

for i, r in enumerate(recs):
    h = r['hash']
    created = r['created_at']
    operations_url = r['_links']['operations']['href'].split('{')[0]

    import urllib.request
    func_name = '(unknown)'
    try:
        resp = urllib.request.urlopen(operations_url, timeout=5)
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
        func_name = '(?)'

    print(f'{i+1:<4} {h:<68} {created:<22} {func_name:<22}')
