import urllib.request
import urllib.error
import ssl

service_id = "srv-d91p0fsm0tmc73d753p0"
deploy_id = "dep-d91p0gcm0tmc73d7549g"
api_key = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"

ctx = ssl.create_default_context()

# Try the deploy log cursor endpoint
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}/log?cursor=0&direction=forward&limit=100",
    headers={"Authorization": f"Bearer {api_key}"},
)
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    print(resp.read().decode()[:3000])
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:500]}")
