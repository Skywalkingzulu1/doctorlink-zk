import json
import urllib.request
import urllib.error
import ssl

data = {
    "type": "web_service",
    "name": "doctorlink-zk",
    "ownerId": "tea-cvmolmp5pdvs73e388g0",
    "repo": "https://github.com/Skywalkingzulu1/doctorlink-zk",
    "branch": "main",
    "rootDir": "doctorlink-health-services",
    "serviceDetails": {
        "runtime": "python",
        "plan": "free",
        "region": "oregon",
        "envSpecificDetails": {
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
            "pythonVersion": "3.11",
        },
        "envVars": [
            {"key": "STELLAR_NETWORK", "value": "testnet"},
            {"key": "ZK_VERIFIER_CONTRACT", "value": "CAB7ZADYO7M7NWYBNCMLTLO4SCQTHGHMW5QBMWJBOSA5HKMOUFTN6AN2"},
            {"key": "HEALTH_TOKEN_CONTRACT", "value": "CBZ5ZNC6I4NOWKGFJOECMYJWUQ2QGQZ622PJQIV6EK427WVS3HONQGRT"},
            {"key": "SECRET_KEY", "generateValue": True},
            {"key": "STELLAR_SECRET_KEY", "sync": False},
            {"key": "OPENROUTER_API_KEY", "sync": False},
            {"key": "OCTOPARSE_API_KEY", "sync": False},
        ],
    },
}

body = json.dumps(data).encode("utf-8")
print("Body length:", len(body))
print("Body preview:", json.dumps(data, indent=2)[:300])

req = urllib.request.Request(
    "https://api.render.com/v1/services",
    data=body,
    headers={
        "Authorization": "Bearer rnd_YKmeCDdpP6sukfIDW7Jt9Bvs0NVp",
        "Content-Type": "application/json",
    },
    method="POST",
)
ctx = ssl.create_default_context()
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=60)
    print(resp.status, resp.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:1000]}")
except Exception as e:
    print(f"Error: {e}")
