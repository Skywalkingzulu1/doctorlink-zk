import urllib.request, ssl, json

S = "srv-d91p0fsm0tmc73d753p0"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()

env_vars = {
    "STELLAR_NETWORK": "testnet",
    "ZK_VERIFIER_CONTRACT": "CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2",
    "HEALTH_TOKEN_CONTRACT": "CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT",
    "OPENROUTER_MODEL": "google/gemini-2.5-flash-lite",
}

for key, value in env_vars.items():
    req = urllib.request.Request(
        f"https://api.render.com/v1/services/{S}/env-vars/{key}",
        data=json.dumps({"value": value}).encode(),
        headers={"Authorization": f"Bearer {K}", "Content-Type": "application/json"},
        method="PUT",
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        print(f"Set {key}: {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        print(f"Set {key}: HTTP {e.code} - {body}")
