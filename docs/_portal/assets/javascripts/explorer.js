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

    const detail = root.querySelector("[data-eng-detail]");
    const sourceHeader = root.querySelector("[data-eng-source-header]");
    const sourceBody = root.querySelector("[data-eng-source]");
    const contextButtons = root.querySelectorAll("[data-eng-context-mode]");
    const contextPanels = root.querySelectorAll("[data-eng-context-panel]");
    const initialUrl = new URL(window.location.href);
    let contextMode =
      initialUrl.searchParams.get("context") === "source"
        ? "source"
        : "architecture";

    function selectedId(node) {
      return node.dataset.objectId || node.dataset.engineeringId || "";
    }

    function setContextMode(mode, updateUrl) {
      contextMode = mode === "source" ? "source" : "architecture";
      contextButtons.forEach((button) => {
        const selected = button.dataset.engContextMode === contextMode;
        button.classList.toggle("is-selected", selected);
        button.setAttribute("aria-pressed", selected ? "true" : "false");
      });
      contextPanels.forEach((panel) => {
        panel.hidden = panel.dataset.engContextPanel !== contextMode;
      });
      if (updateUrl) {
        const url = new URL(window.location.href);
        url.searchParams.set("context", contextMode);
        history.replaceState({}, "", url);
      }
    }

    function objectButton(id, relationType, incoming) {
      const object = data.objects[id];
      if (!object) return "";
      return (
        '<button class="eng-relation" type="button" data-object-id="' +
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
            objectButton(relation[endpointKey], relation.type, incoming)
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
          .map((neighbor) => objectButton(neighbor, "one hop", false))
          .join("") +
        "</div></section>"
      );
    }

    function renderSource(object) {
      if (!sourceHeader || !sourceBody) return;
      const context = object.source_context;
      if (!context) {
        sourceHeader.innerHTML =
          "<strong>Source context unavailable</strong>";
        sourceBody.innerHTML =
          "<p>This object has no line-addressable authored source location.</p>";
        return;
      }

      sourceHeader.innerHTML =
        '<div class="eng-source-title">' +
        "<strong>" +
        escapeHtml(context.path) +
        "</strong>" +
        "<span>line " +
        escapeHtml(context.line) +
        " · showing " +
        escapeHtml(context.start) +
        "–" +
        escapeHtml(context.end) +
        "</span>" +
        "</div>" +
        '<a class="md-button" href="' +
        escapeHtml(object.source_url) +
        '">Open authored source</a>';

      sourceBody.innerHTML = context.lines
        .map((line) => {
          const focused = line.number === context.line ? " is-source-line" : "";
          return (
            '<div class="eng-source-line' +
            focused +
            '">' +
            '<span class="eng-source-line__number">' +
            escapeHtml(line.number) +
            "</span>" +
            '<span class="eng-source-line__text">' +
            escapeHtml(line.text || " ") +
            "</span>" +
            "</div>"
          );
        })
        .join("");
    }

    function render(id, updateUrl) {
      const object = data.objects[id];
      if (!object || !detail) return;

      root
        .querySelectorAll("[data-object-id], [data-engineering-id]")
        .forEach((node) => {
          node.classList.toggle("is-selected", selectedId(node) === id);
        });

      renderSource(object);

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
        focusSection(id);

      if (updateUrl) {
        const url = new URL(window.location.href);
        url.searchParams.set("object", id);
        url.searchParams.set("context", contextMode);
        history.replaceState({}, "", url);
      }
    }

    contextButtons.forEach((button) => {
      button.addEventListener("click", () => {
        setContextMode(button.dataset.engContextMode, true);
      });
    });

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
    setContextMode(contextMode, false);
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
