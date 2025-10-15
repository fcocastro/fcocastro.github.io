# Publications CSV — Schema & Allowed Values

This file documents the **`publications.csv`** format used by `build_publications.py` to generate `publications.html`.

> Put `publications.csv` in the same folder as `build_publications.py`, then run:
>
> ```bash
> python build_publications.py
> ```

---

## Columns (header row required)

| Column        | Required? | Purpose | Allowed / Recommended Values | Examples |
|---|---|---|---|---|
| `section`     | ✅ | Which list to put the entry in | **Accepted (case-insensitive; prefixes OK):** `journal` (`jour…`), `working` (`work…`), `conference` (`conf…`), `other` (anything else defaults to `other`) | `journal`, `working`, `conference`, `other` |
| `title`       | ✅ | Paper/article title | Free text | `Optimal Design of Default Donations` |
| `status`      | ⭕ | Status badge shown as a pill | Free text. **Recommended set for consistency:** `Published`, `In press`, `Forthcoming`, `Accepted`, `Cond. accept`, `Revise & resubmit`, `Under review`, `Working paper`, `Draft`, `Preprint`, `Presented` | `Under review`, `Working paper`, `Draft` |
| `year`        | ⭕ | Year badge & sorting | Prefer a 4‑digit year (`YYYY`). Sorting uses the first 4‑digit number it finds. | `2025` |
| `authors`     | ⭕ | Co‑authors text line | Free text. If **solo**, use `solo` (exact word) to show “solo”; anything else shows as “with …” | `solo`; `Castro, Francisco; Coauthor A; Coauthor B` |
| `venue`       | ⭕ | Journal/Conference name (as an extra pill) | Free text | `Management Science`; `INFORMS Annual Meeting` |
| `paper_url`   | ⭕ | “Paper” button | Any `http(s)` URL. Ideally a direct PDF. | `https://example.com/paper.pdf` |
| `slides_url`  | ⭕ | “Slides” button | Any `http(s)` URL | `https://example.com/slides.pdf` |
| `doi_url`     | ⭕ | “DOI” button (landing page) | Any `http(s)` URL (prefer `https://doi.org/...`) | `https://doi.org/10.1234/abcd.5678` |
| `abstract`    | ⭕ | Collapsible abstract body | Free text. Supports **LaTeX** via MathJax: inline `$...$`, display `$$...$$`. Preserve newlines. | `We study $u(x)=x^{1-\rho}/(1-\rho)$ ...` |
| `bibtex`      | ⭕ | Contents of the **Cite** dropdown | Paste full BibTeX. **If multi‑line**, wrap the CSV field in quotes. | `@article{...}` |
| `media`       | ⭕ | Pills inside **Media** dropdown | **Semicolon‑separated list** of `Label\|URL` pairs. URL optional. | `The Economist\|https://...; FT\|https://...` |

Legend: ✅ = required, ⭕ = optional.

> The builder **ignores any extra columns**, so you can add fields for your own tracking without breaking the page.

---

## Notes & Conventions

### 1) `section`
- Matching is **prefix-based**, case‑insensitive: `journal`, `jour.`, `Journal` → **journal**; `work`, `Working paper` → **working**; `conf`, `conference` → **conference**; everything else → **other**.

### 2) `status`
- Not restricted by the script; the list above is a **recommended vocabulary** for visual consistency.
- You can tailor per section, e.g. for conference items use `Presented`, `Proceedings`, `Extended abstract` if helpful.

### 3) `year`
- For correct sorting, include a **4‑digit year** somewhere in the field. The script looks for the first `YYYY` occurrence.
- If empty or malformed, the item falls back to the “no‑year” group in sorting.

### 4) `authors`
- If you want “solo”, use exactly `solo` (lowercase). Otherwise, whatever you put renders as “with …”
- Separate names with semicolons for readability: `Last, First; Last, First`

### 5) URLs (`paper_url`, `slides_url`, `doi_url`)
- Any regular `http(s)` link is fine.
- If **Paper** and **DOI** point to the same place, it’s OK; both buttons will show. (We can auto‑hide duplicates if you’d like.)

### 6) `abstract`
- Supports LaTeX via MathJax, e.g. `$x^2$`, `$$\int_0^1 f(x)\,dx$$`.
- To preserve line breaks inside CSV, wrap the cell in quotes and use actual newlines.

### 7) `bibtex`
- Paste the full entry; multi‑line is best (wrap in quotes). It appears inside the **Cite** dropdown.
- A **Copy** button is injected automatically.

### 8) `media`
- Format: `Label|URL; Label|URL; ...` (URL optional). Example:  
  `The Economist|https://...; Financial Times|https://...; Podcast Name|https://...`
- The **Media (n)** button shows the count automatically.

---

## Example Row

```csv
journal,Optimal Design of Default Donations,Under review,2025,"Castro, Francisco; Coauthor A; Coauthor B",TBD,https://example.com/paper.pdf,https://example.com/slides.pdf,https://doi.org/10.1234/abcd,"We study $u(x)=x^{1-\rho}/(1-\rho)$ and show $$q^* = \frac{\mu}{\rho\sigma^2}$$.","@article{castro_defaults_2025,
  title={Optimal Design of Default Donations},
  author={Castro, Francisco and ...},
  journal={TBD},
  year={2025}
}","The Economist|https://example.com/econ; Financial Times|https://example.com/ft"
```

---

## FAQ

**Q: Can I add extra columns (e.g., `code_url`, `data_url`)?**  
A: Yes. The builder ignores unknown columns. If you want extra buttons rendered, we can update the script to look for them.

**Q: Do I have to host PDFs?**  
A: No. `paper_url` can be a landing page. Direct PDFs give the best UX, but are not required.

**Q: Ordering within a section?**  
A: Sorted by section → **year (desc)** → title (A–Z).

**Q: Conferences vs. proceedings?**  
A: Use `section=conference`. Put the conference name in `venue` and an optional `status` like `Presented` or `Proceedings`.

---

## Template

Start with the provided template (also downloadable alongside this README) and add one row per paper. Keep the header row exactly as shown.

Happy publishing! 🎓
