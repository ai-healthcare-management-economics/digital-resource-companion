# Artificial Intelligence in Healthcare Management and Economics
## Digital Resource Companion
*Evidence, Value, Governance, and Lifecycle Decision-Making*

**Muthana Zouri and Carmen Marinela Cumpăt**  
Developed and maintained by the authors  
**V1.0 | September 2026**

The Digital Resource Companion is developed and maintained independently by Muthana Zouri and Carmen Marinela Cumpăt to accompany *Artificial Intelligence in Healthcare Management and Economics: Evidence, Value, Governance, and Lifecycle Decision-Making*. The authors are responsible for its content, maintenance, and subsequent updates.

## Start here

Read [START HERE](START_HERE.pdf), open the [local Web Companion](docs/index.html), or use the [online Web Companion](https://ai-healthcare-management-economics.github.io/digital-resource-companion/). Select resources by chapter, decision stage, or resource identifier rather than completing every form.

| Distribution | Intended use |
|---|---|
| **Reader and Practitioner Edition** | Guided practical collection, forms, workbook, cases, guides, readable catalogues, main companion PDF, and offline website. |
| **Core Tools Pack** | The principal editable and printable forms, consolidated workbook, and completion guidance. |
| **Canonical Source** | Complete editable resources, analytical code and notebooks, structured records and schemas, process sources, catalogues, publication sources, and website. |

The consolidated core forms and workbook are included in both larger distributions. The **Core Tools Pack** is a separate lightweight convenience download, not a separate companion edition or a nested archive within these distributions.

## Scope and navigation

V1.0 follows the book's **four parts and twelve chapters** and contains **126 catalogued resources**: 19 core institutional records, 47 specialist tools, 16 worked examples, the common case-analysis method, seven reference guides, and 36 Python analytical modules. The figure and table catalogues cross-reference **29 book figures and 38 book tables**, including two front-matter tables. They are reference indexes, not additional companion resources. The book's figure images are not reproduced in the package; consult the printed or digital book for the definitive artwork. Companion process diagrams and analytical plots remain included.

| Folder | Purpose |
|---|---|
| `chapters/` | Individual chapter-aligned institutional records, specialist tools, reference guides, and analytical modules. |
| `worked_examples/` | Sixteen synthetic worked cases and `AIHE-CASE00`, the common method. |
| `process/` | Cross-chapter decision lifecycle, pathways, stage definitions, and resource selection. |
| `bundles/` | Consolidated Word/PDF forms and Excel workbook with completion guidance. |
| `publications/` | Main companion PDF and its editable Word source. |
| `catalogs/` | Resource, case, analytical, relationship, figure, and table indexes. |
| `docs/` | GitHub Pages website, browser forms, locally available schemas, and process pages. |

Use [RESOURCE_INDEX.md](RESOURCE_INDEX.md) or the [resource browser](docs/resources.html). The four core families address **A: framing, participation, readiness, and data; B: economics, affordability, benefits, and modelling; C: quality, risk, accountability, and communication; D: procurement and lifecycle governance**.

The prefix **AIHE** is retained as the stable identifier for companion resources; it does not abbreviate the current book title.

## Source maintenance and release control

The book governs conceptual definitions and chapter alignment. Individual records in `chapters/`, worked cases, and process sources govern resource-specific content. Catalogues, consolidated documents, and website copies must be synchronized when these sources change. A marked-up consolidated document is a review input, not a separate master resource.

Retain resource identifiers and exact versions. Check affected content, structured records, formulas, examples, website paths, and document layout before rebuilding distribution packages. `CHECKSUMS_SHA256.txt` is the complete file inventory with SHA-256 hashes; it excludes itself. Verify an unchanged extracted copy from this directory with `sha256sum -c CHECKSUMS_SHA256.txt` where that utility is available. Never use checksum validity as a substitute for content review.

Presentation labels use month and year. Preserve precise recorded release, evidence, access, approval, incident, and local-modification dates wherever they carry substantive meaning. A cover month does not establish an evidence cut-off.

## Analytical and institutional use

For an institutional decision, create a governed local copy, replace synthetic examples with authorized evidence, record the intervention and comparator, identify accountable owners, and preserve mandatory safeguards independently of aggregate results. Record conditions, monitoring, review dates, material-change triggers, and a credible exit route.

For computation, select a module through `catalogs/PYTHON_MODULE_CATALOG.xlsx`, read its README, and use its supplied input examples and environment instructions. Preserve inputs, code, assumptions, environments, and outputs; independently check consequential results. Scripts and notebooks are teaching and analytical resources, not validated clinical instruments.

**Do not enter patient identifiers, credentials, private keys, confidential contracts, or restricted institutional information into public demonstrations or uncontrolled files.** See [the limited-use notice](LIMITED_USE_AND_DISCLAIMER.md). Report corrections through the repository; do not post sensitive security details or restricted data in a public issue.

## Public release assets

- `AIHE_Reader_Practitioner_V1.0.zip`
- `AIHE_Core_Tools_V1.0.zip`
- `AIHE_Canonical_V1.0.zip`
- `Digital_Resource_Companion_V1.0.pdf`
- `AIHE_Core_Resource_Forms_V1.0.pdf`
- `AIHE_Core_Resource_Forms_V1.0.docx`
- `AIHE_Core_Resource_Workbooks_V1.0.xlsx`
- `AIHE_V1.0_Release_Checksums_SHA256.txt`

START HERE is packaged guidance, not an additional release attachment. Its editable source and the editable Word edition of the main companion are retained in Canonical; the Reader Edition supplies their PDFs. The release-level checksum file covers the three ZIP packages and four standalone resources.

## Citation and access

[Canonical repository](https://github.com/ai-healthcare-management-economics/digital-resource-companion) · [GitHub Releases](https://github.com/ai-healthcare-management-economics/digital-resource-companion/releases) · [Web Companion](https://ai-healthcare-management-economics.github.io/digital-resource-companion/) · [Persistent companion record](https://doi.org/10.5281/zenodo.21753927)

The book identifies `10.5281/zenodo.21753927` as the **Concept DOI**. For reproducibility, obtain the version-specific DOI from the archived release used and retain the resource identifier, exact version, release date, access date, evidence cut-off, and local changes. Cite the book separately for its conceptual and methodological content. See [CITATION.cff](CITATION.cff).

## Licence

Documentation, forms, workbooks, diagrams, worked examples, synthetic datasets, and original website content use **CC BY-NC 4.0**, unless a file-specific notice states otherwise. Original Python, Jupyter, JavaScript, and repository code use the **MIT Licence**. Third-party material retains its original rights. See [LICENSE.md](LICENSE.md) and [LICENSE-CODE-MIT.txt](LICENSE-CODE-MIT.txt).
