import urllib.request, ssl, json, sys
from datetime import datetime, timezone

K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
owner = "tea-cvmolmp5pdvs73e388g0"
resource = "srv-d91p0fsm0tmc73d753p0"
ctx = ssl.create_default_context()
now = datetime.now(timezone.utc)
hour_ago = int(now.timestamp()) - 3600

end = now.strftime("%Y-%m-%dT%H:%M:%SZ")
start = datetime.fromtimestamp(hour_ago, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

url = f"https://api.render.com/v1/logs?ownerId={owner}&resource={resource}&direction=backward&limit=50&startTime={start}&endTime={end}&type=app"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {K}"})
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    data = json.load(resp)
    logs = data.get("logs", [])
    print(f"=== app logs ({len(logs)} entries) ===", flush=True)
    for log in logs[:50]:
        ts = log.get("timestamp", "")
        text = log.get("text", "")
        instance = log.get("instance", "")
        out = f"[{ts}] {instance} {text}" if text else f"[{ts}] (no text)"
        sys.stdout.buffer.write(out.encode("utf-8", errors="replace")[:500] + b"\n")
    if not logs:
        print("(no app logs)")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")[:500]
    print(f"HTTP {e.code}: {body}")
