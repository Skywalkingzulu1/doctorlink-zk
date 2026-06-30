import urllib.request, ssl, json, time

S = "srv-d91p0fsm0tmc73d753p0"
D = "dep-d91p3gmq1p3s73cbpg30"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()

for i in range(40):
    time.sleep(15)
    r = json.load(urllib.request.urlopen(
        urllib.request.Request(f"https://api.render.com/v1/services/{S}/deploys/{D}",
                               headers={"Authorization": f"Bearer {K}"}),
        context=ctx, timeout=15))
    s = r.get("status", "?")
    print(f"[{i*15}s] {s}")
    if s in ("live", "build_failed", "deploy_failed", "canceled"):
        print("Finished:", r.get("finishedAt", "?"))
        print("Commit:", r.get("commit", {}).get("message", "N/A"))
        break
