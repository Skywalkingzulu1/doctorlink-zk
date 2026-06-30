import urllib.request, ssl, json

S = "srv-d91p0fsm0tmc73d753p0"
D = "dep-d91p3gmq1p3s73cbpg30"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()

# Try cursor-based log endpoint
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{S}/deploys/{D}/cursor",
    headers={"Authorization": f"Bearer {K}"},
)
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    print(resp.read().decode()[:3000])
except urllib.error.HTTPError as e:
    print(f"cursor HTTP {e.code}: {e.read().decode()[:300]}")

# Try log endpoint
req2 = urllib.request.Request(
    f"https://api.render.com/v1/services/{S}/deploys/{D}/events",
    headers={"Authorization": f"Bearer {K}"},
)
try:
    resp2 = urllib.request.urlopen(req2, context=ctx, timeout=15)
    print(resp2.read().decode()[:3000])
except urllib.error.HTTPError as e:
    print(f"events HTTP {e.code}: {e.read().decode()[:300]}")

# Try service env vars
req3 = urllib.request.Request(
    f"https://api.render.com/v1/services/{S}/env-vars",
    headers={"Authorization": f"Bearer {K}"},
)
try:
    resp3 = urllib.request.urlopen(req3, context=ctx, timeout=15)
    print("Env vars:", json.load(resp3))
except urllib.error.HTTPError as e:
    print(f"env HTTP {e.code}: {e.read().decode()[:300]}")
