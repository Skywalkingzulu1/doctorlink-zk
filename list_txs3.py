import json, requests

with open(r'C:\Users\Doctorsonwheels\zk\txs.json') as f:
    d = json.load(f)

recs = d['_embedded']['records']
print(f'{"#":<4} {"HASH":<70} {"CREATED":<22} {"OPS":<4}')
print('-' * 105)

contract_names = {
    'CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2': '(verifier)',
    'CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT': '(token)',
}

for i, r in enumerate(recs):
    h = r['hash']
    c = r['created_at']
    o = r['operation_count']
    print(f'{i+1:<4} {h:<70} {c:<22} {o:<4}')
