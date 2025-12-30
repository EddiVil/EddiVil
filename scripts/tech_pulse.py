import requests
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("assets/pulse/tech.svg")
HEADERS = {"User-Agent": "tech-pulse-bot"}

TOOLS = {
    "Terraform": "hashicorp/terraform",
    "Terragrunt": "gruntwork-io/terragrunt",
    "Kubernetes": "kubernetes/kubernetes",
    "Docker": "docker/docker-ce",
    "AWS CLI": "aws/aws-cli",
    "Python": "python/cpython",
}

DAYS_NEW = 30

def latest_release(repo):
    r = requests.get(
        f"https://api.github.com/repos/{repo}/releases/latest",
        headers=HEADERS,
        timeout=10,
    )
    if r.status_code == 404:
        tags = requests.get(
            f"https://api.github.com/repos/{repo}/tags",
            headers=HEADERS,
            timeout=10,
        )
        tags.raise_for_status()
        return tags.json()[0]["name"], None

    r.raise_for_status()
    data = r.json()
    published = datetime.fromisoformat(
        data["published_at"].replace("Z", "+00:00")
    )
    return data["tag_name"], published

def status_icon(published):
    if not published:
        return "🟢"
    age = (datetime.now(timezone.utc) - published).days
    return "🟡" if age <= DAYS_NEW else "🟢"

def main():
    lines = []
    y = 55

    for name, repo in TOOLS.items():
        try:
            tag, published = latest_release(repo)
            icon = status_icon(published)
            lines.append(
                f'<text x="20" y="{y}" fill="#e5e7eb" font-size="13" font-family="Arial">'
                f'{icon} {name}: {tag}'
                f'</text>'
            )
        except Exception:
            lines.append(
                f'<text x="20" y="{y}" fill="#fbbf24" font-size="13" font-family="Arial">'
                f'🟠 {name}: unavailable'
                f'</text>'
            )
        y += 18

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="360" height="150">
  <rect width="100%" height="100%" rx="10" fill="#0f172a"/>
  <text x="20" y="30" fill="#e5e7eb" font-size="16" font-family="Arial">
    📡 Tech Pulse
  </text>
  {''.join(lines)}
  <text x="20" y="140" fill="#9ca3af" font-size="11" font-family="Arial">
    Updated: {datetime.utcnow().date()}
  </text>
</svg>
"""

    OUT.write_text(svg, encoding="utf-8")

if __name__ == "__main__":
    main()
