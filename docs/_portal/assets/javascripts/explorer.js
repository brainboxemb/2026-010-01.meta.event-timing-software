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

  function initializeExplorer() {
    const root = document.querySelector("[data-eng-explorer]");
    const dataNode = document.getElementById("eng-graph-data");
    if (!root || !dataNode) return;

    let data;
    try {
      data = JSON.parse(dataNode.textContent);
    } catch (error) {
      console.error("Unable to parse engineering graph data", error);
      return;
    }

    const rootDetail = root.querySelector("[data-eng-root-detail]");
    const compareDetail = root.querySelector("[data-eng-compare-detail]");
    const initialUrl = new URL(window.location.href);
    let rootId = "";
    let compareId = "";

    function selectedId(node) {
      return node.dataset.rootObjectId || node.dataset.engineeringId || "";
    }

    function compareButton(id, relationType, incoming) {
      const object = data.objects[id];
      if (!object) return "";
      return (
        '<button class="eng-relation" type="button" data-compare-object-id="' +
        escapeHtml(id) +
        '">' +
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

    function relationSection(title, relations, endpointKey, incoming) {
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
            compareButton(relation[endpointKey], relation.type, incoming)
          )
          .join("") +
        "</section>"
      );
    }

    function focusSection(id) {
      const focus = data.focus_depth_1[id];
      if (!focus) return "";
      const neighbors = focus.objects.filter((objectId) => objectId !== id);
      return (
        '<section class="eng-detail__focus">' +
        "<h3>One-hop context</h3>" +
        "<p>Incoming and outgoing graph neighbors at exact depth 1.</p>" +
        '<div class="eng-focus-list">' +
        neighbors
          .map((neighbor) => compareButton(neighbor, "one hop", false))
          .join("") +
        "</div></section>"
      );
    }

    function objectPanel(object, role) {
      const roleLabel = role === "root" ? "Selected object" : "Compared object";
      return (
        '<div class="eng-detail__role">' +
        escapeHtml(roleLabel) +
        "</div>" +
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
          false
        ) +
        relationSection(
          "Incoming relationships",
          object.incoming,
          "source",
          true
        ) +
        focusSection(object.id)
      );
    }

    function updateSelection() {
      root
        .querySelectorAll("[data-root-object-id], [data-engineering-id]")
        .forEach((node) => {
          node.classList.toggle("is-selected", selectedId(node) === rootId);
        });
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
      url.searchParams.delete("context");
      history.replaceState({}, "", url);
    }

    function renderRoot(id, updateHistory) {
      const object = data.objects[id];
      if (!object || !rootDetail) return;
      rootId = id;
      compareId = "";
      rootDetail.innerHTML = objectPanel(object, "root");
      renderCompare("", false);
      updateSelection();
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
          "<p>Click an Incoming, Outgoing or one-hop relation on the left. " +
          "The selected object stays visible while the related object opens here.</p>" +
          "</div>";
      } else {
        compareId = id;
        compareDetail.innerHTML = objectPanel(object, "compare");
      }
      updateSelection();
      if (updateHistory) updateUrl();
    }

    root.addEventListener("click", (event) => {
      const compareTarget = event.target.closest("[data-compare-object-id]");
      if (compareTarget && root.contains(compareTarget)) {
        renderCompare(compareTarget.dataset.compareObjectId, true);
        return;
      }

      const rootTarget = event.target.closest(
        "[data-root-object-id], [data-engineering-id]"
      );
      if (rootTarget && root.contains(rootTarget)) {
        renderRoot(selectedId(rootTarget), true);
      }
    });

    root.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;

      const compareTarget = event.target.closest("[data-compare-object-id]");
      if (compareTarget && root.contains(compareTarget)) {
        event.preventDefault();
        renderCompare(compareTarget.dataset.compareObjectId, true);
        return;
      }

      const rootTarget = event.target.closest(
        "[data-root-object-id], [data-engineering-id]"
      );
      if (rootTarget && root.contains(rootTarget)) {
        event.preventDefault();
        renderRoot(selectedId(rootTarget), true);
      }
    });

    const requested = initialUrl.searchParams.get("object");
    const initial =
      requested && data.objects[requested] ? requested : data.default_object;
    const compared = initialUrl.searchParams.get("compare");

    renderRoot(initial, false);
    if (compared && data.objects[compared] && compared !== initial) {
      renderCompare(compared, false);
    }
    updateUrl();
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(initializeExplorer);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeExplorer);
  } else {
    initializeExplorer();
  }
})();
