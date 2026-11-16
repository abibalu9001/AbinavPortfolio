
import re
import json
import requests
from bs4 import BeautifulSoup

USERNAME = "abinavbalu"
PROFILE_URL = f"https://www.codechef.com/users/{USERNAME}"


def fetch_codechef_data():
    try:
        response = requests.get(
            PROFILE_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text(" ", strip=True)

        # Total problems solved
        total_solved = None
        match = re.search(
            r"Total Problems Solved\s*[:\-]?\s*(\d+)",
            page_text,
            re.IGNORECASE
        )

        if match:
            total_solved = int(match.group(1))

        # Contest rating
        rating = None
        rating_element = soup.select_one(".rating-number")

        if rating_element:
            rating_text = rating_element.get_text(strip=True)
            if rating_text.isdigit():
                rating = int(rating_text)

        # Active days from CodeChef's submission heatmap
        active_days = None

        heatmap_match = re.search(
            r"userDailySubmissionsStats\s*=\s*(\{.*?\}|\[.*?\])\s*;",
            response.text,
            re.DOTALL
        )

        if heatmap_match:
            try:
                heatmap = json.loads(heatmap_match.group(1))

                if isinstance(heatmap, dict):
                    active_days = sum(
                        1 for value in heatmap.values() if int(value) > 0
                    )
                elif isinstance(heatmap, list):
                    active_days = sum(
                        1 for item in heatmap
                        if int(item.get("value", 0)) > 0
                    )
            except (ValueError, TypeError, AttributeError):
                pass

        # Badge names, when exposed in the public profile HTML
        badges = []
        badge_heading = soup.find(
            lambda tag: tag.name in ["h2", "h3", "h4"]
            and "badges" in tag.get_text(" ", strip=True).lower()
        )

        if badge_heading:
            section = badge_heading.parent
            for image in section.find_all("img"):
                name = image.get("alt") or image.get("title")
                if name and name.lower() not in ["badge", ""]:
                    badges.append(name)

        return {
            "username": USERNAME,
            "total_solved": total_solved,
            "easy": None,
            "medium": None,
            "hard": None,
            "badges": list(dict.fromkeys(badges)),
            "contest_rating": rating,
            "active_days": active_days,
            "profile_url": PROFILE_URL,
            "status": "success"
        }

    except (requests.RequestException, ValueError) as error:
        return {
            "username": USERNAME,
            "status": "error",
            "error": str(error)
        }
