import json

files = [
    ('tx_cb7.json', 'cb704ba8'),
    ('tx_75e.json', '75e66e03'),
    ('tx_f90.json', 'f902ef3a'),
]

for fn, prefix in files:
    d = json.load(open(r'C:\Users\Doctorsonwheels\zk\\' + fn))
    for op in d['_embedded']['records']:
        body = op.get('body', {}) or {}
        cid = body.get('contract_id', body.get('contractId', ''))
        args = body.get('args', body.get('parameters', []))
        sym_val = ''
        if args and isinstance(args, list):
            for a in args:
                if isinstance(a, dict) and a.get('type') == 'Sym':
                    sym_val = a.get('value', '')
                    break
        print(f'{prefix}... | cid={cid[:20]}... | func={sym_val}')
