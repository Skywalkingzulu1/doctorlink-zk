import urllib.request, ssl, json

S = "srv-d91p0fsm0tmc73d753p0"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()

# Update build command to include stellar-cli install
build_cmd = (
    "pip install -r requirements.txt && "
    "curl -fsSL https://raw.githubusercontent.com/stellar/stellar-cli/main/install.sh | bash"
)
start_cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"

body = json.dumps({
    "serviceDetails": {
        "envSpecificDetails": {
            "buildCommand": build_cmd,
            "startCommand": start_cmd,
        }
    }
}).encode()

req = urllib.request.Request(
    f"https://api.render.com/v1/services/{S}",
    data=body,
    headers={"Authorization": f"Bearer {K}", "Content-Type": "application/json"},
    method="PATCH",
)
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    print(f"Service updated: {resp.status}")
    print(json.dumps(json.load(resp), indent=2)[:500])
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:500]}")
