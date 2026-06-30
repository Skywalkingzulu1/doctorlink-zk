import urllib.request, ssl, json

S = "srv-d91p0fsm0tmc73d753p0"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()

env_vars = [
    {"key": "STELLAR_NETWORK", "value": "testnet"},
    {"key": "ZK_VERIFIER_CONTRACT", "value": "CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2"},
    {"key": "HEALTH_TOKEN_CONTRACT", "value": "CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT"},
    {"key": "SECRET_KEY", "value": "doclink-render-secret-key-2026"},
]

for ev in env_vars:
    body = json.dumps(ev).encode()
    req = urllib.request.Request(
        f"https://api.render.com/v1/services/{S}/env-vars",
        data=body,
        headers={"Authorization": f"Bearer {K}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        print(f"Set {ev['key']}: {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        print(f"Set {ev['key']}: HTTP {e.code} - {body}")
