import json
import os
import sys
import urllib.request
from pathlib import Path

USERNAME = "anhafdev"
API_ROOT = "https://api.github.com"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "assets" / "stars.json"


def call_github(path):
    request = urllib.request.Request(API_ROOT + path)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", "profile-stats-builder")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_all_repos(username):
    page_number = 1
    all_repos = []
    while True:
        path = f"/users/{username}/repos?per_page=100&type=owner&page={page_number}"
        one_page = call_github(path)
        all_repos.extend(one_page)
        if len(one_page) < 100:
            return all_repos
        page_number += 1


def count_total_stars(username):
    own_repos = [repo for repo in fetch_all_repos(username) if not repo["fork"]]
    return sum(repo["stargazers_count"] for repo in own_repos)


def main():
    try:
        total_stars = count_total_stars(USERNAME)
    except Exception as error:
        print("Could not fetch GitHub data:", error)
        sys.exit(1)
    badge_data = {
        "schemaVersion": 1,
        "label": "TOTAL STARS",
        "message": str(total_stars),
        "color": "e3b341",
        "namedLogo": "github",
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(badge_data), encoding="utf-8")
    print("Saved", OUTPUT_FILE, "with", total_stars, "stars")


if __name__ == "__main__":
    main()
