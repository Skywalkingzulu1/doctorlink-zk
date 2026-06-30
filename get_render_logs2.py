import urllib.request, ssl, json, time
from datetime import datetime, timezone

K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
owner = "tea-cvmolmp5pdvs73e388g0"
resource = "srv-d91p0fsm0tmc73d753p0"
ctx = ssl.create_default_context()
now = datetime.now(timezone.utc)
hour_ago = int(now.timestamp()) - 3600

# Use ISO 8601 format
end = now.strftime("%Y-%m-%dT%H:%M:%SZ")
start = datetime.fromtimestamp(hour_ago, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

base = f"https://api.render.com/v1/logs?ownerId={owner}&resource={resource}&direction=backward&limit=30&startTime={start}&endTime={end}"

for log_type in ["build", "app", ""]:
    url = base + (f"&type={log_type}" if log_type else "")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {K}"})
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        data = json.load(resp)
        logs = data.get("logs", [])
        print(f"\n=== {log_type or 'all'} logs ({len(logs)} entries) ===")
        for log in logs[:30]:
            ts = log.get("timestamp", "")
            text = log.get("text", "")
            instance = log.get("instance", "")
            if text:
                print(f"[{ts}] {instance} {text[:300]}")
            elif log.get("message"):
                print(f"[{ts}] {log['message'][:300]}")
        if not logs:
            print("(no logs)")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        print(f"\n=== {log_type or 'all'} logs HTTP {e.code} ===")
        print(body)
