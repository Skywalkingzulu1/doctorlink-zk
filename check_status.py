import urllib.request, ssl, json

S = "srv-d91p0fsm0tmc73d753p0"
D = "dep-d91p3gmq1p3s73cbpg30"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()
r = json.load(urllib.request.urlopen(
    urllib.request.Request(f"https://api.render.com/v1/services/{S}/deploys/{D}",
                           headers={"Authorization": f"Bearer {K}"}),
    context=ctx, timeout=15))
print("Status:", r.get("status"))
print("Finished:", r.get("finishedAt", "N/A"))
print("Commit:", r.get("commit", {}).get("message", "N/A"))
