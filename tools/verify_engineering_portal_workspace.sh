#!/usr/bin/env bash
# Engineering Portal browser/workspace verification.
#
# Kept outside GitHub Actions so the exact verification behaviour is ordinary,
# reviewable repository code and can also be invoked locally after portal build.
set -euo pipefail
python -m http.server 8765 \
  --bind 127.0.0.1 \
  --directory bld/engineering-portal/site \
  > bld/engineering-portal/browser-server.log 2>&1 &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT

python - <<'PY'
import time
import urllib.request

url = "http://127.0.0.1:8765/explorer/"
for _ in range(20):
    try:
        urllib.request.urlopen(url, timeout=1).read(1)
        break
    except Exception:
        time.sleep(0.25)
else:
    raise SystemExit("engineering portal preview server did not become ready")
PY

chrome="$(command -v google-chrome || command -v google-chrome-stable || command -v chromium || true)"
if [ -z "$chrome" ]; then
  echo "No Chrome/Chromium executable available on runner"
  exit 1
fi

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/workspace/?object=IF05-REQ-007&compare=SI01-REQ-045" \
  > bld/engineering-portal/browser-workspace-IF05-REQ-007.html

grep -q '<code>IF05-REQ-007</code>' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q '<code>SI01-REQ-045</code>' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'Committed record immutability' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'Reference TimingData representation support' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'A committed TimingData record shall not be modified or renumbered' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'data-compare-object-id="SI01-REQ-045"' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'Selected object' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'Compared object' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'role="tree" data-eng-object-tree' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'data-eng-tree-toggle' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'aria-expanded="true"' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
! grep -q '<details class="eng-tree-group"' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'data-eng-tree-search' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'data-eng-tree-type' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'data-eng-tree-count' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'Requirement (' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'data-workspace-root-id="IF05-REQ-007"' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'aria-current="true"' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q '32-05-ISD-timingdata-interchange' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'Normal operation' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'System, backoffice and recovery' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'Registration operation' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'data-eng-resizer="tree-root"' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'data-eng-resizer="root-compare"' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'role="separator"' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
! grep -q 'md-nav__link eng-tree-group__toggle' bld/engineering-portal/browser-workspace-IF05-REQ-007.html

python - <<'PY'
from pathlib import Path

