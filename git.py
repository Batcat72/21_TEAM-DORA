import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

app = Flask(__name__)

def get_repo_info(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}"

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

    # Open PRs
    pr_url = f"{url}/pulls?state=open"
    pr_response = requests.get(pr_url, headers=HEADERS)
    if pr_response.status_code == 200:
        prs = pr_response.json()
        report["Open PRs Count"] = len(prs)
        report["Open PRs Titles"] = [pr["title"] for pr in prs]
    else:
        report["Open PRs Count"] = "N/A"
        report["Open PRs Titles"] = []

    # Languages
    lang_url = f"{url}/languages"
    lang_response = requests.get(lang_url, headers=HEADERS)
    if lang_response.status_code == 200:
        report["Languages Used"] = list(lang_response.json().keys())
    else:
        report["Languages Used"] = []

    return report


@app.route("/", methods=["GET", "POST"])
def index():
    report_html = ""
    repo_name = ""

    if request.method == "POST":
        repo_name = request.form.get("repo_name", "").strip()
        report = get_repo_info(repo_name)

        if "error" in report:
            report_html = f"<div class='error'>{report['error']}</div>"
        else:
            rows = ""
            for key, value in report.items():
                if isinstance(value, list):
                    value = "<ul>" + "".join(f"<li>{v}</li>" for v in value) + "</ul>"
                rows += f"<tr><th>{key}</th><td>{value}</td></tr>"

            report_html = f"""
            <h2>Report for: <a href="{report['Repo URL']}" target="_blank">{report['Full Name']}</a></h2>
            <table>
                {rows}
            </table>
            """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GitHub OSINT Tool</title>
        <style>
            body {{
                background: #0b1320;
                color: #00f7ff;
                font-family: Arial;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 40px;
            }}
            .box {{
                width: 800px;
                background: #050b17;
                padding: 25px 30px;
                border-radius: 12px;
                box-shadow: 0 0 25px rgba(0,247,255,0.4);
            }}
            h1 {{
                text-align: center;
                margin-bottom: 20px;
            }}
            input {{
                width: 70%;
                padding: 10px;
                border-radius: 6px;
                border: none;
                margin-right: 10px;
            }}
            button {{
                padding: 10px 16px;
                border-radius: 6px;
                border: none;
                background: #00f7ff;
                font-weight: bold;
                cursor: pointer;
            }}
            button:hover {{
                background: #00c4cc;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                font-size: 14px;
            }}
            th, td {{
                border: 1px solid rgba(0,247,255,0.2);
                padding: 8px;
                text-align: left;
            }}
            th {{
                color: #fff;
                width: 200px;
            }}
            a {{
                color: #00f7ff;
            }}
            .error {{
                color: red;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="box">
            <h1>GitHub Repo OSINT Tool</h1>
            <form method="POST">
                <input type="text" name="repo_name" placeholder="owner/repo" value="{repo_name}" required>
                <button type="submit">Fetch Report</button>
            </form>
            {report_html}
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)
