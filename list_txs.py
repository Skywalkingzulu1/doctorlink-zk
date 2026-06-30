import json
with open(r'C:\Users\Doctorsonwheels\zk\txs.json') as f:
    d = json.load(f)
recs = d['_embedded']['records']
print(f'Found {len(recs)} transactions')
for r in recs:
    print(f"{r['hash']} | {r['created_at']} | ops={r['operation_count']} | succ={r['successful']}")
