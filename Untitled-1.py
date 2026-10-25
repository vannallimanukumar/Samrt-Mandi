"""
Daily price updater for the Sell Smart website.

What it does: downloads the latest mandi prices for Annamayya district
from data.gov.in (Agmarknet) and writes them to prices.json,
which index.html reads automatically.

Setup (one time):
1. Create a free account at https://data.gov.in and get an API key.
2. pip install requests
3. Set your key:  export DATA_GOV_API_KEY="your_key_here"
   (on Windows PowerShell:  $env:DATA_GOV_API_KEY="your_key_here")
4. Run:  python update_prices.py

To run it every day automatically, use a GitHub Actions schedule,
or a cron job (Linux/Mac) or Task Scheduler (Windows).

Note: please check the resource id and field names on data.gov.in,
because government datasets can change.
"""
import json
import os
import requests

API_KEY = os.environ["DATA_GOV_API_KEY"]
RESOURCE = "9ef84268-d588-465a-a308-a864a43d0070"  # Daily mandi prices (Agmarknet)
URL = f"https://api.data.gov.in/resource/{RESOURCE}"

params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 1000,
    "filters[state.keyword]": "Andhra Pradesh",
    "filters[district]": "Annamayya",
}

records = requests.get(URL, params=params, timeout=30).json().get("records", [])

rows = []
latest = ""
for r in records:
    try:
        d = r["arrival_date"]  # format dd/mm/yyyy
        iso = f"{d[6:10]}-{d[3:5]}-{d[0:2]}"
        rows.append({
            "market": r["market"],
            "crop": r["commodity"],
            "min": int(float(r["min_price"])),
            "max": int(float(r["max_price"])),
            "avg": int(float(r["modal_price"])),
            "date": iso,
            "real": True,
        })
        latest = max(latest, iso)
    except (KeyError, ValueError):
        continue

if rows:
    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump({"updated": latest, "rows": rows}, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(rows)} price rows, latest date {latest}")
else:
    print("No records returned. Check your API key, filters, or try again later.")






    