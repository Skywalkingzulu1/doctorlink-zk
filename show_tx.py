import json

# Map of known contract IDs
contracts = {
    'CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2': 'verifier',
    'CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT': 'token',
}

with open(r'C:\Users\Doctorsonwheels\zk\txs.json') as f:
    d = json.load(f)

print(f'{"#":<3} {"HASH":<68} {"CREATED":<22} {"TYPE":<22}')
print('-' * 120)

for i, r in enumerate(d['_embedded']['records']):
    h = r['hash']
    c = r['created_at']
    o = r['operation_count']

    # Try to fetch operations to identify
    ops_url = r['_links']['operations']['href'].split('{')[0]
    import urllib.request
    try:
        resp = urllib.request.urlopen(ops_url, timeout=5)
        od = json.loads(resp.read())
        for op in od['_embedded']['records']:
            body = op.get('body', {}) or {}
            cid = body.get('contract_id', body.get('contractId', ''))
            func = body.get('function', body.get('function_name', ''))
            name = body.get('name', '')
            args = body.get('args', body.get('parameters', []))
            sym_args = [a.get('value','') for a in (args or []) if isinstance(a, dict) and a.get('type') == 'Sym']
            fn_name = sym_args[0] if sym_args else func
            prefix = contracts.get(cid, '') if cid else ''
            label = f'{prefix}.{fn_name}' if prefix and fn_name else (fn_name or 'contract_call')
            print(f'{i+1:<3} {h:<68} {c:<22} {label:<22}')
    except Exception as e:
        print(f'{i+1:<3} {h:<68} {c:<22} (unknown)')
