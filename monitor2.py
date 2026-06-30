import urllib.request, ssl, json, time, sys

S = "srv-d91p0fsm0tmc73d753p0"
D = "dep-d91pgoeq1p3s73ccdro0"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()
start = time.time()
done = {"live","build_failed","deploy_failed","canceled","update_failed"}

for i in range(60):
    time.sleep(10)
    try:
        r = json.load(urllib.request.urlopen(
            urllib.request.Request(f"https://api.render.com/v1/services/{S}/deploys/{D}",
                                   headers={"Authorization": f"Bearer {K}"}),
            context=ctx, timeout=10))
        s = r.get("status", "?")
        elapsed = int(time.time() - start)
        sys.stdout.write(f"\r[{elapsed}s] {s}  ")
        sys.stdout.flush()
        if s in done:
            print(f"\nFinished: {r.get('finishedAt', '?')}")
            print(f"Commit: {r.get('commit', {}).get('message', 'N/A')}")
            print(json.dumps(r, indent=2))
            break
    except Exception as e:
        print(f"\nError: {e}")
        break
