import json
with open('/tmp/txs.json') as f:
    d = json.load(f)
recs = d['_embedded']['records']
print(f'Found {len(recs)} transactions')
for r in recs:
    h = r['hash']
    c = r['created_at']
    o = r['operation_count']
    s = r['successful']
    print(f'{h} | {c} | ops={o} | succ={s}')
