import json, requests

with open(r'C:\Users\Doctorsonwheels\zk\txs.json') as f:
    d = json.load(f)

# Get operations for the first 6 most recent
for r in d['_embedded']['records'][:6]:
    h = r['hash']
    created = r['created_at']
    ops_url = r['_links']['operations']['href'].split('{')[0]
    try:
        od = requests.get(ops_url + '?limit=1', timeout=10).json()
        recs = od['_embedded']['records']
        for op in recs:
            op_type = op.get('type', '?')
            body = op.get('body', {}) or {}
            func = body.get('function', '?') if isinstance(body, dict) else '?'
            print(f'{h[:16]}... | {created} | {op_type} | {json.dumps(body)[:100]}')
    except Exception as e:
        print(f'{h[:16]}... | {created} | ERROR: {e}')
