"""
List all available tags in ShipStation
"""

import os
import sys
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

API_BASE = "https://ssapi.shipstation.com"
API_KEY = os.getenv("SHIPSTATION_API_KEY")
API_SECRET = os.getenv("SHIPSTATION_API_SECRET")


def list_tags():
    """List all available tags"""
    if not API_KEY or not API_SECRET:
        print("Error: ShipStation API credentials not configured.", file=sys.stderr)
        sys.exit(1)

    auth = (API_KEY, API_SECRET)
    url = f"{API_BASE}/accounts/listtags"

    try:
        response = requests.get(url, auth=auth, timeout=10)
        response.raise_for_status()
        tags = response.json()

        print("\nAvailable tags:")
        for tag in sorted(tags, key=lambda x: x["name"]):
            print(f"  {tag['name']} (ID: {tag['tagId']})")
        print()

    except Exception as e:
        print(f"Error fetching tags: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    list_tags()
