import json
import sys
from pathlib import Path

from github_data import count_total_stars

USERNAME = "anhafdev"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "assets" / "stars.json"


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
