#!/usr/bin/env bash
# Exercise the generated Engineering Portal in a real headless browser.
#
# This checks interactions that static graph/HTML verification cannot prove:
# expand/collapse, search/filter, comparing and swapping objects, pane resize,
# keyboard/ARIA state and saved layout. The IF05/SSD objects below are small
# representative fixtures for those interactions, not a list of required
# engineering objects or a second copy of the product requirements.
#
# Input: bld/engineering-portal/site from the documentation build.
# Needs: Chrome/Chromium and Python; runs a temporary localhost preview server.
# Static graph/content integrity is owned by verify_engineering_portal.py.
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
grep -q 'class="eng-detail__promote-top"' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'aria-label="Swap selected and compared objects"' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
grep -q 'title="Swap selected and compared objects"' bld/engineering-portal/browser-workspace-IF05-REQ-007.html
python - <<'PY'
from pathlib import Path

html = Path(
    "bld/engineering-portal/browser-workspace-IF05-REQ-007.html"
).read_text(encoding="utf-8")
if html.count('data-eng-promote-object-id="SI01-REQ-045"') != 3:
    raise SystemExit(
        "Both panes must expose swap icons, with the original Make primary action"
    )
# The current UC catalogue is the authority for group labels/order.
# Extract its sections instead of duplicating their names in this test.
import re

source = Path("docs/30-UC-system-use-cases.md").read_text(encoding="utf-8")
catalogue = source.split("## Use-case catalogue", 1)[1].split(
    "## Detailed use cases", 1
)[0]
labels = re.findall(r"(?m)^### (.+)$", catalogue)
if not labels:
    raise SystemExit("no authored use-case groups for portal navigation")
tokens = [
    f'<span class="eng-tree-group__label">{label}</span>'
    for label in labels
]
positions = [html.find(token) for token in tokens]
if any(position < 0 for position in positions) or positions != sorted(positions):
    raise SystemExit(
        f"use-case group order is not operator-first: {list(zip(labels, positions))}"
    )
