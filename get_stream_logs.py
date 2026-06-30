import urllib.request, ssl, json

S = "srv-d91p0fsm0tmc73d753p0"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()

# Try cursor-based deploy log for the latest failed deploy
for deploy_id in ["dep-d91pgoeq1p3s73ccdro0", "dep-d91pabpo3t8c73efbe40"]:
    for ep in [f"https://api.render.com/v1/services/{S}/deploys/{deploy_id}/log?cursor=0&direction=forward&limit=100",
               f"https://api.render.com/v1/services/{S}/deploys/{deploy_id}/events",
               f"https://api.render.com/v1/services/{S}/deploys/{deploy_id}/cursor"]:
        req = urllib.request.Request(ep, headers={"Authorization": f"Bearer {K}"})
        try:
            resp = urllib.request.urlopen(req, context=ctx, timeout=10)
            data = resp.read().decode("utf-8", errors="replace")
            print(f"=== {deploy_id} - {ep.split('/')[-1]} ===")
            print(data[:1000])
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:200]
            if "404" not in str(e.code):
                print(f"=== {deploy_id} - {ep.split('/')[-1]} (HTTP {e.code}) ===")
                print(body)

# Also try service-level recent logs
for ep in [f"https://api.render.com/v1/services/{S}/log?limit=50",
           f"https://api.render.com/v1/services/{S}/events?limit=50"]:
    req = urllib.request.Request(ep, headers={"Authorization": f"Bearer {K}"})
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        data = resp.read().decode("utf-8", errors="replace")
        print(f"=== service {ep.split('/')[-1]} ===")
        print(data[:1000])
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        if "404" not in str(e.code):
            print(f"=== service {ep.split('/')[-1]} (HTTP {e.code}) ===")
            print(body)
