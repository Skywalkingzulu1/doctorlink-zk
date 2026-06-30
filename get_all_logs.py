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

url = f"https://api.render.com/v1/logs?ownerId={owner}&resource={resource}&direction=backward&limit=100&startTime={start}&endTime={end}"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {K}"})
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    data = json.load(resp)
    logs = data.get("logs", [])
    print(f"=== ALL logs ({len(logs)} entries) ===", flush=True)
    for log in logs:
        ts = log.get("timestamp", "")
        text = log.get("text", "")
        ltype = log.get("type", "")
        instance = log.get("instance", "")
        out = f"[{ts}] type={ltype} inst={instance} {text[:500]}" if text else f"[{ts}] type={ltype} inst={instance} (no text)"
        sys.stdout.buffer.write(out.encode("utf-8", errors="replace")[:500] + b"\n")
    if not logs:
        print("(no logs)")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")[:1000]
    print(f"HTTP {e.code}: {body}")
