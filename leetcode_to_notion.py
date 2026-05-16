"""
LeetCode → Notion Auto-Sync Script
===================================
Works both locally (.env file) AND in GitHub Actions (env secrets).

For local setup, see SETUP_GUIDE.md
For GitHub Actions setup (recommended), see GITHUB_ACTIONS_GUIDE.md
"""

import os
import requests
from datetime import datetime

# Try to load .env file if it exists (for local runs).
# In GitHub Actions, env vars are set directly so this is skipped silently.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============ CONFIG ============
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
LEETCODE_CSRF = os.getenv("LEETCODE_CSRF")
LEETCODE_USERNAME = os.getenv("LEETCODE_USERNAME")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# "Me" or "Friend" — set via env var
SOLVED_BY = os.getenv("SOLVED_BY", "Me")

# How many recent submissions to fetch (LeetCode allows up to 20)
LIMIT = 20

# ============ LEETCODE API ============

def fetch_recent_submissions():
    """Fetch recent ACCEPTED submissions from LeetCode."""
    url = "https://leetcode.com/graphql/"
    
    query = """
    query recentAcSubmissions($username: String!, $limit: Int!) {
        recentAcSubmissionList(username: $username, limit: $limit) {
            id
            title
            titleSlug
            timestamp
        }
    }
    """
    
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={LEETCODE_CSRF}",
        "x-csrftoken": LEETCODE_CSRF,
        "Referer": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0"
    }
    
    payload = {
        "query": query,
        "variables": {"username": LEETCODE_USERNAME, "limit": LIMIT}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["data"]["recentAcSubmissionList"]


def fetch_problem_details(title_slug):
    """Fetch difficulty, number, and topics for a problem."""
    url = "https://leetcode.com/graphql/"
    
    query = """
    query questionData($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionFrontendId
            difficulty
            topicTags {
                name
            }
        }
    }
    """
    
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={LEETCODE_CSRF}",
        "x-csrftoken": LEETCODE_CSRF,
        "Referer": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0"
    }
    
    payload = {"query": query, "variables": {"titleSlug": title_slug}}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["data"]["question"]


# ============ NOTION API ============

def check_existing(problem_number):
    """Check if a problem is already in Notion (avoid duplicates)."""
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "filter": {
            "and": [
                {"property": "Number", "number": {"equals": int(problem_number)}},
                {"property": "Solved By", "multi_select": {"contains": SOLVED_BY}}
            ]
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return len(response.json()["results"]) > 0


def add_to_notion(problem):
    """Add a solved problem to the Notion database."""
    url = "https://api.notion.com/v1/pages"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    solved_date = datetime.fromtimestamp(int(problem["timestamp"])).date().isoformat()
    leetcode_url = f"https://leetcode.com/problems/{problem['titleSlug']}/"
    
    properties = {
        "Problem Name": {"title": [{"text": {"content": problem["title"]}}]},
        "Number": {"number": int(problem["questionFrontendId"])},
        "Difficulty": {"select": {"name": problem["difficulty"]}},
        "Solved By": {"multi_select": [{"name": SOLVED_BY}]},
        "Date Solved": {"date": {"start": solved_date}},
        "LeetCode URL": {"url": leetcode_url},
        "Topic": {"multi_select": [{"name": tag} for tag in problem["topics"][:5]]}
    }
    
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": properties
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to add {problem['title']}: {response.text}")
        return False
    return True


# ============ MAIN ============

def main():
    print(f"🚀 Syncing LeetCode → Notion for {LEETCODE_USERNAME} (as '{SOLVED_BY}')")
    print("─" * 50)
    
    missing = [k for k, v in {
        "LEETCODE_SESSION": LEETCODE_SESSION,
        "LEETCODE_CSRF": LEETCODE_CSRF,
        "LEETCODE_USERNAME": LEETCODE_USERNAME,
        "NOTION_TOKEN": NOTION_TOKEN,
        "NOTION_DATABASE_ID": NOTION_DATABASE_ID
    }.items() if not v]
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("   Check your .env file (local) or repo secrets (GitHub Actions).")
        exit(1)
    
    try:
        submissions = fetch_recent_submissions()
    except Exception as e:
        print(f"❌ Failed to fetch from LeetCode: {e}")
        print("   Your session cookie may have expired. Refresh it!")
        exit(1)
    
    if not submissions:
        print("ℹ️  No recent accepted submissions found. Time to solve some!")
        return
    
    print(f"📥 Found {len(submissions)} recent accepted submissions")
    
    added = 0
    skipped = 0
    failed = 0
    
    for sub in submissions:
        try:
            details = fetch_problem_details(sub["titleSlug"])
            problem_data = {
                "title": sub["title"],
                "titleSlug": sub["titleSlug"],
                "timestamp": sub["timestamp"],
                "questionFrontendId": details["questionFrontendId"],
                "difficulty": details["difficulty"],
                "topics": [tag["name"] for tag in details["topicTags"]]
            }
            
            if check_existing(problem_data["questionFrontendId"]):
                print(f"⏭️  Skipped (already exists): {problem_data['title']}")
                skipped += 1
                continue
            
            if add_to_notion(problem_data):
                difficulty_emoji = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(
                    problem_data["difficulty"], "⚪"
                )
                print(f"✅ Added: {difficulty_emoji} #{problem_data['questionFrontendId']} {problem_data['title']}")
                added += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Error processing {sub['title']}: {e}")
            failed += 1
    
    print("─" * 50)
    print(f"📊 Summary: {added} added | {skipped} skipped | {failed} failed")
    print(f"🔥 Keep grinding!")


if __name__ == "__main__":
    main()
