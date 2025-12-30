import requests
from pathlib import Path
from datetime import date, datetime, timezone

README = Path("README.md")

START = "<!-- TECH-PULSE:START -->"
END = "<!-- TECH-PULSE:END -->"
DAYS_NEW = 30

HEADERS = {
    "User-Agent": "tech-pulse-bot"
}

def latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    r = requests.get(url, headers=HEADERS, timeout=10)

    if r.status_code == 404:
        # fallback to tags
        tags = requests.get(
            f"https://api.github.com/repos/{repo}/tags",
            headers=HEADERS,
            timeout=10
        )
        tags.raise_for_status()
        tag = tags.json()[0]["name"]
        return tag, None

    r.raise_for_status()
    data = r.json()
    tag = data["tag_name"]
    published = datetime.fromisoformat(data["published_at"].replace("Z", "+00:00"))
    return tag, published


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
            icon = status_icon(published)
            lines.append(f"- {icon} {name:<14}: {tag}")
        except Exception as e:
            lines.append(f"- 🔴 {name:<14}: unavailable")

    content = README.read_text(encoding="utf-8")

    block = (
        f"{START}\n"
        + "\n".join(lines) +
        f"\n{END}\n\n_Last update: {date.today()}_"
    )

    if START not in content or END not in content:
        raise RuntimeError("TECH-PULSE markers not found in README")

    before = content.split(START)[0]
    after = content.split(END)[1]

    updated = before + block + after

    if updated != content:
        README.write_text(updated, encoding="utf-8")
        print("README updated")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
