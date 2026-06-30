import urllib.request
import urllib.error
import ssl
import json

service_id = "srv-d91p0fsm0tmc73d753p0"
api_key = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"

ctx = ssl.create_default_context()
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{service_id}/deploys",
    data=b"{}",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    method="POST",
)
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    result = json.load(resp)
    print("Deploy ID:", result.get("id"))
    print("Status:", result.get("status"))
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:500]}")
