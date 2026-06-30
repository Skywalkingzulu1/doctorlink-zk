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

# Get ALL recent logs to see if stellar CLI errors appear
url = f"https://api.render.com/v1/logs?ownerId={owner}&resource={resource}&direction=backward&limit=100&startTime={start}&endTime={end}"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {K}"})
resp = urllib.request.urlopen(req, context=ctx, timeout=15)
data = json.load(resp)
for log in data.get("logs", []):
    msg = log.get("message", "")
    ts = log.get("timestamp", "")
    if msg and ("stellar" in msg.lower() or "error" in msg.lower() or "ProofError" in msg or "traceback" in msg.lower() or "stderr" in msg.lower()):
        sys.stdout.buffer.write(f"[{ts}] {msg[:500]}\n".encode("utf-8", errors="replace"))
