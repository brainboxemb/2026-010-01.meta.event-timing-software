# Document templates

These files are the starting point for new project documents.

Do not create a new document in an existing family from an empty file. Copy the
matching template, rename it according to `../12-GPD-documentation-guide.md`, replace the
marked placeholders and then add the document-specific content.

The templates intentionally contain reusable explanatory text. Keep that text when it
remains true for the new document; it exists to prevent each document from inventing a
different explanation of the same engineering relationship.

Normal introductory order:

```text
Purpose
Terms and abbreviations
Relationship to other documents
<document-family content>
```

Available templates:

- `GPD-template.md` — general project/support guidance when no more specific document type fits;
- `UC-template.md` — system use cases;
- `SSSD-template.md` — software-system specification/architecture;
- `ISD-template.md` — system-owned interface specification;
- `IDD-template.md` — concrete interface design description;
- `SSD-template.md` — combined software-item requirements/architecture;
- `SDD-template.md` — focused software-item detailed design;
- `SVP-template.md` — verification strategy;
- `VTS-template.md` — stable verification cases;
- `SIP-template.md` — implementation roadmap;
- `SDE-template.md` — development/engineering environment;
- `EXT-template.md` — external/parent-system input register;
- `SUM-template.md` — technical software user manual.

The SDP is a singular project document rather than a repeatable product-document
family. Its current structure is itself the maintained project baseline.
