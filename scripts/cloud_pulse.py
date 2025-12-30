import feedparser
from datetime import datetime, timedelta
from pathlib import Path
import re

README = Path("README.md")
START = r"<!--\s*CLOUD-PULSE:START\s*-->"
END   = r"<!--\s*CLOUD-PULSE:END\s*-->"

SOURCES = {
    "AWS": "https://aws.amazon.com/about-aws/whats-new/recent/feed/",
    "Azure": "https://azure.microsoft.com/en-us/updates/feed/",
    "GCP": "https://cloud.google.com/feeds/gcp-release-notes.xml",
}

DAYS = 7

def count_recent(feed_url):
    feed = feedparser.parse(feed_url)
    since = datetime.utcnow() - timedelta(days=DAYS)
    count = 0
    for e in feed.entries:
        if hasattr(e, "published_parsed") and e.published_parsed:
            published = datetime(*e.published_parsed[:6])
            if published >= since:
                count += 1
    return count

def main():
    lines = []
    for name, url in SOURCES.items():
        try:
            c = count_recent(url)
            lines.append(f"- {name}: {c} updates (7d)")
        except Exception:
            lines.append(f"- {name}: unavailable")

    content = README.read_text(encoding="utf-8")
    block = "\n".join(lines)

    new, n = re.subn(
        rf"{START}.*?{END}",
        f"<!-- CLOUD-PULSE:START -->\n{block}\n<!-- CLOUD-PULSE:END -->",
        content,
        flags=re.DOTALL,
    )
    if n == 0:
        raise RuntimeError("CLOUD-PULSE markers not found")

    README.write_text(new, encoding="utf-8")

if __name__ == "__main__":
    main()
