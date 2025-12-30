import requests
import re
from pathlib import Path
from datetime import date, datetime, timezone

README = Path("README.md")

START_RE = r"<!--\s*TECH-PULSE:START\s*-->"
END_RE   = r"<!--\s*TECH-PULSE:END\s*-->"

DAYS_NEW = 30
HEADERS = {"User-Agent": "tech-pulse-bot"}

def latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    r = requests.get(url, headers=HEADERS, timeout=10)

    if r.status_code == 404:
        tags = requests.get(
            f"https://api.github.com/repos/{repo}/tags",
            headers=HEADERS,
            timeout=10
        )
        tags.raise_for_status()
        return tags.json()[0]["name"], None

    r.raise_for_status()
    data = r.json()
    published = datetime.fromisoformat(data["published_at"].replace("Z", "+00:00"))
    return data["tag_name"], published


def status_icon(published_at):
    if not published_at:
        return "🟢"
    days = (datetime.now(timezone.utc) - published_at).days
    return "🟡" if days <= DAYS_NEW else "🟢"


def main():
    tools = {
        "Terraform": "hashicorp/terraform",
        "Terragrunt": "gruntwork-io/terragrunt",
        "Kubernetes": "kubernetes/kubernetes",
        "Docker": "docker/docker-ce",
        "AWS CLI": "aws/aws-cli",
        "Python": "python/cpython",
    }

    lines = []
    for name, repo in tools.items():
        try:
            tag, published = latest_release(repo)
            lines.append(f"- {status_icon(published)} {name:<14}: {tag}")
        except Exception:
            lines.append(f"- 🔴 {name:<14}: unavailable")

    content = README.read_text(encoding="utf-8")

    block = "\n".join(lines) + f"\n\n_Last update: {date.today()}_"

    new_content, count = re.subn(
        rf"{START_RE}.*?{END_RE}",
        f"<!-- TECH-PULSE:START -->\n{block}\n<!-- TECH-PULSE:END -->",
        content,
        flags=re.DOTALL,
    )

    if count == 0:
        raise RuntimeError("TECH-PULSE markers not found in README")

    README.write_text(new_content, encoding="utf-8")
    print("README updated successfully")


if __name__ == "__main__":
    main()
