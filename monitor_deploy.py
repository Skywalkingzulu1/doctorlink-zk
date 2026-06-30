import urllib.request, ssl, json, time, sys
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
D = sys.argv[1]
ctx = ssl.create_default_context()
for i in range(60):
    time.sleep(15)
    r = json.load(urllib.request.urlopen(
        urllib.request.Request(f"https://api.render.com/v1/services/srv-d91p0fsm0tmc73d753p0/deploys/{D}",
                               headers={"Authorization": f"Bearer {K}"}),
        context=ctx, timeout=10))
    s = r.get("status", "?")
    print(f"[{i*15}s] {s}", flush=True)
    if s == "live":
        print("Live!")
        break
    if s in ("build_failed", "deploy_failed", "canceled", "update_failed"):
        print(f"Failed: {json.dumps(r.get('errorSummary', {}), indent=2)[:500]}")
        break
