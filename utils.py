import os
import json
from urllib.parse import quote


DATA_DIR = "data"
THUMBNAIL_DIR = "static/thumbnails"
VIDEO_DIR = "static/videos"


def fetch_cartoons():
    """
    Load the cartoon index from a JSON file.
    Returns a list of cartoon episodes with metadata.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(BASE_DIR, "data", "cartoon_index.json")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_thumbnail(episode):
    """
    Returns the path to the thumbnail image for a given episode.
    """
    filename = episode.get("thumbnail", "")
    if filename:
        return f"/{THUMBNAIL_DIR}/{quote(filename)}"
    return None


def get_video_url(episode):
    """
    Returns the path to the video file for a given episode.
    """
    filename = episode.get("file", "")
    if filename:
        return f"/{VIDEO_DIR}/{quote(filename)}"
    return None


def group_by_season(episodes):
    """
    Groups episodes by season.
    Returns a dictionary like: { "Season 1": [ep1, ep2], "Season 2": [...] }
    """
    seasons = {}
    for episode in episodes:
        season = episode.get("season", "Season 1")
        if season not in seasons:
            seasons[season] = []
        seasons[season].append(episode)
    return seasons
