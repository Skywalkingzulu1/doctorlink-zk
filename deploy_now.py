import urllib.request, ssl, json, sys
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()
body = json.dumps({"clearBuildCache": True}).encode()
req = urllib.request.Request(
    "https://api.render.com/v1/services/srv-d91p0fsm0tmc73d753p0/deploys",
    data=body,
    headers={"Authorization": f"Bearer {K}", "Content-Type": "application/json"},
    method="POST",
)
r = json.load(urllib.request.urlopen(req, context=ctx, timeout=15))
print(r.get("id"))
