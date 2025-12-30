import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT = Path("assets/pulse/security.svg")
HEADERS = {"User-Agent": "security-pulse-bot"}

DAYS = 7
ADVISORIES_API = "https://api.github.com/advisories"

def advisories_last_days():
    since = (datetime.now(timezone.utc) - timedelta(days=DAYS)).isoformat()
    params = {
        "since": since,
        "per_page": 100,
    }
    r = requests.get(ADVISORIES_API, headers=HEADERS, params=params, timeout=10)
    r.raise_for_status()
    return len(r.json())

def status_icon(count):
    if count == 0:
        return "🟢"
    if count < 10:
        return "🟡"
    return "🔴"

def main():
    try:
        count = advisories_last_days()
        icon = status_icon(count)
        line = f"{icon} Advisories: {count} (7d)"
    except Exception:
        line = "🟠 CVE feed unavailable"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="360" height="150">
  <rect width="100%" height="100%" rx="10" fill="#0f172a"/>
  <text x="20" y="30" fill="#e5e7eb" font-size="16" font-family="Arial">
    🔐 Security Pulse
  </text>
  <text x="20" y="70" fill="#e5e7eb" font-size="13" font-family="Arial">
    {line}
  </text>
  <text x="20" y="95" fill="#9ca3af" font-size="12" font-family="Arial">
    Source: GitHub Security Advisories
  </text>
  <text x="20" y="140" fill="#9ca3af" font-size="11" font-family="Arial">
    Updated: {datetime.utcnow().date()}
  </text>
</svg>
"""
    OUT.write_text(svg, encoding="utf-8")

if __name__ == "__main__":
    main()
