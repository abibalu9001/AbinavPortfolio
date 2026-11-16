
import json
import requests

USERNAME = "Abinavbalu"

URL = "https://leetcode.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "Referer": f"https://leetcode.com/u/{USERNAME}/",
    "Origin": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0"
}


def fetch_leetcode_data():

    query = """
    query userProfile($username: String!, $year: Int!) {
        matchedUser(username: $username) {
            username

            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                    submissions
                }
            }

            badges {
                id
                name
                shortName
                displayName
                icon
            }

            userCalendar(year: $year) {
                activeYears
                streak
                totalActiveDays
                submissionCalendar
            }
        }

        userContestRanking(username: $username) {
            rating
            globalRanking
            topPercentage
            attendedContestsCount
        }
    }
    """

    try:
        response = requests.post(
            URL,
            headers=HEADERS,
            json={
                "query": query,
                "variables": {
                    "username": USERNAME,
                    "year": 2026
                }
            },
            timeout=25
        )

        response.raise_for_status()
        result = response.json()

        if result.get("errors"):
            raise ValueError(str(result["errors"]))

        data = result["data"]

        user = data.get("matchedUser")
        contest = data.get("userContestRanking")

        if not user:
            raise ValueError("LeetCode profile not found")

        # Difficulty breakdown
        difficulty = {
            item["difficulty"]: item["count"]
            for item in user["submitStats"]["acSubmissionNum"]
        }

        easy = difficulty.get("Easy", 0)
        medium = difficulty.get("Medium", 0)
        hard = difficulty.get("Hard", 0)

        # Badges
        badges = [
            {
                "name": badge.get("displayName") or badge.get("name"),
                "icon": badge.get("icon")
            }
            for badge in user.get("badges", [])
        ]

        # Activity calendar
        calendar = user.get("userCalendar") or {}

        submission_calendar = json.loads(
            calendar.get("submissionCalendar") or "{}"
        )

        return {
            "username": user["username"],
            "total_solved": easy + medium + hard,
            "easy": easy,
            "medium": medium,
            "hard": hard,

            "contest_rating": (
                round(contest["rating"], 2)
                if contest and contest.get("rating") is not None
                else None
            ),

            "global_ranking": (
                contest.get("globalRanking") if contest else None
            ),

            "contests_attended": (
                contest.get("attendedContestsCount")
                if contest else 0
            ),

            "active_days": calendar.get("totalActiveDays", 0),
            "current_streak": calendar.get("streak", 0),

            "badges": badges,
            "badge_count": len(badges),

            "submission_calendar": submission_calendar,

            "profile_url": (
                f"https://leetcode.com/u/{USERNAME}/"
            ),

            "status": "success"
        }

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError
    ) as error:

        return {
            "username": USERNAME,
            "status": "error",
            "error": str(error)
        }
