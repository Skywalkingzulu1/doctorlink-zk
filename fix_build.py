import urllib.request, ssl, json

S = "srv-d91p0fsm0tmc73d753p0"
K = "rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp"
ctx = ssl.create_default_context()

# Install stellar CLI inside the project directory so it persists to runtime
build_cmd = (
    'pip install -r requirements.txt ; '
    'mkdir -p bin ; '
    'curl -fsSL https://github.com/stellar/stellar-cli/releases/download/v27.0.0/'
    'stellar-cli-27.0.0-x86_64-unknown-linux-gnu.tar.gz -o /tmp/stellar.tar.gz ; '
    'tar -xzf /tmp/stellar.tar.gz -C /tmp ; '
    'find /tmp -maxdepth 3 -name stellar -type f -exec cp {} bin/stellar \\; ; '
    'chmod +x bin/stellar'
)

start_cmd = (
    'export PATH="$PWD/bin:/opt/render/.local/bin:$HOME/.cargo/bin:$PATH" && '
    'uvicorn main:app --host 0.0.0.0 --port $PORT'
)

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
    print(f"Updated: {resp.status}")
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:500]}")
