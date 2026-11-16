
import re
import requests
from bs4 import BeautifulSoup

USERNAME = "25add002@cit"

# Paste the complete Programming Profile URL from your browser here.
PROFILE_URL = "https://www.skillrack.com/faces/resume.xhtml?id=552803&key=a1239ae24c6e78c8c56c0d01cadb42bb6db573ff"


def fetch_skillrack_data():
    try:
        response = requests.get(
            PROFILE_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text(" ", strip=True)

        def extract_number(pattern):
            match = re.search(pattern, page_text, re.IGNORECASE)
            return int(match.group(1)) if match else None

        total_solved = extract_number(
            r"(\d+)\s*PROGRAMS\s*SOLVED"
        )

        rank = extract_number(
            r"(\d+)\s*RANK"
        )

        bronze = extract_number(r"(\d+)\s*BRONZE")
        silver = extract_number(r"(\d+)\s*SILVER")
        gold = extract_number(r"(\d+)\s*GOLD")

        return {
            "username": USERNAME,
            "total_solved": total_solved,
            "easy": None,
            "medium": None,
            "hard": None,
            "badges": {
                "bronze": bronze,
                "silver": silver,
                "gold": gold
            },
            "contest_rating": None,
            "active_days": None,
            "rank": rank,
            "profile_url": PROFILE_URL,
            "status": "success"
        }

    except requests.RequestException as error:
        return {
            "username": USERNAME,
            "status": "error",
            "error": str(error)
        }
