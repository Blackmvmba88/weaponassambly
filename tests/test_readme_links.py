"""Regression guard for local Markdown links in the repository README."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def test_readme_local_links_resolve():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    local_links = []
    for destination in LINK_RE.findall(readme):
        path = destination.split("#", maxsplit=1)[0]
        if not path or path.startswith(("https://", "http://", "mailto:")):
            continue
        local_links.append(path)

    assert local_links, "README.md should link to local documentation"
    missing = sorted(path for path in local_links if not (ROOT / path).exists())
    assert not missing, f"Broken local README links: {', '.join(missing)}"
