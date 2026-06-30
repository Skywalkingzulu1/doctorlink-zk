import urllib.request, ssl, json
from datetime import datetime, timezone

K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
owner = "tea-cvmolmp5pdvs73e388g0"
resource = "srv-d91p0fsm0tmc73d753p0"
ctx = ssl.create_default_context()
now = datetime.now(timezone.utc)
hour_ago = int(now.timestamp()) - 3600
end = now.strftime("%Y-%m-%dT%H:%M:%SZ")
start = datetime.fromtimestamp(hour_ago, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

url = f"https://api.render.com/v1/logs?ownerId={owner}&resource={resource}&direction=backward&limit=5&startTime={start}&endTime={end}"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {K}"})
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    data = json.load(resp)
    print(json.dumps(data, indent=2)[:3000])
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:500]}")

# Also try without startTime/endTime to see current
url2 = f"https://api.render.com/v1/logs?ownerId={owner}&resource={resource}&direction=backward&limit=5"
req2 = urllib.request.Request(url2, headers={"Authorization": f"Bearer {K}"})
try:
    resp2 = urllib.request.urlopen(req2, context=ctx, timeout=15)
    data2 = json.load(resp2)
    print("\n=== No time filters ===")
    print(json.dumps(data2, indent=2)[:3000])
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:500]}")
