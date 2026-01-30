import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
def get_repo_info(repo_full_name):
    base_url = "https://api.github.com/repos/"
    url = f"{base_url}{repo_full_name}"

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return {"error": f"Failed to fetch repo: {response.status_code}"}

    data = response.json()
    
    report = {
        "Full Name": data.get("full_name"),
        "Description": data.get("description"),
        "Owner": data.get("owner", {}).get("login"),
        "Private": data.get("private"),
        "Fork": data.get("fork"),
        "Stars": data.get("stargazers_count"),
        "Forks": data.get("forks_count"),
        "Open Issues": data.get("open_issues_count"),
        "Watchers": data.get("watchers_count"),
        "Default Branch": data.get("default_branch"),
        "Created At": data.get("created_at"),
        "Updated At": data.get("updated_at"),
        "Pushed At": data.get("pushed_at"),
        "Language": data.get("language"),
        "License": data.get("license", {}).get("name") if data.get("license") else None,
        "Repo URL": data.get("html_url")
    }
    pr_url = f"{url}/pulls?state=open"
    pr_response = requests.get(pr_url, headers=HEADERS)
    if pr_response.status_code == 200:
        prs = pr_response.json()
        report["Open PRs Count"] = len(prs)
        report["Open PRs Titles"] = [pr["title"] for pr in prs]
    else:
        report["Open PRs Count"] = "N/A"
        report["Open PRs Titles"] = []
    lang_url = f"{url}/languages"
    lang_response = requests.get(lang_url, headers=HEADERS)
    if lang_response.status_code == 200:
        report["Languages Used"] = list(lang_response.json().keys())
    else:
        report["Languages Used"] = []

    return report
if __name__ == "__main__":
    repo_name = input("Enter GitHub repo (owner/repo): ").strip()
    osint_report = get_repo_info(repo_name)

    print("\n=== GitHub Repo OSINT Report ===")
    for key, value in osint_report.items():
        print(f"{key}: {value}")