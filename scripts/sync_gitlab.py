"""
Sync and monitor MoveSense issues from FH Kufstein GitLab repository.
Project: konraddaniel/movesense (ID: 8519)
"""

import requests
import json
from pathlib import Path

GITLAB_TOKEN = "glpat-iNdmd9wqNR5dTj6PPndYMG86MQp1Omx3CA.01.0y0a97l4r"
BASE_URL = "https://gitlab.web.hok.ac.at/api/v4"
PROJECT_ID = 8519
HEADERS = {"PRIVATE-TOKEN": GITLAB_TOKEN}


def get_all_issues():
    url = f"{BASE_URL}/projects/{PROJECT_ID}/issues?state=all&per_page=100"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_boards():
    url = f"{BASE_URL}/projects/{PROJECT_ID}/boards"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def print_dashboard():
    print("=" * 70)
    print("📊 MOVESENSE GITLAB DASHBOARD (FH Kufstein)")
    print("   Repository: https://gitlab.web.hok.ac.at/konraddaniel/movesense")
    print("=" * 70)

    issues = get_all_issues()

    opened = [i for i in issues if i.get("state") == "opened"]
    closed = [i for i in issues if i.get("state") == "closed"]

    print(f"\n🔹 Total de Issues: {len(issues)} (Abertos: {len(opened)} | Fechados: {len(closed)})\n")

    print("📌 ISSUES ABERTOS (EM ANDAMENTO / BACKLOG):")
    for i in opened:
        iid = i.get("iid")
        title = i.get("title")
        labels = i.get("labels", [])
        assignees = [a.get("name") for a in i.get("assignees", [])]
        assignee_str = ", ".join(assignees) if assignees else "⚠️ NÃO ATRIBUÍDO"
        labels_str = f"[{', '.join(labels)}]" if labels else ""
        print(f"  #{iid:<2} | {assignee_str:<20} | {title} {labels_str}")

    print("\n✅ ISSUES CONCLUÍDOS:")
    for i in closed:
        iid = i.get("iid")
        title = i.get("title")
        assignees = [a.get("name") for a in i.get("assignees", [])]
        assignee_str = ", ".join(assignees) if assignees else "None"
        print(f"  #{iid:<2} | {assignee_str:<20} | {title}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print_dashboard()
