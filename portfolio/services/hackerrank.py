
USERNAME = "abibalu9001"

PROFILE_URL = f"https://www.hackerrank.com/profile/{USERNAME}"


def fetch_hackerrank_data():
    badges = [
        {
            "name": "Python",
            "stars": 5,
            "icon": ""
        },
        {
            "name": "C++",
            "stars": 4,
            "icon": ""
        }
    ]

    return {
        "username": USERNAME,
        "badges": badges,
        "badge_count": len(badges),
        "certifications": [],
        "profile_url": PROFILE_URL,
        "status": "success"
    }
