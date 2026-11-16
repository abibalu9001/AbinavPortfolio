
from portfolio.services.leetcode import fetch_leetcode_data
from portfolio.services.codeforces import fetch_codeforces_data
from portfolio.services.codechef import fetch_codechef_data
from portfolio.services.hackerrank import fetch_hackerrank_data
from portfolio.services.skillrack import fetch_skillrack_data


def normalize_badges(badges):
    """Convert platform badge data into a consistent display format."""

    normalized = []

    if isinstance(badges, dict):
        for name, count in badges.items():
            if count:
                normalized.append({
                    "name": f"{name.title()} ({count})",
                    "icon": ""
                })

    elif isinstance(badges, list):
        for badge in badges:
            if isinstance(badge, dict):
                normalized.append({
                    "name": (
                        badge.get("name")
                        or badge.get("displayName")
                        or badge.get("shortName")
                        or "Achievement"
                    ),
                    "icon": badge.get("icon") or "",
                    "stars": badge.get("stars")
                })
            else:
                normalized.append({
                    "name": str(badge),
                    "icon": "",
                    "stars": None
                })

    return normalized


def normalize_badge_icons(badges, platform):
    """Convert relative badge image paths into absolute URLs."""

    if platform == "leetcode":
        base_url = "https://leetcode.com"

        for badge in badges:
            icon = badge.get("icon", "")

            if icon.startswith("/"):
                badge["icon"] = base_url + icon

    return badges


def fetch_all_platforms():
    services = {
        "leetcode": fetch_leetcode_data,
        "codeforces": fetch_codeforces_data,
        "codechef": fetch_codechef_data,
        "hackerrank": fetch_hackerrank_data,
        "skillrack": fetch_skillrack_data,
    }

    results = {}

    for platform, fetch_function in services.items():

        try:
            data = fetch_function()

            if data.get("status") != "success":
                raise ValueError(
                    data.get("error", "Unable to retrieve platform data")
                )

            data["badges"] = normalize_badges(
                data.get("badges", [])
            )

            data["badges"] = normalize_badge_icons(
                data["badges"],
                platform
            )

            # LeetCode: retain its difficulty-wise statistics.
            if platform == "leetcode":
                data["total_solved"] = data.get("total_solved")
                data["easy"] = data.get("easy")
                data["medium"] = data.get("medium")
                data["hard"] = data.get("hard")
                data["contest_rating"] = data.get("contest_rating")
                data["active_days"] = data.get("active_days")

            # Codeforces: no Easy / Medium / Hard classification.
            elif platform == "codeforces":
                data["total_solved"] = data.get(
                    "total_solved",
                    data.get("problems_solved")
                )

                data["contest_rating"] = data.get(
                    "contest_rating",
                    data.get("rating")
                )

                data["max_rating"] = data.get("max_rating")
                data["rank"] = data.get("rank")
                data["max_rank"] = data.get("max_rank")

                data["contests_participated"] = data.get(
                    "contests_participated"
                )

                # Remove difficulty fields from Codeforces.
                data.pop("easy", None)
                data.pop("medium", None)
                data.pop("hard", None)

            # CodeChef: use only the available profile statistics.
            elif platform == "codechef":
                data["total_solved"] = data.get("total_solved")
                data["contest_rating"] = data.get("contest_rating")
                data["active_days"] = data.get("active_days")

            # HackerRank: badge-based achievements.
            elif platform == "hackerrank":
                data["badges"] = data.get("badges", [])

            # Skillrack: programming-specific statistics.
            elif platform == "skillrack":
                data["total_solved"] = data.get("total_solved")
                data["rank"] = data.get("rank")

            results[platform] = data

        except Exception as error:
            results[platform] = {
                "username": "",
                "status": "error",
                "error": str(error),
                "badges": []
            }

    return results