source = Path("bld/engineering-portal/site/workspace/index.html")
target = Path(
    "bld/engineering-portal/site/workspace-interaction-test/index.html"
)
target.parent.mkdir(parents=True, exist_ok=True)
html = source.read_text(encoding="utf-8")
probe = r"""
<script>
window.addEventListener("load", () => {
  window.setTimeout(() => {
    const root = document.querySelector("[data-eng-workspace]");
    const collapsed = root && Array.from(
      root.querySelectorAll(
        '[data-eng-tree-toggle][aria-expanded="false"]'
      )
    ).find((toggle) => {
      return (
        getComputedStyle(toggle).display !== "none" &&
        toggle.getClientRects().length > 0
      );
    });
    if (collapsed) {
      const group = collapsed.closest("[data-eng-tree-group]");
      const children = group && group.querySelector(
        ":scope > .eng-tree-group__items"
      );
      const before = children
        ? getComputedStyle(children).display
        : "missing";
      collapsed.click();
      const afterOpen = children
        ? getComputedStyle(children).display
        : "missing";
      collapsed.click();
      const afterClose = children
        ? getComputedStyle(children).display
        : "missing";
      document.body.dataset.treeToggleInteraction =
        before === "none" &&
        afterOpen !== "none" &&
        afterClose === "none" &&
        collapsed.getAttribute("aria-expanded") === "false"
          ? "passed"
          : "failed";
    } else {
      document.body.dataset.treeToggleInteraction = "no-collapsed-node";
    }

    const customTree = root && root.querySelector(".eng-object-tree");
    document.body.dataset.treeMaterialIsolation =
      customTree &&
      !customTree.querySelector('[class*="md-nav"]')
        ? "passed"
        : "failed";

    const browser = root && root.querySelector(".eng-object-browser");
    const search = root && root.querySelector("[data-eng-tree-search]");
    const topToggle = root && root.querySelector(
      '[data-tree-level="0"] > [data-eng-tree-toggle]'
    );
    const visibleObject = root && Array.from(
      root.querySelectorAll("[data-workspace-root-id]")
    ).find((node) => node.getClientRects().length > 0);
    if (browser && search && topToggle && visibleObject) {
      const browserLeft = browser.getBoundingClientRect().left;
      const searchLeft = search.getBoundingClientRect().left;
      const topLeft = topToggle.getBoundingClientRect().left;
      const objectLabel = visibleObject.querySelector(
        ".eng-tree-item__id"
      );
      const objectLeft = objectLabel
        ? objectLabel.getBoundingClientRect().left
        : Number.POSITIVE_INFINITY;
      const searchOffset = searchLeft - browserLeft;
      const topOffset = topLeft - browserLeft;
      const objectOffset = objectLeft - browserLeft;
      document.body.dataset.treeGeometry =
        [
          searchOffset.toFixed(1),
          topOffset.toFixed(1),
          objectOffset.toFixed(1)
        ].join(",");
      document.body.dataset.treeEdgeSpacing =
        Math.abs(searchOffset - 4) <= 1.5 &&
        Math.abs(topOffset - 4) <= 1.5
          ? "passed"
          : "failed";
      document.body.dataset.treeIndentCompact =
        objectOffset > topOffset &&
        objectOffset <= 20
          ? "passed"
          : "failed";
    }

    const collapseAll = root && root.querySelector(
      "[data-eng-tree-collapse-all]"
    );
    if (collapseAll) {
      collapseAll.click();
      const expanded = root.querySelectorAll(
        "[data-eng-tree-group].is-expanded"
      ).length;
      const ariaOpen = Array.from(
        root.querySelectorAll("[data-eng-tree-toggle]")
      ).some((toggle) => toggle.getAttribute("aria-expanded") === "true");
      document.body.dataset.collapseAllInteraction =
        expanded === 0 && !ariaOpen ? "passed" : "failed";

      const directChildren = (group) => {
        const list = group.querySelector(
          ":scope > .eng-tree-group__items"
        );
        if (!list) return { groups: [], leaves: [] };
        return {
          groups: Array.from(
            list.querySelectorAll(
              ":scope > [data-eng-tree-group]"
            )
          ).filter((child) => !child.hidden),
          leaves: Array.from(
            list.querySelectorAll(
              ":scope > .eng-tree-leaf > [data-workspace-root-id]"
            )
          ).filter((leaf) => !leaf.hidden)
        };
      };

      const linearChain = (group) => {
        const chain = [group];
        let current = group;
        while (current) {
          const children = directChildren(current);
          if (
            children.leaves.length ||
            children.groups.length !== 1
          ) {
            break;
          }
          current = children.groups[0];
          chain.push(current);
        }
        return chain;
      };

      const candidate = Array.from(
        root.querySelectorAll("[data-eng-tree-group]")
      )
        .map((group) => linearChain(group))
        .find((chain) => chain.length >= 2);
      if (candidate) {
        const toggle = candidate[0].querySelector(
          ":scope > [data-eng-tree-toggle]"
        );
        if (toggle) toggle.click();
        document.body.dataset.linearBranchExpansion =
          candidate.every((group) =>
            group.classList.contains("is-expanded")
          )
            ? "passed"
            : "failed";
        collapseAll.click();
      } else {
        document.body.dataset.linearBranchExpansion =
          "no-linear-branch";
      }

      const groupByLabel = (label, scope = root) =>
        Array.from(
          scope.querySelectorAll("[data-eng-tree-group]")
        ).find((group) => {
          const labelNode = group.querySelector(
            ":scope > [data-eng-tree-toggle] .eng-tree-group__label"
          );
          return (
            labelNode &&
            labelNode.textContent.trim() === label
          );
        });

      const ssd = groupByLabel(
        "41-01-SSD-timing-application-specification-document"
      );
      if (ssd) {
        const ssdToggle = ssd.querySelector(
          ":scope > [data-eng-tree-toggle]"
        );
        if (ssdToggle) ssdToggle.click();

        const topChildren = directChildren(ssd).groups;
        const topLabels = topChildren.map((group) => {
          const label = group.querySelector(
            ":scope > [data-eng-tree-toggle] .eng-tree-group__label"
          );
          return label ? label.textContent.trim() : "";
        });
        const requirements = topChildren.find((group) => {
          const label = group.querySelector(
            ":scope > [data-eng-tree-toggle] .eng-tree-group__label"
          );
          return (
            label &&
            label.textContent.trim() === "Software-item requirements"
          );
        });
        const architecture = topLabels.includes(
          "Software-item architecture"
        );

        const firstExecutable = groupByLabel(
          "SI-01 application requirements",
          requirements || root
        );
        const usefulChoices = firstExecutable
          ? directChildren(firstExecutable).groups
              .map((group) => {
                const label = group.querySelector(
                  ":scope > [data-eng-tree-toggle] .eng-tree-group__label"
                );
                return label ? label.textContent.trim() : "";
              })
          : [];

        document.body.dataset.ssdRequirementsExpansion =
          ssd.classList.contains("is-expanded") &&
          topLabels.includes("Software-item requirements") &&
          architecture &&
          requirements &&
          requirements.classList.contains("is-expanded") &&
          firstExecutable &&
          firstExecutable.classList.contains("is-expanded") &&
          usefulChoices.includes("Process lifecycle and configuration") &&
          usefulChoices.includes("Build and version identity") &&
          usefulChoices.includes("Status") &&
          usefulChoices.includes("Application boundary and testability") &&
          usefulChoices.includes("Registration operation")
            ? "passed"
            : "failed";
        collapseAll.click();
      } else {
        document.body.dataset.ssdRequirementsExpansion =
          "missing-ssd";
      }
    }

    const splitter = root && root.querySelector(
      '[data-eng-resizer="tree-root"]'
    );
    const layout = root && root.querySelector(".eng-trace-layout");
    if (splitter && layout) {
      const before = layout.style.gridTemplateColumns;
      splitter.dispatchEvent(
        new KeyboardEvent("keydown", {
          key: "ArrowRight",
          bubbles: true
        })
      );
      const after = layout.style.gridTemplateColumns;
      document.body.dataset.paneResizeInteraction =
        before !== after ? "passed" : "failed";
      document.body.dataset.paneResizePersisted =
        localStorage.getItem(
          "engineering-traceability-pane-shares-v1"
        )
          ? "passed"
          : "failed";
    }
  }, 400);
});
</script>
"""
target.write_text(
    html.replace("</body>", probe + "</body>"),
    encoding="utf-8",
)
PY

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --window-size=1920,1200 \
  --virtual-time-budget=3500 \
  --dump-dom \
  "http://127.0.0.1:8765/workspace-interaction-test/?object=IF05-REQ-007&compare=SI01-REQ-045" \
  > bld/engineering-portal/browser-workspace-interaction.html

