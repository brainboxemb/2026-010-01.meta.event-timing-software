#!/usr/bin/env bash
set -euo pipefail

rm -rf bld/sphinx-needs
mkdir -p   bld/sphinx-needs/source/docs/architecture-assets   bld/sphinx-needs/diagrams

cp docs/_sphinx-needs/conf.py bld/sphinx-needs/source/conf.py
cp docs/_sphinx-needs/schemas.json bld/sphinx-needs/source/schemas.json
cp docs/30-UC-system-use-cases.md bld/sphinx-needs/source/docs/
cp docs/41-01-SSD-timing-application-specification-document.md bld/sphinx-needs/source/docs/
cp docs/32-03-ISD-application-control-status.md bld/sphinx-needs/source/docs/
cp docs/32-04-ISD-web-interface.md bld/sphinx-needs/source/docs/
cp docs/32-05-ISD-timingdata-interchange.md bld/sphinx-needs/source/docs/
cp docs/33-05-IDD-timingdata-interchange.md bld/sphinx-needs/source/docs/
cp docs/61-01-VTS-timing-application-verification-test-specification.md bld/sphinx-needs/source/docs/
cp docs/_diagrams/layered-architecture.yaml bld/sphinx-needs/diagrams/
cp -L bld/docs/assets/architecture/*.svg bld/sphinx-needs/source/docs/architecture-assets/

python - <<'PY'
from pathlib import Path
import re

for path in Path("bld/sphinx-needs/source/docs").glob("*.md"):
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"(?:\.\./)+raw/prod/docs/assets/architecture/",
        "architecture-assets/",
        text,
    )
    path.write_text(text, encoding="utf-8")
PY

cat > bld/sphinx-needs/source/index.md <<'EOF'
# Migration 013 engineering traceability

~~~{toctree}
:maxdepth: 2

docs/30-UC-system-use-cases
docs/41-01-SSD-timing-application-specification-document
docs/32-03-ISD-application-control-status
docs/32-04-ISD-web-interface
docs/32-05-ISD-timingdata-interchange
docs/33-05-IDD-timingdata-interchange
docs/61-01-VTS-timing-application-verification-test-specification
~~~
EOF

sphinx-build -W --keep-going -b needs   bld/sphinx-needs/source   bld/sphinx-needs/needs

sphinx-build -W --keep-going -b html   bld/sphinx-needs/source   bld/sphinx-needs/html
