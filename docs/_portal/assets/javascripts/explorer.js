(function () {
  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function relationLabel(type) {
    return String(type).replaceAll("_", " ");
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

    const detail = root.querySelector("[data-eng-detail]");

    function selectedId(node) {
      return node.dataset.objectId || node.dataset.engineeringId || "";
    }

    function objectButton(id, relationType) {
      const object = data.objects[id];
      if (!object) return "";
      return (
        '<button class="eng-relation" type="button" data-object-id="' +
        escapeHtml(id) +
        '">' +
        '<span class="eng-relation__type">' +
        escapeHtml(relationLabel(relationType)) +
        "</span>" +
        '<span class="eng-relation__object">' +
        escapeHtml(object.id) +
        " — " +
        escapeHtml(object.title) +
        "</span>" +
        "</button>"
      );
    }

    function relationSection(title, relations, endpointKey) {
      if (!relations.length) {
        return (
          '<section class="eng-detail__relations">' +
          "<h3>" +
          escapeHtml(title) +
          "</h3><p>None in this production slice.</p></section>"
        );
      }
      return (
        '<section class="eng-detail__relations"><h3>' +
        escapeHtml(title) +
        "</h3>" +
        relations
          .map((relation) => objectButton(relation[endpointKey], relation.type))
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
        neighbors.map((neighbor) => objectButton(neighbor, "one hop")).join("") +
        "</div></section>"
      );
    }

    function render(id, updateUrl) {
      const object = data.objects[id];
      if (!object || !detail) return;

      root
        .querySelectorAll("[data-object-id], [data-engineering-id]")
        .forEach((node) => {
          node.classList.toggle("is-selected", selectedId(node) === id);
        });

      detail.innerHTML =
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
          ? '<div class="eng-detail__summary">' +
            object.content_html +
            "</div>"
          : "") +
        '<div class="eng-detail__actions">' +
        '<a class="md-button md-button--primary" href="../objects/' +
        encodeURIComponent(object.id) +
        '/">Open details & relations</a>' +
        '<a class="md-button" href="' +
        escapeHtml(object.source_url) +
        '">Open source definition</a>' +
        "</div>" +
        relationSection("Outgoing", object.outgoing, "target") +
        relationSection("Incoming", object.incoming, "source") +
        focusSection(id);

      if (updateUrl) {
        const url = new URL(window.location.href);
        url.searchParams.set("object", id);
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

    const requested = new URL(window.location.href).searchParams.get("object");
    const initial =
      requested && data.objects[requested] ? requested : data.default_object;
    render(initial, false);
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(initializeExplorer);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeExplorer);
  } else {
    initializeExplorer();
  }
})();