python - <<'PY'
import re
from pathlib import Path

html = Path(
    "bld/engineering-portal/browser-workspace-interaction.html"
).read_text(encoding="utf-8")
geometry = re.search(
    r'data-tree-geometry="([^"]*)"',
    html,
)
print(
    "tree-geometry offsets search, top, object:",
    geometry.group(1) if geometry else "<missing>",
)

checks = {
    "tree-toggle-interaction": "passed",
    "tree-material-isolation": "passed",
    "tree-edge-spacing": "passed",
    "tree-indent-compact": "passed",
    "collapse-all-interaction": "passed",
    "linear-branch-expansion": "passed",
    "ssd-requirements-expansion": "passed",
    "pane-resize-interaction": "passed",
    "pane-resize-persisted": "passed",
}
failures = []
for name, expected in checks.items():
    match = re.search(rf'data-{name}="([^"]*)"', html)
    actual = match.group(1) if match else "<missing>"
    print(f"{name}: {actual}")
    if actual != expected:
        failures.append((name, actual, expected))
if failures:
    raise SystemExit(f"browser interaction failures: {failures}")
PY

rm -rf bld/engineering-portal/site/workspace-interaction-test
! grep -q 'treeToggleInteraction' bld/engineering-portal/site/workspace/index.html
! grep -q 'paneResizeInteraction' bld/engineering-portal/site/workspace/index.html
! grep -q 'paneResizePersisted' bld/engineering-portal/site/workspace/index.html

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/" \
  > bld/engineering-portal/browser-landing.html

