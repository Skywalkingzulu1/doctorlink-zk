import urllib.request, ssl, json

S = "srv-d91p0fsm0tmc73d753p0"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()

req = urllib.request.Request(
    f"https://api.render.com/v1/services/{S}",
    headers={"Authorization": f"Bearer {K}"},
)
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    r = json.load(resp)
    print("Service name:", r.get("service", {}).get("name"))
    print("Service ID:", r.get("service", {}).get("id"))
    print("Suspend state:", r.get("service", {}).get("suspendState"))
    print("Auto deploy:", r.get("service", {}).get("autoDeploy"))
    print("Last deploy:", r.get("lastDeploy", {}).get("id"))
    print("Service details:", json.dumps(r, indent=2)[:2000])
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:1000]}")
