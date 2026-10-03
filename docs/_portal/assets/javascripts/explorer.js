(function () {
  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function relationLabel(type, incoming) {
    const label = String(type).replaceAll("_", " ");
    if (!incoming) return label;
    if (type === "derived_from") return "derived from this";
    if (type === "satisfies") return "satisfies this";
    if (type === "verifies") return "verifies this";
    return label + " this";
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

    function relationButton(id, relationType, incoming, mode) {
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
        '<span class="eng-relation__type">' +
        escapeHtml(relationLabel(relationType, incoming)) +
        "</span>" +
        '<span class="eng-relation__object">' +
        escapeHtml(object.id) +
        " — " +
        escapeHtml(object.title) +
        "</span>" +
        "</button>"
      );
    }

    function relationSection(title, relations, endpointKey, incoming, mode) {
      const explanation = incoming
        ? "Declared by the listed source object and directed to this object."
        : "Declared by this object and directed to the listed target object.";
      if (!relations.length) {
        return (
          '<section class="eng-detail__relations">' +
          "<h3>" +
          escapeHtml(title) +
          "</h3><p>" +
          escapeHtml(explanation) +
          "</p><p>None in this production slice.</p></section>"
        );
      }
      return (
        '<section class="eng-detail__relations"><h3>' +
        escapeHtml(title) +
        "</h3><p>" +
        escapeHtml(explanation) +
        "</p>" +
        relations
          .map((relation) =>
            relationButton(relation[endpointKey], relation.type, incoming, mode)
          )
          .join("") +
        "</section>"
      );
    }

    function focusSection(id, mode) {
      const focus = data.focus_depth_1[id];
      if (!focus) return "";
      const neighbors = focus.objects.filter((objectId) => objectId !== id);
      return (
        '<section class="eng-detail__focus">' +
        "<h3>One-hop context</h3>" +
        "<p>Incoming and outgoing graph neighbors at exact depth 1.</p>" +
        '<div class="eng-focus-list">' +
        neighbors
          .map((neighbor) => relationButton(neighbor, "one hop", false, mode))
          .join("") +
        "</div></section>"
      );
    }

    function objectPanel(object, roleLabel, mode) {
      return (
        (roleLabel
          ? '<div class="eng-detail__role">' +
            escapeHtml(roleLabel) +
            "</div>"
          : "") +
        '<div class="eng-detail__header">' +
        '<span class="eng-object-type">' +
        escapeHtml(object.type_label) +
        "</span>" +
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
        "</div>" +
        relationSection(
          "Outgoing relationships",
          object.outgoing,
          "target",
          false,
          mode
        ) +
        relationSection(
          "Incoming relationships",
          object.incoming,
          "source",
          true,
          mode
        ) +
        focusSection(object.id, mode)
      );
    }

    function initializeExplorer() {
      const root = document.querySelector("[data-eng-explorer]");
      if (!root) return;
      const detail = root.querySelector("[data-eng-detail]");
      const initialUrl = new URL(window.location.href);

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
      const initial =
        requested && data.objects[requested] ? requested : data.default_object;
      render(initial, false);
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
      const resultCount = root.querySelector("[data-eng-tree-count]");
      const treeItems = Array.from(
        root.querySelectorAll("[data-workspace-root-id]")
      );
      const treeGroups = Array.from(
        root.querySelectorAll("[data-eng-tree-group]")
      );
      const initialUrl = new URL(window.location.href);
      let rootId = "";
      let compareId = "";

      function updateTreeSelection() {
        let selectedNode = null;
        treeItems.forEach((node) => {
          const selected = node.dataset.workspaceRootId === rootId;
          node.classList.toggle("is-selected", selected);
          if (selected) {
            selectedNode = node;
            node.setAttribute("aria-current", "true");
            const group = node.closest("[data-eng-tree-group]");
            if (group) group.open = true;
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

      function updateUrl() {
        const url = new URL(window.location.href);
        url.searchParams.set("object", rootId);
        if (compareId) {
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
          if ((query || selectedType) && visible) group.open = true;
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
            "<p>Click an Incoming, Outgoing or one-hop relation in the selected object. " +
            "The root object stays visible while the related object opens here.</p>" +
            "</div>";
        } else {
          compareId = id;
          compareDetail.innerHTML = objectPanel(
            object,
            "Compared object",
            "compare"
          );
        }
        updateCompareSelection();
        if (updateHistory) updateUrl();
      }

      root.addEventListener("click", (event) => {
        const treeTarget = event.target.closest("[data-workspace-root-id]");
        if (treeTarget && root.contains(treeTarget)) {
          renderRoot(treeTarget.dataset.workspaceRootId, true);
          return;
        }

        const compareTarget = event.target.closest("[data-compare-object-id]");
        if (compareTarget && root.contains(compareTarget)) {
          renderCompare(compareTarget.dataset.compareObjectId, true);
        }
      });

      if (searchInput) searchInput.addEventListener("input", applyTreeFilter);
      if (typeFilter) typeFilter.addEventListener("change", applyTreeFilter);

      const requested = initialUrl.searchParams.get("object");
      const initial =
        requested && data.objects[requested] ? requested : data.default_object;
      const compared = initialUrl.searchParams.get("compare");

      renderRoot(initial, false);
      if (compared && data.objects[compared] && compared !== initial) {
        renderCompare(compared, false);
      }
      applyTreeFilter();
      updateUrl();
    }

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
