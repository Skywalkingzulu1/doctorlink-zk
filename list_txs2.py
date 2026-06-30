import json
with open(r'C:\Users\Doctorsonwheels\zk\txs.json') as f:
    d = json.load(f)
recs = d['_embedded']['records']
print(f'{"HASH":<70} {"CREATED":<22} {"TYPE":<20} {"OPS":<4} {"SUCC":<6}')
print('-' * 125)
for r in recs:
    h = r['hash']
    c = r['created_at']
    o = r['operation_count']
    s = r['successful']
    memo = r.get('memo', '')
    memo_type = r.get('memo_type', 'none')
    tx_type = memo if memo and memo_type != 'none' else '(contract call)' if o == 1 else '(unknown)'
    print(f'{h:<70} {c:<22} {str(tx_type):<20} {o:<4} {str(s):<6}')
