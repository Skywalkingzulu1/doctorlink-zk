import urllib.request, ssl, json

S = "srv-d91p0fsm0tmc73d753p0"
D = "dep-d91p3gmq1p3s73cbpg30"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()

# Try the deploy logs endpoint with cursor 0
for cursor in [0, "start"]:
    req = urllib.request.Request(
        f"https://api.render.com/v1/services/{S}/deploys/{D}/logs?cursor={cursor}&direction=forward&limit=50",
        headers={"Authorization": f"Bearer {K}"},
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        data = json.load(resp)
        for entry in data:
            ts = entry.get("timestamp", "")
            text = entry.get("text", "")
            print(ts, text[:200])
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        print(f"cursor={cursor} HTTP {e.code}: {body}")
