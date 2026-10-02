"""Check relative Markdown file links; remote URLs and anchors are not checked."""

import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
errors = []
for path in [root / "README.md", root / "CONTRIBUTING.md", *sorted((root / "docs").rglob("*.md"))]:
    for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        if "://" in target or target.startswith("#"):
            continue
        if not (path.parent / target.split("#")[0]).exists():
            errors.append(f"{path.relative_to(root)}: {target}")
if errors:
    raise SystemExit("Broken links:\n" + "\n".join(errors))
print("Relative documentation links OK (remote URLs/anchors not checked)")