grep -q 'Event Timing Engineering Portal' bld/engineering-portal/browser-landing.html
grep -q 'Start here' bld/engineering-portal/browser-landing.html

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/explorer/" \
  > bld/engineering-portal/browser-explorer-neutral.html

grep -q 'Select an engineering object.' bld/engineering-portal/browser-explorer-neutral.html
! grep -q '<code>TimingNode</code>' bld/engineering-portal/browser-explorer-neutral.html

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/workspace/" \
  > bld/engineering-portal/browser-workspace-neutral.html

grep -q 'Select an engineering object.' bld/engineering-portal/browser-workspace-neutral.html
grep -q 'Select a related object to compare.' bld/engineering-portal/browser-workspace-neutral.html
! grep -q 'aria-current="true"' bld/engineering-portal/browser-workspace-neutral.html

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/explorer/?object=TimingNode" \
  > bld/engineering-portal/browser-explorer.html

grep -q '<code>TimingNode</code>' bld/engineering-portal/browser-explorer.html
# Report the exact missing/obsolete phrase if a browser UX assertion fails.
portal_has() {
  if ! grep -q "$2" "$1"; then
    echo "Portal browser check: missing '$2' in $1" >&2
    return 1
  fi
}
portal_lacks() {
  if grep -q "$2" "$1"; then
    echo "Portal browser check: unexpected '$2' in $1" >&2
    return 1
  fi
}
portal_has bld/engineering-portal/browser-explorer.html 'This architecture element realizes:'
portal_has bld/engineering-portal/browser-explorer.html 'Detailed designs (2)'
portal_has bld/engineering-portal/browser-explorer.html 'data-object-id="SI01-REQ-020"'
portal_has bld/engineering-portal/browser-explorer.html 'data-object-id="DD-TimingNodeExecution"'
portal_lacks bld/engineering-portal/browser-explorer.html 'Outgoing relationships'
portal_lacks bld/engineering-portal/browser-explorer.html 'Incoming relationships'
portal_lacks bld/engineering-portal/browser-explorer.html 'One-hop context'
portal_lacks bld/engineering-portal/browser-explorer.html 'ELABORATES THIS'

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/workspace/?object=TimingNode&compare=DD-TimingNodeExecution" \
  > bld/engineering-portal/browser-workspace-TimingNode.html

portal_has bld/engineering-portal/browser-workspace-TimingNode.html 'This architecture element realizes:'
portal_has bld/engineering-portal/browser-workspace-TimingNode.html 'Detailed designs (2)'
portal_has bld/engineering-portal/browser-workspace-TimingNode.html 'This detailed design elaborates:'
portal_has bld/engineering-portal/browser-workspace-TimingNode.html 'data-compare-object-id="DD-TimingNodeExecution"'
portal_lacks bld/engineering-portal/browser-workspace-TimingNode.html 'One-hop context'


grep -q 'eng-explorer-workspace' bld/engineering-portal/browser-explorer.html
grep -q 'data-eng-detail' bld/engineering-portal/browser-explorer.html
grep -q 'data-engineering-id="TimingNode"' bld/engineering-portal/browser-explorer.html
# The old one-hop list duplicated the typed relationship groups above.
grep -q 'Open details &amp; relations' bld/engineering-portal/browser-explorer.html
grep -q 'Open source definition' bld/engineering-portal/browser-explorer.html
! grep -q 'data-eng-compare-detail' bld/engineering-portal/browser-explorer.html

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/explorer/?object=UC-001" \
  > bld/engineering-portal/browser-explorer-UC-001.html

grep -q '<code>UC-001</code>' bld/engineering-portal/browser-explorer-UC-001.html
portal_has bld/engineering-portal/browser-explorer-UC-001.html 'Requirements (3)'
for target in SI01-REQ-023 SI01-REQ-024 SI01-REQ-025; do
  portal_has bld/engineering-portal/browser-explorer-UC-001.html "data-object-id=\"$target\""
done
portal_lacks bld/engineering-portal/browser-explorer-UC-001.html 'class="eng-relation__document"'
portal_lacks bld/engineering-portal/browser-explorer-UC-001.html 'This use case is specified by:'

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/workspace/?object=UC-001&compare=SI01-REQ-024" \
  > bld/engineering-portal/browser-workspace-UC-001.html

