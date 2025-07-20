import requests
import os
import json
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
INDEX_FILE = DATA_DIR / "cartoon_index.json"

# Replace with your actual collection or list of identifiers
CARTOON_IDENTIFIERS = [
    "AdventuresOfSonicTheHedgehog_1001",
    "AdventuresOfSonicTheHedgehog_1002"
]

def fetch_from_ia(identifier):
    url = f"https://archive.org/metadata/{identifier}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    title = data.get("metadata", {}).get("title", identifier)
    year = data.get("metadata", {}).get("year", "")
    description = data.get("metadata", {}).get("description", "")
    
    files = data.get("files", [])
    mp4_files = [f for f in files if f.get("format") == "MPEG4" or f.get("name", "").endswith(".mp4")]

    items = []
    for f in mp4_files:
        name = f.get("name")
        items.append({
            "identifier": identifier,
            "file": name,
            "title": title,
            "year": year,
            "description": description,
            "video_url": f"https://archive.org/download/{identifier}/{name}",
            "thumbnail": f"https://archive.org/download/{identifier}/{name.replace('.mp4', '.jpg')}"
        })

    return items

def refresh_cartoon_index():
    all_items = []
    for ident in CARTOON_IDENTIFIERS:
        cartoon_items = fetch_from_ia(ident)
        if cartoon_items:
            all_items.extend(cartoon_items)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2)
    return all_items

def load_cartoon_data():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return refresh_cartoon_index()

def group_by_season(cartoons):
    # Optional: you can improve this based on metadata
    grouped = {}
    for c in cartoons:
        key = c.get("identifier")
        grouped.setdefault(key, []).append(c)
    return grouped

def get_thumbnail(item):
    return item.get("thumbnail", "")
