import json
import urllib.request
import ssl

ctx = ssl.create_default_context()
req = urllib.request.Request(
    "https://api-docs.render.com/openapi/render-public-api-1.json",
    headers={"User-Agent": "Mozilla/5.0"}
)
resp = urllib.request.urlopen(req, context=ctx, timeout=30)
spec = json.load(resp)

for schema_name in ["nativeRuntimeDetailsPOST", "dockerDetailsPOST", "pythonDetails", "webServiceDetailsPOST", "servicePOST", "serviceDetails"]:
    try:
        s = spec["components"]["schemas"][schema_name]["properties"]
        r = spec["components"]["schemas"][schema_name].get("required", [])
        print(f"\n=== {schema_name} ===")
        for k, v in s.items():
            star = "*" if k in r else " "
            typ = v.get("type", "")
            desc = v.get("description", "")[:120]
            print(f"{star} {k}: {typ}  {desc}")
    except KeyError:
        print(f"\n=== {schema_name}: not found ===")

# Search for buildCommand across all schemas
print("\n=== Schemas containing 'buildCommand' ===")
for sname, sdata in spec["components"]["schemas"].items():
    props = sdata.get("properties", {})
    if "buildCommand" in props or "startCommand" in props:
        print(f"\n  {sname}:")
        if "buildCommand" in props:
            print(f"    buildCommand: {json.dumps(props['buildCommand'])[:200]}")
        if "startCommand" in props:
            print(f"    startCommand: {json.dumps(props['startCommand'])[:200]}")
    # Check allOf
    for ref_key in ["allOf", "anyOf", "oneOf"]:
        if ref_key in sdata:
            for ref_item in sdata[ref_key]:
                if "$ref" in ref_item:
                    ref_name = ref_item["$ref"].split("/")[-1]
                    ref_data = spec["components"]["schemas"].get(ref_name, {})
                    ref_props = ref_data.get("properties", {})
                    if "buildCommand" in ref_props or "startCommand" in ref_props:
                        print(f"\n  {sname} -> {ref_name}:")
                        if "buildCommand" in ref_props:
                            print(f"    buildCommand: {json.dumps(ref_props['buildCommand'])[:200]}")
                        if "startCommand" in ref_props:
                            print(f"    startCommand: {json.dumps(ref_props['startCommand'])[:200]}")