PY
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
# The ordered UC and SSD groups are exercised by the browser checks below.
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
        // A correctly grouped tree may have no single-child heading chain.
        // The invariant applies only if a linear branch is present.
        document.body.dataset.linearBranchExpansion = "passed";
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

        // Clicking the SSD once must expose the meaningful requirement
        // categories; do not manually expand the intermediate headings here,
        // or the test would conceal a usability regression.
        const childGroupLabels = (group) =>
          group
            ? directChildren(group).groups.map((child) => {
                const label = child.querySelector(
                  ":scope > [data-eng-tree-toggle] .eng-tree-group__label"
                );
                return label ? label.textContent.trim() : "";
              })
            : [];

        const topRequirementLabels = childGroupLabels(requirements);
        const functional = groupByLabel(
          "Functional requirements", requirements || root
        );
        const technical = groupByLabel(
          "Technical requirements", requirements || root
        );
        const functionalLabels = childGroupLabels(functional);
        const technicalLabels = childGroupLabels(technical);

        // A leaf-bearing category is a deliberate choice: it should not be
        // auto-expanded along with structural headings.
        const firstFunctionalCategory =
          functional && directChildren(functional).groups[0];
        const categoryWasCollapsed =
          firstFunctionalCategory &&
          !firstFunctionalCategory.classList.contains("is-expanded");
        if (firstFunctionalCategory) {
          const toggle = firstFunctionalCategory.querySelector(
            ":scope > [data-eng-tree-toggle]"
          );
          if (toggle) toggle.click();
        }
        const categoryManuallyExpanded =
          firstFunctionalCategory &&
          firstFunctionalCategory.classList.contains("is-expanded") &&
          directChildren(firstFunctionalCategory).leaves.length > 0;

        document.body.dataset.ssdRequirementsExpansion =
          categoryWasCollapsed &&
          categoryManuallyExpanded &&
          ssd.classList.contains("is-expanded") &&
          topLabels.includes("Software-item requirements") &&
          architecture &&
          requirements &&
          requirements.classList.contains("is-expanded") &&
          requirements &&
          topRequirementLabels.indexOf("Functional requirements") >= 0 &&
          topRequirementLabels.indexOf("Technical requirements") >
            topRequirementLabels.indexOf("Functional requirements") &&
          functional &&
          functional.classList.contains("is-expanded") &&
          functionalLabels.length > 0 &&
          technical &&
          technical.classList.contains("is-expanded") &&
          technicalLabels.length > 0
            ? "passed"
            : "failed";
        collapseAll.click();
      } else {
        document.body.dataset.ssdRequirementsExpansion =
          "missing-ssd";
      }
    }

    const comparePane = root && root.querySelector(
      "[data-eng-compare-detail]"
    );
    const primaryPane = root && root.querySelector(
      "[data-eng-root-detail]"
    );
    const promoteTop = comparePane && comparePane.querySelector(
      ".eng-detail__promote-top"
    );
    if (promoteTop && primaryPane && comparePane) {
      const beforePrimary = primaryPane.querySelector(
        ".eng-detail__header > code"
      );
      const beforeCompared = comparePane.querySelector(
        ".eng-detail__header > code"
      );
      const beforePrimaryId = beforePrimary
        ? beforePrimary.textContent.trim()
        : "";
      const beforeComparedId = beforeCompared
        ? beforeCompared.textContent.trim()
        : "";
      promoteTop.click();
      const afterPrimary = primaryPane.querySelector(
        ".eng-detail__header > code"
      );
      const afterCompared = comparePane.querySelector(
        ".eng-detail__header > code"
      );
      document.body.dataset.promoteTopInteraction =
        afterPrimary &&
        afterCompared &&
        afterPrimary.textContent.trim() === beforeComparedId &&
        afterCompared.textContent.trim() === beforePrimaryId
          ? "passed"
          : "failed";
    } else {
      document.body.dataset.promoteTopInteraction = "missing";
    }

    const selectedSwap = primaryPane && primaryPane.querySelector(
      "[data-eng-selected-swap]"
    );
    const swapReady = selectedSwap && !selectedSwap.hidden &&
      selectedSwap.dataset.engPromoteObjectId;
    if (swapReady && primaryPane && comparePane) {
      const beforeSelected = primaryPane.querySelector(".eng-detail__header > code").textContent.trim();
      const beforeCompared = comparePane.querySelector(".eng-detail__header > code").textContent.trim();
      selectedSwap.click();
      const afterSelected = primaryPane.querySelector(".eng-detail__header > code").textContent.trim();
      const afterCompared = comparePane.querySelector(".eng-detail__header > code").textContent.trim();
      document.body.dataset.selectedSwapInteraction =
        afterSelected === beforeCompared && afterCompared === beforeSelected
          ? "passed" : "failed";
    } else {
      document.body.dataset.selectedSwapInteraction = "missing";
    }
    const comparedId = comparePane && comparePane.querySelector(".eng-detail__header > code");
    const comparedLink = comparedId && root.querySelector(
      '[data-compare-object-id="' + comparedId.textContent.trim() + '"]'
    );
    if (comparedLink) {
      // Selecting a fresh primary object clears the comparison.
      const other = root.querySelector('[data-workspace-root-id="IF05-REQ-007"]');
      if (other) other.click();
    }
    const selectedWithoutComparison = primaryPane && primaryPane.querySelector("[data-eng-selected-swap]");
    document.body.dataset.swapHiddenWithoutComparison =
      selectedWithoutComparison && selectedWithoutComparison.hidden
        ? "passed" : "failed";

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
    "promote-top-interaction": "passed",
    "selected-swap-interaction": "passed",
    "swap-hidden-without-comparison": "passed",
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
# Negative relation membership is asserted against the generated graph in
# verify_engineering_portal.py; the Explorer DOM also contains the global object tree.

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
