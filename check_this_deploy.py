import urllib.request, ssl, json
S = "srv-d91p0fsm0tmc73d753p0"
D = "dep-d91plc5aeets73fvb2og"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()
r = json.load(urllib.request.urlopen(
    urllib.request.Request(f"https://api.render.com/v1/services/{S}/deploys/{D}",
                           headers={"Authorization": f"Bearer {K}"}),
    context=ctx, timeout=15))
print(json.dumps(r, indent=2))
