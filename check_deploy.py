import json
import urllib.request
import urllib.error
import ssl

service_id = "srv-d91p0fsm0tmc73d753p0"
deploy_id = "dep-d91p0gcm0tmc73d7549g"
api_key = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"

ctx = ssl.create_default_context()

# Check the deploy
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}",
    headers={"Authorization": f"Bearer {api_key}"},
)
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    result = json.load(resp)
    print("Status:", result.get("status"))
    print("Finished at:", result.get("finishedAt"))
    print("Commit:", result.get("commit", {}).get("message", "N/A")[:100])
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:500]}")
