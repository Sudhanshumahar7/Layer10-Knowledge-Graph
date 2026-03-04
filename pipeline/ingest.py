import os
import requests
import json
from dotenv import load_dotenv

# .env is one level up (project root)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

REPO_OWNER = "langchain-ai"
REPO_NAME = "langchain"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def fetch_issues(limit=50):
    print(f"Fetching exactly {limit} closed issues from {REPO_OWNER}/{REPO_NAME}...")
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    
    corpus = []
    page = 1
    
    while len(corpus) < limit:
        params = {
            "state": "closed",
            "per_page": min(100, limit - len(corpus) + 20), 
            "sort": "updated",
            "direction": "desc",
            "page": page
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        issues = response.json()
        
        if not issues:
            print("No more issues found.")
            break 
            
        for issue in issues:
            if len(corpus) >= limit:
                break
                
            if "pull_request" in issue:
                continue
                
            issue_data = {
                "id": str(issue["number"]),
                "url": issue["html_url"],
                "title": issue["title"],
                "state": issue["state"],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "labels": [label["name"] for label in issue.get("labels", [])],
                "body": issue["body"] or "",
                "comments": []
            }
            
            if issue.get("comments", 0) > 0:
                comments_url = issue["comments_url"]
                c_resp = requests.get(comments_url, headers=headers)
                if c_resp.status_code == 200:
                    for c in c_resp.json():
                        issue_data["comments"].append({
                            "id": str(c["id"]),
                            "author": c["user"]["login"],
                            "body": c["body"] or "",
                            "created_at": c["created_at"]
                        })
            
            corpus.append(issue_data)
            print(f"Fetching issue {len(corpus)}/{limit}...")
            
        page += 1
        
    return corpus

if __name__ == "__main__":
    # Output goes to ../data/ relative to this script
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    data = fetch_issues(limit=50)
    
    out_path = os.path.join(data_dir, "corpus.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    print(f"Saved corpus to {out_path}")
