import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT = Path("assets/pulse/cloud.svg")
HEADERS = {"User-Agent": "cloud-pulse-bot"}

REPOS = {
    "AWS": "aws/aws-cli",
    "Azure": "Azure/azure-cli",
    "GCP": "google-cloud-sdk/google-cloud-cli",
}

DAYS = 7

def commits_last_days(repo):
    since = (datetime.now(timezone.utc) - timedelta(days=DAYS)).isoformat()
    url = f"https://api.github.com/repos/{repo}/commits?since={since}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return len(r.json())

def status_icon(count):
    if count == 0:
        return "🟢"
    if count < 5:
        return "🟡"
    return "🔴"

def main():
    y = 55
    lines = []

    for name, repo in REPOS.items():
        try:
            count = commits_last_days(repo)
            icon = status_icon(count)
            lines.append(
                f'<text x="20" y="{y}" fill="#e5e7eb" font-size="13" font-family="Arial">'
                f'{icon} {name}: {count} updates (7d)'
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
    ☁️ Cloud Pulse
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
