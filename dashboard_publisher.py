import csv
import json
import os
import time
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

CSV_FILE = Path(os.getenv("OLIS_SHADOW_CSV", "research_23_shadow.csv"))
API_URL = os.getenv("OLIS_API_URL", "https://YOUR-OLIS-SERVER.example/api/live")
API_KEY = os.getenv("OLIS_API_KEY", "CHANGE_ME")
POLL_SECONDS = int(os.getenv("OLIS_POLL_SECONDS", "2"))

MARKETS = {
    "GG":  ("gg_probability", "gg_edge", "1.8"),
    "O25": ("o25_probability", "o25_edge", "1.8"),
    "O35": ("o35_probability", "o35_edge", "2.8"),
}

# Conservative display thresholds. These are dashboard display gates,
# not claims of guaranteed outcomes.
THRESHOLDS = {
    "GG":  (65.0, 5.0),
    "O25": (65.0, 5.0),
    "O35": (70.0, 5.0),
}

def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def latest_capture(rows):
    ids = []
    for r in rows:
        try:
            ids.append(int(float(r.get("capture_id", ""))))
        except Exception:
            pass
    return max(ids) if ids else None

def build_payload(rows, capture_id):
    current = [r for r in rows if str(r.get("capture_id","")).strip() == str(capture_id)]
    current.sort(key=lambda r: int(float(r.get("fixture_number", 999))) if r.get("fixture_number") else 999)
    fixtures = []

    for i, r in enumerate(current[:10], 1):
        markets = {}
        for key, (pcol, ecol, odds) in MARKETS.items():
            p, e = fnum(r.get(pcol)), fnum(r.get(ecol))
            if p is not None and e is not None:
                markets[key] = {"probability": p, "edge": e, "odds": float(odds)}

        candidates = []
        for key, (pmin, emin) in THRESHOLDS.items():
            m = markets.get(key)
            if m and m["probability"] >= pmin and m["edge"] >= emin:
                candidates.append((m["probability"] + m["edge"], key, m))

        candidates.sort(reverse=True)
        best = candidates[0] if candidates else None

        fixtures.append({
            "number": i,
            "fixture_id": r.get("fixture_id"),
            "home": r.get("home_team"),
            "away": r.get("away_team"),
            "markets": markets,
            "decision": {
                "market": best[1] if best else None,
                "action": "SHADOW BET" if best else "NO BET",
                "probability": best[2]["probability"] if best else None,
                "edge": best[2]["edge"] if best else None,
                "reason": "Qualified shadow signal" if best else "No sufficiently qualified signal"
            }
        })

    bets = [f for f in fixtures if f["decision"]["action"] == "SHADOW BET"]
    return {
        "capture_id": int(capture_id),
        "fixtures": fixtures,
        "summary": {"qualified_signals": len(bets), "fixtures": len(fixtures)},
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

def publish(payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(API_URL, data=data, method="POST",
                                 headers={"Content-Type":"application/json", "X-OLIS-Key":API_KEY})
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.read().decode()

def main():
    last = None
    print("OLIS Dashboard Publisher started.")
    print("CSV:", CSV_FILE)
    print("API :", API_URL)

    while True:
        try:
            if CSV_FILE.exists():
                with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as f:
                    rows = list(csv.DictReader(f))
                cid = latest_capture(rows)
                if cid is not None and cid != last:
                    payload = build_payload(rows, cid)
                    if len(payload["fixtures"]) == 10:
                        print(f"Publishing Capture {cid}...")
                        print(publish(payload))
                        last = cid
            time.sleep(POLL_SECONDS)
        except Exception as e:
            print("Publisher warning:", e)
            time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()
