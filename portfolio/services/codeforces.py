
import requests
import time
from datetime import datetime, timezone

BASE_URL = "https://codeforces.com/api"
USERNAME = "Abinavbalu"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_codeforces_data():
    try:
        # 1. Fetch user profile
        profile_response = requests.get(
            f"{BASE_URL}/user.info",
            params={"handles": USERNAME},
            headers=HEADERS,
            timeout=20
        )
        profile_response.raise_for_status()

        profile_result = profile_response.json()

        if profile_result.get("status") != "OK":
            raise ValueError("Unable to fetch Codeforces profile")

        profile = profile_result["result"][0]

        # 2. Fetch contest history
        rating_response = requests.get(
            f"{BASE_URL}/user.rating",
            params={"handle": USERNAME},
            headers=HEADERS,
            timeout=20
        )
        rating_response.raise_for_status()

        rating_result = rating_response.json()

        if rating_result.get("status") != "OK":
            raise ValueError("Unable to fetch contest history")

        contests = rating_result["result"]

        # 3. Fetch ALL submissions in batches
        submissions = []
        offset = 1
        batch_size = 1000

        while True:
            submission_response = requests.get(
                f"{BASE_URL}/user.status",
                params={
                    "handle": USERNAME,
                    "from": offset,
                    "count": batch_size
                },
                headers=HEADERS,
                timeout=30
            )
            submission_response.raise_for_status()

            submission_result = submission_response.json()

            if submission_result.get("status") != "OK":
                raise ValueError("Unable to fetch submissions")

            batch = submission_result["result"]

            if not batch:
                break

            submissions.extend(batch)

            if len(batch) < batch_size:
                break

            offset += batch_size
            time.sleep(1)

        # 4. Count unique accepted problems
        solved_problems = set()

        for submission in submissions:
            if submission.get("verdict") == "OK":
                problem = submission.get("problem", {})

                contest_id = submission.get("contestId")
                index = problem.get("index")

                if contest_id is not None and index:
                    solved_problems.add((contest_id, index))

        # 5. Calculate active days
        active_dates = set()

        for submission in submissions:
            timestamp = submission.get("creationTimeSeconds")

            if timestamp is not None:
                active_date = datetime.fromtimestamp(
                    timestamp,
                    timezone.utc
                ).date()

                active_dates.add(active_date)

        # 6. Prepare rating information
        current_rating = profile.get("rating")
        maximum_rating = profile.get("maxRating")

        current_rank = profile.get("rank", "Unrated")
        maximum_rank = profile.get("maxRank", "Unrated")

        return {
            "username": USERNAME,

            "total_solved": len(solved_problems),

            "contest_rating": current_rating,
            "max_rating": maximum_rating,

            "rank": current_rank,
            "max_rank": maximum_rank,

            "contests_participated": len(contests),

            "active_days": len(active_dates),

            "profile_url": (
                f"https://codeforces.com/profile/{USERNAME}"
            ),

            "status": "success"
        }

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        IndexError
    ) as error:

        return {
            "username": USERNAME,
            "status": "error",
            "error": str(error)
        }
