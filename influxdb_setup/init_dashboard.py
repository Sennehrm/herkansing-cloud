import urllib.request
import json
import time

token = "my-influx-token"
base_url = "http://influxdb:8086/api/v2"
org_name = "sensorsim"

headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}

# 1. Wacht tot InfluxDB gereed is
print("[Influx-Init] Wachten tot InfluxDB online is...")
while True:
    try:
        req = urllib.request.Request("http://influxdb:8086/health")
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                print("[Influx-Init] InfluxDB is online!")
                break
    except Exception:
        time.sleep(1)

# 2. Vraag Org ID op
org_id = None
for _ in range(10):
    try:
        req = urllib.request.Request(f"{base_url}/orgs?org={org_name}", headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("orgs"):
                org_id = data["orgs"][0]["id"]
                break
    except Exception:
        time.sleep(1)

if not org_id:
    print("[Influx-Init] Fout: Kon Org ID niet ophalen.")
    exit(1)

# 3. Check of dashboard al bestaat
req = urllib.request.Request(f"{base_url}/dashboards?org={org_name}", headers=headers)
with urllib.request.urlopen(req) as resp:
    existing = json.loads(resp.read().decode("utf-8"))
    for d in existing.get("dashboards", []):
        if d["name"] == "Smart Controller Gateway":
            print("[Influx-Init] Dashboard bestaat al, configuratie is up-to-date.")
            exit(0)

# 4. Maak Dashboard aan
print("[Influx-Init] Dashboard automatisch aanmaken...")
dash_payload = json.dumps({
    "orgID": org_id,
    "name": "Smart Controller Gateway",
    "description": "Smart Sensor Gateway Live Dashboard"
}).encode("utf-8")

req = urllib.request.Request(f"{base_url}/dashboards", data=dash_payload, headers=headers, method="POST")
with urllib.request.urlopen(req) as resp:
    dash_data = json.loads(resp.read().decode("utf-8"))
dash_id = dash_data["id"]

cells = [
    {
        "name": "Joystick 1 (Live X & Y)",
        "x": 0, "y": 0, "w": 6, "h": 4,
        "view": {
            "name": "Joystick 1 (Live X & Y)",
            "properties": {
                "type": "xy",
                "shape": "chronograf-v2",
                "queries": [{
                    "text": 'from(bucket: "sensor_data")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r["_measurement"] == "joystick1")\n  |> filter(fn: (r) => r["_field"] == "x" or r["_field"] == "y")',
                    "editMode": "advanced",
                    "name": "",
                    "builderConfig": {"buckets": [], "tags": [], "functions": [], "aggregateWindowType": "filter"}
                }],
                "axes": {
                    "x": {"bounds": ["", ""], "label": "Tijd", "prefix": "", "suffix": "", "base": "10", "scale": "linear"},
                    "y": {"bounds": ["0", "255"], "label": "Positie (0-255)", "prefix": "", "suffix": "", "base": "10", "scale": "linear"}
                },
                "geom": "line",
                "colors": [
                    {"id": "1", "type": "scale", "hex": "#31C0F6", "name": "Nineteen Eighty Four", "value": 0},
                    {"id": "2", "type": "scale", "hex": "#A500A5", "name": "Nineteen Eighty Four", "value": 0}
                ],
                "note": "",
                "showNoteWhenEmpty": False,
                "xColumn": "_time",
                "yColumn": "_value",
                "position": "overlaid",
                "opacity": 1,
                "hoverDimension": "auto",
                "generateCheckboxes": False
            }
        }
    },
    {
        "name": "Joystick 2 (Live X & Y)",
        "x": 6, "y": 0, "w": 6, "h": 4,
        "view": {
            "name": "Joystick 2 (Live X & Y)",
            "properties": {
                "type": "xy",
                "shape": "chronograf-v2",
                "queries": [{
                    "text": 'from(bucket: "sensor_data")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r["_measurement"] == "joystick2")\n  |> filter(fn: (r) => r["_field"] == "x" or r["_field"] == "y")',
                    "editMode": "advanced",
                    "name": "",
                    "builderConfig": {"buckets": [], "tags": [], "functions": [], "aggregateWindowType": "filter"}
                }],
                "axes": {
                    "x": {"bounds": ["", ""], "label": "Tijd", "prefix": "", "suffix": "", "base": "10", "scale": "linear"},
                    "y": {"bounds": ["0", "255"], "label": "Positie (0-255)", "prefix": "", "suffix": "", "base": "10", "scale": "linear"}
                },
                "geom": "line",
                "colors": [
                    {"id": "1", "type": "scale", "hex": "#00C9FF", "name": "Nineteen Eighty Four", "value": 0},
                    {"id": "2", "type": "scale", "hex": "#92FE9D", "name": "Nineteen Eighty Four", "value": 0}
                ],
                "note": "",
                "showNoteWhenEmpty": False,
                "xColumn": "_time",
                "yColumn": "_value",
                "position": "overlaid",
                "opacity": 1,
                "hoverDimension": "auto",
                "generateCheckboxes": False
            }
        }
    },
    {
        "name": "Laatste Knop Ingedrukt",
        "x": 0, "y": 4, "w": 4, "h": 3,
        "view": {
            "name": "Laatste Knop Ingedrukt",
            "properties": {
                "type": "single-stat",
                "shape": "chronograf-v2",
                "queries": [{
                    "text": 'from(bucket: "sensor_data")\n  |> range(start: -24h, stop: now())\n  |> filter(fn: (r) => r["_measurement"] == "button_data")\n  |> filter(fn: (r) => r["_field"] == "button_name" or r["_field"] == "pressed")\n  |> last()',
                    "editMode": "advanced",
                    "name": "",
                    "builderConfig": {"buckets": [], "tags": [], "functions": [], "aggregateWindowType": "filter"}
                }],
                "colors": [{"id": "base", "type": "text", "hex": "#00C9FF", "name": "laser", "value": 0}],
                "prefix": "",
                "suffix": "",
                "decimalPlaces": {"isEnforced": False, "digits": 2},
                "note": "",
                "showNoteWhenEmpty": False
            }
        }
    },
    {
        "name": "Gemiddelde Joystick 1 (1 uur)",
        "x": 4, "y": 4, "w": 4, "h": 3,
        "view": {
            "name": "Gemiddelde Joystick 1 (1 uur)",
            "properties": {
                "type": "single-stat",
                "shape": "chronograf-v2",
                "queries": [{
                    "text": 'from(bucket: "sensor_data")\n  |> range(start: -1h, stop: now())\n  |> filter(fn: (r) => r["_measurement"] == "joystick1")\n  |> filter(fn: (r) => r["_field"] == "x" or r["_field"] == "y")\n  |> mean()',
                    "editMode": "advanced",
                    "name": "",
                    "builderConfig": {"buckets": [], "tags": [], "functions": [], "aggregateWindowType": "filter"}
                }],
                "colors": [{"id": "base", "type": "text", "hex": "#FFD700", "name": "gold", "value": 0}],
                "prefix": "",
                "suffix": "",
                "decimalPlaces": {"isEnforced": True, "digits": 1},
                "note": "",
                "showNoteWhenEmpty": False
            }
        }
    },
    {
        "name": "Gemiddelde Joystick 2 (1 uur)",
        "x": 8, "y": 4, "w": 4, "h": 3,
        "view": {
            "name": "Gemiddelde Joystick 2 (1 uur)",
            "properties": {
                "type": "single-stat",
                "shape": "chronograf-v2",
                "queries": [{
                    "text": 'from(bucket: "sensor_data")\n  |> range(start: -1h, stop: now())\n  |> filter(fn: (r) => r["_measurement"] == "joystick2")\n  |> filter(fn: (r) => r["_field"] == "x" or r["_field"] == "y")\n  |> mean()',
                    "editMode": "advanced",
                    "name": "",
                    "builderConfig": {"buckets": [], "tags": [], "functions": [], "aggregateWindowType": "filter"}
                }],
                "colors": [{"id": "base", "type": "text", "hex": "#FFD700", "name": "gold", "value": 0}],
                "prefix": "",
                "suffix": "",
                "decimalPlaces": {"isEnforced": True, "digits": 1},
                "note": "",
                "showNoteWhenEmpty": False
            }
        }
    },
    {
        "name": "Gemiddelde Joystick 1 (24 uur)",
        "x": 0, "y": 7, "w": 6, "h": 3,
        "view": {
            "name": "Gemiddelde Joystick 1 (24 uur)",
            "properties": {
                "type": "single-stat",
                "shape": "chronograf-v2",
                "queries": [{
                    "text": 'from(bucket: "sensor_data")\n  |> range(start: -24h, stop: now())\n  |> filter(fn: (r) => r["_measurement"] == "joystick1")\n  |> filter(fn: (r) => r["_field"] == "x" or r["_field"] == "y")\n  |> mean()',
                    "editMode": "advanced",
                    "name": "",
                    "builderConfig": {"buckets": [], "tags": [], "functions": [], "aggregateWindowType": "filter"}
                }],
                "colors": [{"id": "base", "type": "text", "hex": "#47D147", "name": "green", "value": 0}],
                "prefix": "",
                "suffix": "",
                "decimalPlaces": {"isEnforced": True, "digits": 1},
                "note": "",
                "showNoteWhenEmpty": False
            }
        }
    },
    {
        "name": "Gemiddelde Joystick 2 (24 uur)",
        "x": 6, "y": 7, "w": 6, "h": 3,
        "view": {
            "name": "Gemiddelde Joystick 2 (24 uur)",
            "properties": {
                "type": "single-stat",
                "shape": "chronograf-v2",
                "queries": [{
                    "text": 'from(bucket: "sensor_data")\n  |> range(start: -24h, stop: now())\n  |> filter(fn: (r) => r["_measurement"] == "joystick2")\n  |> filter(fn: (r) => r["_field"] == "x" or r["_field"] == "y")\n  |> mean()',
                    "editMode": "advanced",
                    "name": "",
                    "builderConfig": {"buckets": [], "tags": [], "functions": [], "aggregateWindowType": "filter"}
                }],
                "colors": [{"id": "base", "type": "text", "hex": "#47D147", "name": "green", "value": 0}],
                "prefix": "",
                "suffix": "",
                "decimalPlaces": {"isEnforced": True, "digits": 1},
                "note": "",
                "showNoteWhenEmpty": False
            }
        }
    }
]

for c in cells:
    cell_req = urllib.request.Request(f"{base_url}/dashboards/{dash_id}/cells", data=json.dumps({"x": c["x"], "y": c["y"], "w": c["w"], "h": c["h"], "name": c["name"]}).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(cell_req) as resp:
        cell_data = json.loads(resp.read().decode("utf-8"))
    cell_id = cell_data["id"]
    
    view_req = urllib.request.Request(f"{base_url}/dashboards/{dash_id}/cells/{cell_id}/view", data=json.dumps(c["view"]).encode("utf-8"), headers=headers, method="PATCH")
    with urllib.request.urlopen(view_req) as resp:
        pass

print("[Influx-Init] Dashboard succesvol geconfigureerd en live gezet!")