portal_has bld/engineering-portal/browser-workspace-UC-001.html 'Requirements (3)'
portal_has bld/engineering-portal/browser-workspace-UC-001.html 'data-compare-object-id="SI01-REQ-024"'
portal_has bld/engineering-portal/browser-workspace-UC-001.html 'This requirement specifies:'
portal_has bld/engineering-portal/browser-workspace-UC-001.html 'More specific requirements (2)'
portal_has bld/engineering-portal/browser-workspace-UC-001.html 'data-compare-object-id="IF04-REQ-002"'
portal_has bld/engineering-portal/browser-workspace-UC-001.html 'data-compare-object-id="IF03-REQ-004"'
portal_lacks bld/engineering-portal/browser-workspace-UC-001.html 'class="eng-relation__document"'

grep -q 'Preconditions' bld/engineering-portal/browser-explorer-UC-001.html
grep -q 'Alternative/failure flows' bld/engineering-portal/browser-explorer-UC-001.html
grep -q 'Open source definition' bld/engineering-portal/browser-explorer-UC-001.html
grep -q '?plain=1#L' bld/engineering-portal/browser-explorer-UC-001.html

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/explorer/?object=UC-002" \
  > bld/engineering-portal/browser-explorer-UC-002.html

portal_has bld/engineering-portal/browser-explorer-UC-002.html 'Requirements (3)'
for target in SI01-REQ-024 SI01-REQ-026 SI01-REQ-040; do
  portal_has bld/engineering-portal/browser-explorer-UC-002.html "data-object-id=\"$target\""
done
portal_lacks bld/engineering-portal/browser-explorer-UC-002.html 'data-object-id="IF04-REQ-003"'
portal_lacks bld/engineering-portal/browser-explorer-UC-002.html 'data-object-id="IF03-REQ-011"'

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/explorer/?object=UC-005" \
  > bld/engineering-portal/browser-explorer-UC-005.html

portal_has bld/engineering-portal/browser-explorer-UC-005.html 'Requirements (1)'
portal_has bld/engineering-portal/browser-explorer-UC-005.html 'data-object-id="SI01-REQ-060"'

grep -q 'data-engineering-id="AntennaManager"' bld/engineering-portal/site/explorer/index.html
grep -q 'aria-label="Open AntennaManager"' bld/engineering-portal/site/explorer/index.html

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/explorer/?object=AntennaManager" \
  > bld/engineering-portal/browser-explorer-AntennaManager.html

grep -q '<code>AntennaManager</code>' bld/engineering-portal/browser-explorer-AntennaManager.html
grep -q 'coordinates 1..N configured Antenna components for one' bld/engineering-portal/browser-explorer-AntennaManager.html
grep -q 'Open source definition' bld/engineering-portal/browser-explorer-AntennaManager.html

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --dump-dom \
  "http://127.0.0.1:8765/engineering-client-ui/" \
  > bld/engineering-portal/browser-engineering-client-ui.html

grep -q 'Engineering Client — Step 4 Timing UI' bld/engineering-portal/browser-engineering-client-ui.html
grep -q 'CLOSED without operational location' bld/engineering-portal/browser-engineering-client-ui.html
grep -q 'OPEN with bounded LogBook' bld/engineering-portal/browser-engineering-client-ui.html
grep -q 'RECONNECTING / stale' bld/engineering-portal/browser-engineering-client-ui.html
grep -q 'engineering-client-timing-open.svg' bld/engineering-portal/browser-engineering-client-ui.html

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --window-size=1600,1200 \
  --screenshot=bld/engineering-portal/engineering-client-ui.png \
  "http://127.0.0.1:8765/engineering-client-ui/"

"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --window-size=1920,1200 \
  --screenshot=bld/engineering-portal/explorer-TimingNode.png \
  "http://127.0.0.1:8765/explorer/?object=TimingNode"


"$chrome" \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --virtual-time-budget=2500 \
  --window-size=1920,1200 \
  --screenshot=bld/engineering-portal/workspace-IF05-REQ-007.png \
  "http://127.0.0.1:8765/workspace/?object=IF05-REQ-007&compare=SI01-REQ-045"
