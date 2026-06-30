import urllib.request
import urllib.error
import ssl
import json

service_id = "srv-d91p0fsm0tmc73d753p0"
deploy_id = "dep-d91p3gmq1p3s73cbpg30"
api_key = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"

ctx = ssl.create_default_context()
for i in range(12):
    import time
    time.sleep(10)
    req = urllib.request.Request(
        f"https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=30)
        result = json.load(resp)
        status = result.get("status", "unknown")
        print(f"[{i*10}s] Status: {status}")
        if status in ("live", "build_failed", "deploy_failed", "canceled"):
            print("Finished at:", result.get("finishedAt", "N/A"))
            print("Commit:", result.get("commit", {}).get("message", "N/A"))
            break
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:200]}")
        break
