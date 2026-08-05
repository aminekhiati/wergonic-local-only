# Local Only — folder structure

Management artifacts for Wergonic. Synced between the Windows and Mac laptops
by `wsync` (git, private repo `wergonic-local-only`). Not part of any app repo.

**Run `wsync` after changing anything here**, so the other laptop gets it.

## Where things go

| Folder | What belongs in it |
|---|---|
| `Tasks/` | Task lists we hand to devs — the current version of each |
| `Audits/` | Findings: QA audits, bug audits, calculation issues to confirm |
| `Documentation/` | Reference docs — product, technical, QA onboarding |
| `Plans/` | Proposals and plans not executed yet (migrations, rebuilds) |
| `Reports/` | Data and usage analysis, org/cleanup reports |
| `Team/Performance_Reviews/` | Dev reviews: `exports/` holds the raw CSV, `reports/` the written review |
| `Team/Hiring/` | Interview material |
| `Translations/` | `en.json` / `de.json` plus the translation-manager docs |
| `_sources/` | The HTML each PDF is rendered from — keeps the doc folders to finished files only |
| `_scripts/` | Generator scripts that produce the PDFs |
| `Archive/` | Superseded versions. Nothing is deleted, just moved out of the way |

## Naming

`Title_Case_With_Underscores.pdf`, date suffix `_YYYY-MM-DD` when the document
is tied to a point in time (`Web_Improvement_Tasks_2026-07-27.pdf`).
Raw exports keep the filename the export tool gives them.

## Rules

- One current version per document lives in its folder; older ones go to `Archive/`.
- A PDF and the HTML it came from share a name — PDF in its topic folder, HTML in `_sources/`.
- `.obsidian/workspace.json` is deliberately not synced; it is per-laptop window layout.
