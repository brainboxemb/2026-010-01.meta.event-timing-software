(function () {
  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function initializePortalViews() {
    const dataNode = document.getElementById("eng-graph-data");
    if (!dataNode) return;

    let data;
    try {
      data = JSON.parse(dataNode.textContent);
    } catch (error) {
      console.error("Unable to parse engineering graph data", error);
      return;
    }

    // The portal generator creates these headings for all three view types.
    // Incoming links are labelled by the linked object's role, not a passive
    // inversion of the authored Sphinx-Needs verb.
    function relationButton(id, mode) {
      const object = data.objects[id];
      if (!object) return "";
      const attribute =
        mode === "compare"
          ? 'data-compare-object-id="' + escapeHtml(id) + '"'
          : 'data-object-id="' + escapeHtml(id) + '"';
      return (
        '<button class="eng-relation" type="button" ' +
        attribute +
        ">" +
        '<span class="eng-relation__object">' +
        escapeHtml(object.id) +
        " — " +
        escapeHtml(object.title) +
        "</span>" +
        "</button>"
      );
    }

    function relationGroups(object, mode) {
      const sections = [];
      for (const group of object.relation_groups || []) {
        const heading =
          '<h3 title="Traceability relation: ' +
          escapeHtml(group.type) +
          '">' +
          escapeHtml(group.title) +
          "</h3>";
        const description = group.description
          ? '<p class="eng-relation__hint">' +
            escapeHtml(group.description) +
            "</p>"
          : "";

        // Every item stays directly visible; headings simply partition
        // the existing flat rows by their authored source document.
        let relatedRows;
        if (group.document_groups && group.document_groups.length > 1) {
          relatedRows = group.document_groups
            .map((document) => {
              return (
                '<div class="eng-relation__source-group">' +
                '<h4 class="eng-relation__source-heading">' +
                escapeHtml(document.title) +
                " (" +
                document.related_ids.length +
                ")</h4>" +
                document.related_ids
                  .map((id) => relationButton(id, mode))
                  .join("") +
                "</div>"
              );
            })
            .join("");
        } else {
          relatedRows = group.related_ids
            .map((id) => relationButton(id, mode))
            .join("");
        }

        sections.push(
          '<section class="eng-detail__relations" data-eng-relation-type="' +
            escapeHtml(group.type) +
            '" data-eng-relation-direction="' +
            escapeHtml(group.direction) +
            '">' +
            heading +
            description +
            relatedRows +
            "</section>"
        );
      }
      return sections.length
        ? sections.join("")
        : "<p>No traceability relationships are recorded for this object.</p>";
    }

    function maturityStatus(object) {
      const labels = {
        D: "Draft",
        R: "Review",
        A: "Approved",
        O: "Obsolete",
      };
      const code = object && object.status ? String(object.status) : "";
      if (!labels[code]) return "";
      return (
        '<span class="eng-object-status eng-object-status--' +
        escapeHtml(code) +
        '" title="Requirement maturity: ' +
        escapeHtml(labels[code]) +
        '">' +
        escapeHtml(code) +
        " — " +
        escapeHtml(labels[code]) +
        "</span>"
      );
    }

    function sourceContextPanel(object) {
      const source = object ? object.source_context : null;
      if (!source || !Array.isArray(source.lines) || !source.lines.length) {
        return "";
      }
      const rows = source.lines
        .map((line) => {
          const selected =
            Number(line.number) === Number(source.line)
              ? " is-authoritative-line"
              : "";
          return (
            '<div class="eng-source-context__line' +
            selected +
            '">' +
            '<span class="eng-source-context__number">' +
            escapeHtml(line.number) +
            "</span>" +
            '<code class="eng-source-context__text">' +
            escapeHtml(line.text) +
            "</code>" +
            "</div>"
          );
        })
        .join("");
      return (
        '<details class="eng-source-context">' +
        "<summary>Source definition in pane</summary>" +
        '<div class="eng-source-context__meta">' +
        "<code>" +
        escapeHtml(source.path) +
        ":" +
        escapeHtml(source.line) +
        "</code>" +
        "</div>" +
        '<div class="eng-source-context__lines">' +
        rows +
        "</div>" +
        "</details>"
      );
    }

    function objectPanel(object, roleLabel, mode) {
      const canPromote =
        mode === "compare" && roleLabel === "Compared object";
      const promoteAction = canPromote
        ? '<button class="md-button" type="button" data-eng-promote-object-id="' +
          escapeHtml(object.id) +
          '">Make primary</button>'
        : "";
      const selectedSwap =
        mode === "compare" && roleLabel === "Selected object";
      const promoteTopAction = canPromote || selectedSwap
        ? '<button class="eng-detail__promote-top" type="button" ' +
          (selectedSwap
            ? "data-eng-selected-swap hidden "
            : 'data-eng-promote-object-id="' + escapeHtml(object.id) + '" ') +
          'title="Swap selected and compared objects" ' +
          'aria-label="Swap selected and compared objects">' +
          '<span aria-hidden="true">⇄</span></button>'
        : "";
      return (
        (roleLabel
          ? '<div class="eng-detail__role-row">' +
            '<div class="eng-detail__role">' +
            escapeHtml(roleLabel) +
            "</div>" +
            promoteTopAction +
            "</div>"
          : "") +
        '<div class="eng-detail__header">' +
        '<span class="eng-object-type">' +
        escapeHtml(object.type_label) +
        "</span>" +
        maturityStatus(object) +
        "<h2>" +
        escapeHtml(object.title) +
        "</h2>" +
        "<code>" +
        escapeHtml(object.id) +
        "</code>" +
        "</div>" +
        (object.content_html
          ? '<div class="eng-detail__summary">' + object.content_html + "</div>"
          : "") +
        '<div class="eng-detail__actions">' +
        '<a class="md-button md-button--primary" href="../objects/' +
        encodeURIComponent(object.id) +
        '/">Open details & relations</a>' +
        '<a class="md-button" href="' +
        escapeHtml(object.source_url) +
        '">Open source definition</a>' +
        promoteAction +
        "</div>" +
        sourceContextPanel(object) +
        relationGroups(object, mode)
      );
    }

    function initializeExplorer() {
      const root = document.querySelector("[data-eng-explorer]");
      if (!root) return;
      const detail = root.querySelector("[data-eng-detail]");
      const resizer = root.querySelector("[data-eng-explorer-resizer]");
      const storageKey = "engineering-explorer-pane-shares-v1";
      const defaultShares = [0.75, 0.25];
      let paneShares = defaultShares.slice();
      const initialUrl = new URL(window.location.href);

      function normalizeShares(shares) {
        if (!Array.isArray(shares) || shares.length !== 2) return null;
        const values = shares.map(Number);
        if (values.some((value) => !Number.isFinite(value) || value <= 0)) {
          return null;
        }
        const total = values[0] + values[1];
        if (!Number.isFinite(total) || total <= 0) return null;
        return values.map((value) => value / total);
      }

      function applyShares(shares, persist) {
        const normalized = normalizeShares(shares);
        if (!normalized) return;
        paneShares = normalized;

        if (window.matchMedia("(max-width: 900px)").matches) {
          root.style.removeProperty("grid-template-columns");
          return;
        }

        const available = Math.max(1, root.clientWidth - 4);
        const left = Math.round(paneShares[0] * available);
        const right = Math.max(0, available - left);
        root.style.gridTemplateColumns =
          left + "px 4px " + right + "px";

        if (resizer) {
          resizer.setAttribute(
            "aria-valuenow",
            String(Math.round(paneShares[0] * 100))
          );
        }
        if (persist) {
          try {
            localStorage.setItem(storageKey, JSON.stringify(paneShares));
          } catch (error) {
            // Resizing remains usable when storage is unavailable.
          }
        }
      }

      function restoreShares() {
        try {
          const saved = normalizeShares(
            JSON.parse(localStorage.getItem(storageKey))
          );
          if (saved) paneShares = saved;
        } catch (error) {
          // Keep the authored default ratio.
        }
        applyShares(paneShares, false);
      }

      function resize(deltaPixels, startShares) {
        const available = Math.max(1, root.clientWidth - 4);
        const widths = startShares.map((share) => share * available);
        const pairTotal = widths[0] + widths[1];
        const minimumLeft = 260;
        const minimumRight = 240;

        widths[0] = Math.min(
          pairTotal - minimumRight,
          Math.max(minimumLeft, widths[0] + deltaPixels)
        );
        widths[1] = pairTotal - widths[0];
        applyShares(widths.map((width) => width / available), false);
      }

      function initializeResizer() {
        if (!resizer) return;
        resizer.setAttribute("aria-valuemin", "10");
        resizer.setAttribute("aria-valuemax", "90");
        restoreShares();

        resizer.addEventListener("pointerdown", (event) => {
          if (window.matchMedia("(max-width: 900px)").matches) return;
          event.preventDefault();
          const startX = event.clientX;
          const startShares = paneShares.slice();
          resizer.classList.add("is-dragging");
          if (resizer.setPointerCapture) {
            resizer.setPointerCapture(event.pointerId);
          }

          const move = (moveEvent) => {
            resize(moveEvent.clientX - startX, startShares);
          };
          const finish = () => {
            resizer.classList.remove("is-dragging");
            applyShares(paneShares, true);
            resizer.removeEventListener("pointermove", move);
            resizer.removeEventListener("pointerup", finish);
            resizer.removeEventListener("pointercancel", finish);
          };

          resizer.addEventListener("pointermove", move);
          resizer.addEventListener("pointerup", finish);
          resizer.addEventListener("pointercancel", finish);
        });

        resizer.addEventListener("keydown", (event) => {
          if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
            return;
          }
          event.preventDefault();
          resize(
            (event.key === "ArrowLeft" ? -1 : 1) * 24,
            paneShares.slice()
          );
          applyShares(paneShares, true);
        });

        resizer.addEventListener("dblclick", () => {
          applyShares(defaultShares, true);
        });

        window.addEventListener("resize", () => {
          applyShares(paneShares, false);
        });
      }

      function selectedId(node) {
        return node.dataset.objectId || node.dataset.engineeringId || "";
      }

      function render(id, updateHistory) {
        const object = data.objects[id];
        if (!object || !detail) return;

        root
          .querySelectorAll("[data-object-id], [data-engineering-id]")
          .forEach((node) => {
            node.classList.toggle("is-selected", selectedId(node) === id);
          });

        detail.innerHTML = objectPanel(object, "Selected object", "navigate");

        if (updateHistory) {
          const url = new URL(window.location.href);
          url.searchParams.set("object", id);
          url.searchParams.delete("compare");
          history.replaceState({}, "", url);
        }
      }

      root.addEventListener("click", (event) => {
        const target = event.target.closest(
          "[data-object-id], [data-engineering-id]"
        );
        if (target && root.contains(target)) {
          render(selectedId(target), true);
        }
      });

      root.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        const target = event.target.closest(
          "[data-object-id], [data-engineering-id]"
        );
        if (target && root.contains(target)) {
          event.preventDefault();
          render(selectedId(target), true);
        }
      });

      const requested = initialUrl.searchParams.get("object");
      if (requested && data.objects[requested]) {
        render(requested, false);
      }
      initializeResizer();
    }

    function initializeWorkspace() {
      const root = document.querySelector("[data-eng-workspace]");
      if (!root) return;

      const rootDetail = root.querySelector("[data-eng-root-detail]");
      const compareDetail = root.querySelector("[data-eng-compare-detail]");
      const objectBrowser = root.querySelector(".eng-object-browser");
      const filterPanel = root.querySelector(".eng-object-browser__filters");
      const searchInput = root.querySelector("[data-eng-tree-search]");
      const typeFilter = root.querySelector("[data-eng-tree-type]");
      const collapseAllButton = root.querySelector(
        "[data-eng-tree-collapse-all]"
      );
      const resultCount = root.querySelector("[data-eng-tree-count]");

      // Use cases are read operator-first. Keep this as a portal presentation
      // rule rather than reordering the authored use-case document.
      const topTreeGroups = Array.from(
        root.querySelectorAll(".eng-tree-root > [data-eng-tree-group]")
      );
      const useCaseGroup = topTreeGroups.find((group) => {
        const label = group.querySelector(
          ":scope > [data-eng-tree-toggle] .eng-tree-group__label"
        );
        return (
          label &&
          label.textContent.trim() === "30-UC-system-use-cases"
        );
      });
      if (useCaseGroup) {
        const items = useCaseGroup.querySelector(
          ":scope > .eng-tree-group__items"
        );
        if (items) {
          const preferred = [
            "Normal operation",
            "System, backoffice and recovery",
            "Engineering, simulation and verification"
          ];
          const groups = Array.from(
            items.querySelectorAll(":scope > [data-eng-tree-group]")
          );
          const labelOf = (group) => {
            const label = group.querySelector(
              ":scope > [data-eng-tree-toggle] .eng-tree-group__label"
            );
            return label ? label.textContent.trim() : "";
          };
          const ordered = preferred
            .map((label) => groups.find((group) => labelOf(group) === label))
            .filter(Boolean);
          const remainder = groups.filter((group) => !ordered.includes(group));
          [...ordered, ...remainder].forEach((group) =>
            items.appendChild(group)
          );
        }
      }

      const treeItems = Array.from(
        root.querySelectorAll("[data-workspace-root-id]")
      );
      const treeGroups = Array.from(
        root.querySelectorAll("[data-eng-tree-group]")
      );
      const treeToggles = Array.from(
        root.querySelectorAll("[data-eng-tree-toggle]")
      );
      const traceLayout = root.querySelector(".eng-trace-layout");
      const paneResizers = Array.from(
        root.querySelectorAll("[data-eng-resizer]")
      );
      const paneStorageKey = "engineering-traceability-pane-shares-v1";
      let paneShares = [0.28, 0.36, 0.36];
      const initialUrl = new URL(window.location.href);
      let rootId = "";
      let compareId = "";

      function normalizePaneShares(shares) {
        if (!Array.isArray(shares) || shares.length !== 3) return null;
        const values = shares.map(Number);
        if (values.some((value) => !Number.isFinite(value) || value <= 0)) {
          return null;
        }
        const total = values.reduce((sum, value) => sum + value, 0);
        if (!Number.isFinite(total) || total <= 0) return null;
        return values.map((value) => value / total);
      }

      function persistPaneShares() {
        try {
          localStorage.setItem(paneStorageKey, JSON.stringify(paneShares));
        } catch (error) {
          // Storage may be unavailable; resizing must still work for this page.
        }
      }

      function updateResizerAria() {
        if (paneResizers.length < 2) return;
        paneResizers[0].setAttribute(
          "aria-valuenow",
          String(Math.round(paneShares[0] * 100))
        );
        paneResizers[1].setAttribute(
          "aria-valuenow",
          String(Math.round((paneShares[0] + paneShares[1]) * 100))
        );
      }

      function applyPaneShares(shares, persist) {
        const normalized = normalizePaneShares(shares);
        if (!normalized || !traceLayout) return;
        paneShares = normalized;

        if (window.matchMedia("(max-width: 900px)").matches) {
          traceLayout.style.removeProperty("grid-template-columns");
          return;
        }

        const available = Math.max(0, traceLayout.clientWidth - 8);
        if (!available) return;
        const widths = paneShares.map((share) => Math.round(share * available));
        traceLayout.style.gridTemplateColumns =
          widths[0] +
          "px 4px " +
          widths[1] +
          "px 4px " +
          widths[2] +
          "px";
        updateResizerAria();
        if (persist) persistPaneShares();
      }

      function restorePaneShares() {
        try {
          const saved = JSON.parse(localStorage.getItem(paneStorageKey));
          const normalized = normalizePaneShares(saved);
          if (normalized) paneShares = normalized;
        } catch (error) {
          // Keep defaults when stored state is unavailable or invalid.
        }
        applyPaneShares(paneShares, false);
      }

      function resizeBoundary(index, deltaPixels, startShares) {
        if (!traceLayout) return;
        const available = Math.max(1, traceLayout.clientWidth - 8);
        const widths = startShares.map((share) => share * available);
        const minimums = [150, 240, 240];

        if (index === 0) {
          const pairTotal = widths[0] + widths[1];
          widths[0] = Math.min(
            pairTotal - minimums[1],
            Math.max(minimums[0], widths[0] + deltaPixels)
          );
          widths[1] = pairTotal - widths[0];
        } else {
          const pairTotal = widths[1] + widths[2];
          widths[1] = Math.min(
            pairTotal - minimums[2],
            Math.max(minimums[1], widths[1] + deltaPixels)
          );
          widths[2] = pairTotal - widths[1];
        }

        applyPaneShares(
          widths.map((width) => width / available),
          false
        );
      }

      function initializePaneResizers() {
        if (!traceLayout || paneResizers.length !== 2) return;
        restorePaneShares();

        paneResizers.forEach((resizer, index) => {
          resizer.setAttribute("aria-valuemin", "10");
          resizer.setAttribute("aria-valuemax", "90");

          resizer.addEventListener("pointerdown", (event) => {
            if (window.matchMedia("(max-width: 900px)").matches) return;
            event.preventDefault();
            const startX = event.clientX;
            const startShares = paneShares.slice();
            resizer.classList.add("is-dragging");
            if (resizer.setPointerCapture) {
              resizer.setPointerCapture(event.pointerId);
            }

            const move = (moveEvent) => {
              resizeBoundary(index, moveEvent.clientX - startX, startShares);
            };
            const finish = () => {
              resizer.classList.remove("is-dragging");
              persistPaneShares();
              resizer.removeEventListener("pointermove", move);
              resizer.removeEventListener("pointerup", finish);
              resizer.removeEventListener("pointercancel", finish);
            };

            resizer.addEventListener("pointermove", move);
            resizer.addEventListener("pointerup", finish);
            resizer.addEventListener("pointercancel", finish);
          });

          resizer.addEventListener("keydown", (event) => {
            if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
              return;
            }
            event.preventDefault();
            const direction = event.key === "ArrowLeft" ? -1 : 1;
            resizeBoundary(index, direction * 24, paneShares.slice());
            persistPaneShares();
          });

          resizer.addEventListener("dblclick", () => {
            paneShares = [0.28, 0.36, 0.36];
            applyPaneShares(paneShares, true);
          });
        });

        window.addEventListener("resize", () => {
          applyPaneShares(paneShares, false);
        });
      }

      function setGroupExpanded(group, expanded) {
        if (!group) return;
        group.classList.toggle("is-expanded", expanded);
        const toggle = group.querySelector(":scope > [data-eng-tree-toggle]");
        if (toggle) {
          toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
        }
      }

      function directVisibleTreeChildren(group) {
        if (!group) return { groups: [], leaves: [] };
        const items = group.querySelector(
          ":scope > .eng-tree-group__items"
        );
        if (!items) return { groups: [], leaves: [] };

        const groups = Array.from(
          items.querySelectorAll(":scope > [data-eng-tree-group]")
        ).filter((child) => !child.hidden);
        const leaves = Array.from(
          items.querySelectorAll(
            ":scope > .eng-tree-leaf > [data-workspace-root-id]"
          )
        ).filter((leaf) => !leaf.hidden);
        return { groups, leaves };
      }

      // Auto-open headings that merely organize more headings. Stop at a
      // meaningful choice (a group containing actual object leaves), so
      // opening a deep SSD does not require 3-4 clicks just to reach its
      // functional/technical categories, nor dump every requirement at once.
      // A single-child chain is also unfolded to its first available leaves.
      function expandUsefulBranches(group) {
        if (!group) return;
        setGroupExpanded(group, true);

        const children = directVisibleTreeChildren(group);
        if (children.leaves.length) return;

        if (children.groups.length === 1) {
          expandUsefulBranches(children.groups[0]);
          return;
        }
        children.groups.forEach((child) => {
          const nested = directVisibleTreeChildren(child);
          if (nested.groups.length && !nested.leaves.length) {
            expandUsefulBranches(child);
          }
        });
      }

      function toggleGroup(group) {
        if (!group) return;
        if (group.classList.contains("is-expanded")) {
          setGroupExpanded(group, false);
        } else {
          expandUsefulBranches(group);
        }
      }

      function updateTreeSelection() {
        let selectedNode = null;
        treeItems.forEach((node) => {
          const selected = node.dataset.workspaceRootId === rootId;
          node.classList.toggle("is-selected", selected);
          if (selected) {
            selectedNode = node;
            node.setAttribute("aria-current", "true");
            let group = node.closest("[data-eng-tree-group]");
            while (group) {
              setGroupExpanded(group, true);
              group = group.parentElement
                ? group.parentElement.closest("[data-eng-tree-group]")
                : null;
            }
          } else {
            node.removeAttribute("aria-current");
          }
        });
        if (selectedNode && objectBrowser) {
          const browserRect = objectBrowser.getBoundingClientRect();
          const nodeRect = selectedNode.getBoundingClientRect();
          const filterHeight = filterPanel
            ? filterPanel.getBoundingClientRect().height
            : 0;
          const visibleHeight = Math.max(
            0,
            objectBrowser.clientHeight - filterHeight
          );
          const targetTop =
            objectBrowser.scrollTop +
            (nodeRect.top - browserRect.top) -
            filterHeight -
            Math.max(0, (visibleHeight - nodeRect.height) / 2);
          objectBrowser.scrollTop = Math.max(0, targetTop);
        }
      }

      function updateCompareSelection() {
        root.querySelectorAll("[data-compare-object-id]").forEach((node) => {
          node.classList.toggle(
            "is-selected",
            node.dataset.compareObjectId === compareId
          );
        });
      }

      function updateSelectedSwapAction() {
        const button = rootDetail
          ? rootDetail.querySelector("[data-eng-selected-swap]")
          : null;
        if (!button) return;
        const canSwap = Boolean(compareId && rootId && compareId !== rootId);
        button.hidden = !canSwap;
        if (canSwap) {
          button.dataset.engPromoteObjectId = compareId;
        } else {
          button.removeAttribute("data-eng-promote-object-id");
        }
      }

      function updateUrl() {
        const url = new URL(window.location.href);
        if (rootId) {
          url.searchParams.set("object", rootId);
        } else {
          url.searchParams.delete("object");
        }
        if (rootId && compareId) {
          url.searchParams.set("compare", compareId);
        } else {
          url.searchParams.delete("compare");
        }
        history.replaceState({}, "", url);
      }

      function applyTreeFilter() {
        const query = (searchInput ? searchInput.value : "")
          .trim()
          .toLowerCase();
        const selectedType = typeFilter ? typeFilter.value : "";

        treeItems.forEach((node) => {
          const matchesQuery =
            !query || (node.dataset.objectSearch || "").includes(query);
          const matchesType =
            !selectedType || node.dataset.objectType === selectedType;
          node.hidden = !(matchesQuery && matchesType);
        });

        treeGroups.forEach((group) => {
          const visible = Array.from(
            group.querySelectorAll("[data-workspace-root-id]")
          ).some((node) => !node.hidden);
          group.hidden = !visible;
          if ((query || selectedType) && visible) {
            setGroupExpanded(group, true);
          }
        });

        if (resultCount) {
          const visibleCount = treeItems.filter((node) => !node.hidden).length;
          resultCount.textContent =
            visibleCount + (visibleCount === 1 ? " object" : " objects");
        }
      }

      function renderRoot(id, updateHistory) {
        const object = data.objects[id];
        if (!object || !rootDetail) return;
        rootId = id;
        compareId = "";
        rootDetail.innerHTML = objectPanel(object, "Selected object", "compare");
        rootDetail.scrollTop = 0;
        renderCompare("", false);
        updateTreeSelection();
        if (updateHistory) updateUrl();
      }

      function renderCompare(id, updateHistory) {
        if (!compareDetail) return;
        const object = data.objects[id];
        if (!object) {
          compareId = "";
          compareDetail.innerHTML =
            '<div class="eng-compare-empty">' +
            "<strong>Compare a related object</strong>" +
            "<p>Click a linked object under the selected object's relationship headings. " +
            "The root object stays visible while the related object opens here.</p>" +
            "</div>";
        } else {
          compareId = id;
          compareDetail.innerHTML = objectPanel(
            object,
            "Compared object",
            "compare"
          );
          compareDetail.scrollTop = 0;
        }
        updateSelectedSwapAction();
        updateCompareSelection();
        if (updateHistory) updateUrl();
      }

      function promoteComparedObject(id, updateHistory) {
        const object = data.objects[id];
        const previousRoot = data.objects[rootId];
        if (!object || !previousRoot || id === rootId) return;

        rootId = id;
        compareId = previousRoot.id;
        rootDetail.innerHTML = objectPanel(
          object,
          "Selected object",
          "compare"
        );
        compareDetail.innerHTML = objectPanel(
          previousRoot,
          "Compared object",
          "compare"
        );
        rootDetail.scrollTop = 0;
        compareDetail.scrollTop = 0;
        updateSelectedSwapAction();
        updateTreeSelection();
        updateCompareSelection();
        if (updateHistory) updateUrl();
      }

      root.addEventListener("click", (event) => {
        const toggleTarget = event.target.closest("[data-eng-tree-toggle]");
        if (toggleTarget && root.contains(toggleTarget)) {
          toggleGroup(toggleTarget.closest("[data-eng-tree-group]"));
          return;
        }

        const treeTarget = event.target.closest("[data-workspace-root-id]");
        if (treeTarget && root.contains(treeTarget)) {
          renderRoot(treeTarget.dataset.workspaceRootId, true);
          return;
        }

        const promoteTarget = event.target.closest(
          "[data-eng-promote-object-id]"
        );
        if (promoteTarget && root.contains(promoteTarget)) {
          promoteComparedObject(
            promoteTarget.dataset.engPromoteObjectId,
            true
          );
          return;
        }

        const compareTarget = event.target.closest("[data-compare-object-id]");
        if (compareTarget && root.contains(compareTarget)) {
          renderCompare(compareTarget.dataset.compareObjectId, true);
        }
      });

      treeToggles.forEach((toggle) => {
        toggle.addEventListener("keydown", (event) => {
          const group = toggle.closest("[data-eng-tree-group]");
          if (event.key === "ArrowRight") {
            event.preventDefault();
            expandUsefulBranches(group);
          } else if (event.key === "ArrowLeft") {
            event.preventDefault();
            setGroupExpanded(group, false);
          }
        });
      });

      if (collapseAllButton) {
        collapseAllButton.addEventListener("click", () => {
          treeGroups.forEach((group) => setGroupExpanded(group, false));
        });
      }

      if (searchInput) searchInput.addEventListener("input", applyTreeFilter);
      if (typeFilter) typeFilter.addEventListener("change", applyTreeFilter);

      const requested = initialUrl.searchParams.get("object");
      const initial =
        requested && data.objects[requested] ? requested : "";
      const compared = initialUrl.searchParams.get("compare");

      if (initial) {
        renderRoot(initial, false);
        if (compared && data.objects[compared] && compared !== initial) {
          renderCompare(compared, false);
        }
      }
      applyTreeFilter();
      updateUrl();
      initializePaneResizers();
    }

    const workspacePage = Boolean(
      document.querySelector("[data-eng-workspace]")
    );
    const explorerPage = Boolean(
      document.querySelector("[data-eng-explorer]")
    );
    document.documentElement.classList.toggle(
      "eng-workspace-page",
      workspacePage
    );
    document.body.classList.toggle("eng-workspace-page", workspacePage);
    document.documentElement.classList.toggle(
      "eng-explorer-page",
      explorerPage
    );
    document.body.classList.toggle("eng-explorer-page", explorerPage);

    initializeExplorer();
    initializeWorkspace();
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(initializePortalViews);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializePortalViews);
  } else {
    initializePortalViews();
  }
})();
