# Engineering graph review evidence

This is Migration 013 native MyST/Sphinx-Needs production-canary evidence.

- source revision: dca0d6d0b488689778b5b82289f21fe5a0ec6dee
- authoritative authoring: selected MyST/Sphinx-Needs objects in the event-timing engineering documents
- native Sphinx reader: [native/index.html](native/index.html)
- Sphinx-Needs export: [needs.json](needs.json)
- normalized human review: [review.md](review.md)
- normalized graph: [engineering-graph.json](engineering-graph.json)
- consumer-owned Needs configuration: [input/conf.py](input/conf.py) · [input/schemas.json](input/schemas.json)

Requirements own derived_from, design owns satisfies, and verification owns verifies.
Sphinx-Needs generates the inverse/backlink context. Diagram object_id values reference the same engineering objects.
