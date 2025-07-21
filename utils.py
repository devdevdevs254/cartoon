# 📁 utils.py
import requests
from collections import Counter, defaultdict
import re

def fetch_cartoons(query=None, year=None, genre=None, include_subjects=False, sort_by="downloads"):
    base_url = "https://archive.org/advancedsearch.php"
    q = "collection:animationandcartoons AND mediatype:movies"

    if query:
        q += f" AND ({query})"
    if year:
        q += f" AND year:{year}"
    if genre:
        q += f" AND subject:{genre}"

    params = {
        "q": q,
        "fl[]": "identifier,title,description,subject,year",
        "sort[]": "downloads desc",
        "rows": 100,
        "output": "json"
    }

    res = requests.get(base_url, params=params).json()
    docs = res['response']['docs']

    genre_counts = Counter()
    if include_subjects:
        for doc in docs:
            subjects = doc.get("subject")
            if isinstance(subjects, list):
                for tag in subjects:
                    genre_counts[tag.lower().strip()] += 1
            elif isinstance(subjects, str):
                for tag in subjects.split(";"):
                    genre_counts[tag.lower().strip()] += 1

    return docs, genre_counts if include_subjects else None

def get_metadata(identifier):
    return requests.get(f"https://archive.org/metadata/{identifier}").json()

def get_thumbnail(meta):
    for file in meta.get("files", []):
        fname = file.get("name", "").lower()
        fmt = file.get("format", "").lower()
        if "thumb" in fname or fmt in ["jpeg", "jpeg thumb", "jpeg2000", "jpeg2000 image"]:
            return f"https://archive.org/download/{meta['metadata']['identifier']}/{file['name']}"
    return f"https://archive.org/services/img/{meta['metadata']['identifier']}"

def get_stream_url(identifier):
    meta = get_metadata(identifier)
    for file in meta.get("files", []):
        if file["name"].endswith(".mp4"):
            return f"https://archive.org/download/{identifier}/{file['name']}"
    return None

def get_episodes(identifier):
    meta = get_metadata(identifier)
    episodes = []
    for file in meta.get("files", []):
        if file["name"].endswith(".mp4"):
            episodes.append({
                "title": file.get("title") or file["name"],
                "url": f"https://archive.org/download/{identifier}/{file['name']}",
                "duration": "",
                "number": len(episodes) + 1
            })
    return episodes

def group_by_season(episodes):
    seasons = defaultdict(list)
    for ep in episodes:
        match = re.search(r"(0?(\d+))x(\d+)", ep["title"])
        if match:
            season = f"Season {int(match.group(2))}"
        else:
            season = "Specials"
        seasons[season].append(ep)
    return dict(seasons)
