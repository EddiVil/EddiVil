import requests
from datetime import datetime, timedelta
from pathlib import Path
import re

README = Path("README.md")
START = r"<!--\s*SECURITY-PULSE:START\s*-->"
END   = r"<!--\s*SECURITY-PULSE:END\s*-->"

NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
WINDOW_HOURS = 24

def fetch_counts():
    since = (datetime.utcnow() - timedelta(hours=WINDOW_HOURS)).isoformat() + "Z"
    params = {
        "pubStartDate": since,
        "resultsPerPage": 2000
    }
    r = requests.get(NVD_URL, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    critical = high = 0
    for v in data.get("vulnerabilities", []):
        metrics = v["cve"].get("metrics", {})
        for k in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            if k in metrics:
                sev = metrics[k][0]["cvssData"]["baseSeverity"]
                if sev == "CRITICAL":
                    critical += 1
                elif sev == "HIGH":
                    high += 1
                break
    return critical, high

def main():
    try:
        critical, high = fetch_counts()
        lines = [
            f"- Critical CVEs (24h): {critical} 🔴",
            f"- High CVEs (24h): {high} 🟠",
        ]
    except Exception:
        lines = ["- CVE feed: unavailable"]

    content = README.read_text(encoding="utf-8")
    block = "\n".join(lines)

    new, n = re.subn(
        rf"{START}.*?{END}",
        f"<!-- SECURITY-PULSE:START -->\n{block}\n<!-- SECURITY-PULSE:END -->",
        content,
        flags=re.DOTALL,
    )
    if n == 0:
        raise RuntimeError("SECURITY-PULSE markers not found")

    README.write_text(new, encoding="utf-8")

if __name__ == "__main__":
    main()
