#!/usr/bin/env python3
"""
build_publications.py
Reads publications.csv and generates publications.html with your current styling
and features (sections, numbering, Cite/Media overlays, MathJax, collapsible sections, etc.).

Usage:
  python build_publications.py  # writes publications.html in the same folder
"""
from __future__ import annotations
import csv, html, os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(HERE, "publications.csv")
OUT_FILE = os.path.join(HERE, "publications.html")

# --- Icons used outside helper functions ---
ICON_COMMENT = (
    '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M21 15a2 2 0 0 1-2 2H8l-4 4v-4H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'
)

# --- Helper rendering ---

def esc(s: str) -> str:
    return html.escape(s or "", quote=True)

def pills(status: str, year: str, venue: str) -> str:
    ICON_STATUS = '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20l9-5-9-5-9 5 9 5z"/><path d="M12 12l9-5-9-5-9 5 9 5z"/></svg>'
    ICON_YEAR = '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>'
    out = []
    if status: out.append(f'<span class="pill" title="Status">{ICON_STATUS} {esc(status)}</span>')
    if year:   out.append(f'<span class="pill" title="Year">{ICON_YEAR} {esc(year)}</span>')
    if venue:  out.append(f'<span class="pill" title="Venue">{esc(venue)}</span>')
    return "\n          ".join(out)

def links(row: dict) -> str:
    parts = ['<div class="links">']
    # Paper (label override via CSV column: paper_label; default "Paper")
    if row.get("paper_url"):
        paper_label = (row.get("paper_label") or "Paper").strip() or "Paper"
        parts.append(f'<a class="btn" href="{esc(row["paper_url"])}" itemprop="url">{esc(paper_label)}</a>')

    # Slides / DOI (unchanged, but you can add similar *_label overrides later)
    if row.get("slides_url"):
        parts.append(f'<a class="btn" href="{esc(row["slides_url"])}">Slides</a>')
    if row.get("doi_url"):
        parts.append(f'<a class="btn" href="{esc(row["doi_url"])}">DOI</a>')

    # Cite
    if row.get("bibtex"):
        cite = esc(row["bibtex"]).replace("&amp;#10;", "&#10;")
        parts.append(
            '<details class="tool cite">'
            '<summary class="btn" aria-label="Cite this paper">'
            '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16l4-4h6a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/></svg>'
            '<span>Cite</span></summary>'
            f'<div class="dropdown cite-body"><pre><code>{cite}</code></pre></div>'
            '</details>'
        )

    # Media
    media_raw = (row.get("media") or "").strip()
    if media_raw:
        pills_html = []
        for item in media_raw.split(";"):
            label, url = (item.split("|", 1) + [""])[:2]
            label = label.strip()
            url = url.strip()
            if not label:
                continue
            if url:
                pills_html.append(f'<a class="media-pill" href="{esc(url)}" rel="noopener">{esc(label)}</a>')
            else:
                pills_html.append(f'<span class="media-pill">{esc(label)}</span>')
        parts.append(
            '<details class="tool media">'
            '<summary class="btn" aria-label="Media coverage">'
            '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h10l6 6v8a2 2 0 0 1-2 2z"/></svg>'
            '<span>Media</span></summary>'
            '<div class="dropdown"><div class="media-list">'
            + "".join(pills_html) +
            '</div></div></details>'
        )
    parts.append("</div>")
    return "\n            ".join(parts)


def article(row: dict) -> str:
    title = esc(row.get("title", ""))
    authors = (row.get("authors") or "").strip()
    if not authors or authors.lower() == "solo":
        authors_html = "solo"
    else:
        authors_html = f"with {esc(authors)}"

    # Optional comment line (CSV column: comment)
    comment = (row.get("comment") or "").strip()
    comment_html = f'''
        <div class="comment">{ICON_COMMENT} {esc(comment)}</div>
    ''' if comment else ""

    abstract = (row.get("abstract") or "").replace("\r\n","\n").strip()
    abstract_html = f'''
        <details class="abstract">
          <summary><svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg> Show abstract</summary>
          <div class="abs-body" itemprop="description">{fmt(abstract)}</div>
        </details>''' if abstract else ""
    return f'''
      <article class="paper" itemscope itemtype="https://schema.org/ScholarlyArticle">
        <div class="title-row">
          <h3 class="title" itemprop="headline">{title}</h3>
          {links(row)}
        </div>
        <div class="meta">
          {pills(row.get("status",""), row.get("year",""), row.get("venue",""))}
        </div>
        <div class="authors">{authors_html}</div>
        {comment_html}
        {abstract_html}
      </article>'''

def normalize_section(s: str) -> str:
    s = (s or "").strip().lower()
    if s.startswith("jour"): return "journal"
    if s.startswith("work"): return "working"
    if s.startswith("conf"): return "conference"
    return "other"

def read_rows(csv_path: str) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rows.append({k.strip(): (v or "").strip() for k,v in r.items()})
        return rows

def fmt(s: str) -> str:
    """Escape first, then allow *italic*, _italic_, **bold**, __bold__,
    and whitelisted <em>/<i>/<strong>/<b> HTML tags."""
    t = esc(s or "")
    # Markdown → HTML
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"__(.+?)__", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<em>\1</em>", t)
    # Whitelist a few tags if user typed raw HTML in CSV
    t = (t.replace("&lt;em&gt;", "<em>").replace("&lt;/em&gt;", "</em>")
           .replace("&lt;i&gt;", "<em>").replace("&lt;/i&gt;", "</em>")
           .replace("&lt;strong&gt;", "<strong>").replace("&lt;/strong&gt;", "</strong>")
           .replace("&lt;b&gt;", "<strong>").replace("&lt;/b&gt;", "</strong>"))
    return t


# --- HTML shell ---
SHELL = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Publications — Francisco Castro</title>
  <style>
    :root{
      --accent:#0ea5e9; --text:#111827; --muted:#6b7280; --bg:#ffffff; --card:#f9fafb; --radius:12px;
      --profile-img:url('./assets/me.jpg');
    }
    @media (prefers-color-scheme: dark){ :root{ --text:#e5e7eb; --muted:#9ca3af; --bg:#0b1020; --card:#0f172a; --accent:#38bdf8 } }
    *{box-sizing:border-box}
    html,body{margin:0; padding:0; background:var(--bg); color:var(--text); font:15px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Inter,Helvetica,Arial}
    a{color:var(--accent); text-decoration:none}
    a:hover{text-decoration:underline}

    .wrap{max-width:860px; margin:40px auto; padding:0 18px}
    header{display:flex; align-items:center; justify-content:space-between; margin-bottom:22px}
    .site-title{font-weight:700; font-size:20px}
    nav{display:flex; gap:16px}

    /* Section header + toggle (collapsible) */
    h2{
      margin:24px 0 10px; font-size:22px; line-height:1.2;
      padding-left:8px; border-left:4px solid var(--accent);
      display:flex; align-items:center; gap:10px;
    }
    h2 .toggle{
      appearance:none; background:none; border:0; padding:0; margin:0;
      font:inherit; color:inherit; cursor:pointer; display:inline-flex; align-items:center; gap:8px;
    }
    .caret{ width:14px; height:14px; transition: transform .2s ease; }
    .pub-sec.collapsed .paper-list{ display:none; }
    .pub-sec.collapsed h2 .caret{ transform: rotate(-90deg); }

    .subtle{color:var(--muted)}

    :root{ /* Section accent colors */
      --accent-journal: var(--accent);
      --accent-conference: #6366f1; /* indigo */
      --accent-working: #f59e0b;    /* amber */
      --accent-other: #64748b;      /* slate */
    }

    /* --- Single-column compact list --- */
    .paper-list{display:block; counter-reset: paper}
    .paper{position:relative; padding:10px 12px 8px 40px; margin:8px 0; border-left:3px solid var(--accent); background:transparent; border-radius:0}
    .paper::before{counter-increment: paper; content: counter(paper); position:absolute; left:8px; top:10px; width:20px; height:20px; border-radius:999px; display:grid; place-items:center; font-weight:700; font-size:12px; color:var(--text); background:var(--card); border:1px solid rgba(0,0,0,.12)}
    @media (prefers-color-scheme: dark){ .paper::before{border-color:rgba(255,255,255,.18)} }
    .paper + .paper{border-top:1px solid rgba(0,0,0,.06)}
    @media (prefers-color-scheme: dark){ .paper + .paper{border-color:rgba(255,255,255,.08)} }

    /* Per-section accent overrides */
    #journal{ border-left-color: var(--accent-journal) }
    #journal-papers .paper{ border-left-color: var(--accent-journal) }

    #working{ border-left-color: var(--accent-working) }
    #working-papers .paper{ border-left-color: var(--accent-working) }

    #conference{ border-left-color: var(--accent-conference) }
    #conf-papers .paper{ border-left-color: var(--accent-conference) }

    #other{ border-left-color: var(--accent-other) }
    #other-articles .paper{ border-left-color: var(--accent-other) }

    .title-row{display:flex; align-items:start; gap:10px}
    .title{font-size:16.5px; font-weight:650; margin:0; line-height:1.25; flex:1}

    .links{display:flex; gap:6px; flex-wrap:wrap; align-items:center; position:relative}
    .btn{display:inline-flex; align-items:center; gap:6px; padding:3px 7px; border-radius:9px; font-size:12px; border:1px solid rgba(0,0,0,.10); background:#fff0}
    @media (prefers-color-scheme: dark){ .btn{border-color:rgba(255,255,255,.15)} }

    .meta{display:flex; flex-wrap:wrap; gap:8px; margin:4px 0 0 0; font-size:12.5px; color:var(--muted)}
    .authors{margin:2px 0 0 0; font-size:12.5px; color:var(--muted)}

    /* Pill + icon alignment */
    .pill{
      display:inline-flex; align-items:center; gap:6px;
      padding:2px 8px; line-height:1; border-radius:999px;
      border:1px solid rgba(0,0,0,.10);
    }
    @media (prefers-color-scheme: dark){ .pill{border-color:rgba(255,255,255,.18)} }
    .i{width:14px; height:14px; display:inline-block; flex:0 0 auto; vertical-align:middle; transform:translateY(.5px)}

    /* Comment line */
    .comment{margin:4px 0 0; font-size:12.5px; color:var(--muted); display:flex; align-items:center; gap:6px}
    .comment .i{width:14px; height:14px}

    /* Abstract */
    details.abstract{margin-top:6px}
    details.abstract summary{
      list-style:none; cursor:pointer; display:inline-flex; align-items:center; gap:8px;
      user-select:none; color:var(--accent); font-weight:500; font-size:12.5px;
    }
    details.abstract summary::-webkit-details-marker{display:none}
    .chev{width:12px; height:12px; transition:transform .2s ease}
    details[open] .chev{transform: rotate(90deg)}
    .abs-body{margin:6px 0 0; font-size:13px}

    /* Masthead */
    .masthead{display:flex; align-items:center; gap:12px; padding:10px 0 8px; border-bottom:1px solid rgba(0,0,0,.06); margin-bottom:8px}
    @media (prefers-color-scheme: dark){ .masthead{border-color:rgba(255,255,255,.08)} }
    .avatar{width:56px; height:56px; border-radius:999px; background:var(--profile-img) center/cover no-repeat; border:1px solid rgba(0,0,0,.12)}
    @media (prefers-color-scheme: dark){ .avatar{border-color:rgba(255,255,255,.18)} }
    .page-title{margin:0; font-size:18px; font-weight:750}
    .page-subtle{margin:2px 0 0 0; color:var(--muted); font-size:13.5px}
    .head-actions{display:none} /* old 'Show all abstracts' hidden */

    /* Subnav */
    .subnav{position:sticky; top:0; background:var(--bg); z-index:5; border-bottom:1px solid rgba(0,0,0,.06); padding:8px 0; margin:6px 0 12px}
    @media (prefers-color-scheme: dark){ .subnav{border-color:rgba(255,255,255,.08)} }
    .subnav-inner{display:flex; align-items:center; gap:12px; flex-wrap:wrap}
    .subnav-name{font-weight:700; color:var(--text)}
    .subnav-links{display:flex; gap:6px; flex-wrap:wrap}
    .subnav a{display:inline-block; padding:4px 8px; border-radius:8px; font-size:13px; color:var(--muted); border:1px solid transparent}
    .subnav a:hover{border-color:rgba(0,0,0,.10); text-decoration:none}
    .subnav a.active{color:var(--text); border-color:rgba(0,0,0,.10); background:rgba(0,0,0,.03)}
    @media (prefers-color-scheme: dark){ .subnav a.active{background:rgba(255,255,255,.06); border-color:rgba(255,255,255,.18)} }
    h2{scroll-margin-top:60px}

    /* Cite/Media dropdowns */
    details.cite, details.media{margin-top:6px}
    details.cite summary, details.media summary{list-style:none; cursor:pointer; display:inline-flex; align-items:center; gap:6px; user-select:none; color:var(--accent); font-weight:500}
    details.cite summary::-webkit-details-marker, details.media summary::-webkit-details-marker{display:none}
    .cite-body{margin:6px 0 0; font-size:12.5px; background:var(--card); border-radius:8px; padding:8px 10px; overflow:auto}
    .media-list{display:flex; flex-wrap:wrap; gap:6px; margin-top:6px}
    .media-pill{display:inline-flex; align-items:center; gap:6px; font-size:12px; border:1px solid rgba(0,0,0,.10); padding:3px 7px; border-radius:999px; background:#fff0}

    /* Inline tools */
    .links details.tool{position:relative; display:inline-block}
    .links details.tool summary{padding:4px; border-radius:8px; border:1px solid rgba(0,0,0,.10)}
    @media (prefers-color-scheme: dark){ .links details.tool summary{border-color:rgba(255,255,255,.15)} }
    .links details.tool .dropdown{display:none; position:absolute; right:0; top:calc(100% + 6px); min-width:320px; max-width:520px; background:var(--card); border:1px solid rgba(0,0,0,.1); border-radius:10px; padding:8px 10px; box-shadow:0 6px 24px rgba(0,0,0,.08); z-index:20}
    @media (prefers-color-scheme: dark){ .links details.tool .dropdown{border-color:rgba(255,255,255,.15)} }
    .links details.tool[open] .dropdown{display:block}
    .links details.cite, .links details.media{margin-top:0}
    .links .tool .i{width:16px; height:16px}

    /* Dropdown positioning helpers */
    .links details.tool.align-left .dropdown{right:auto; left:0}
    .links details.tool.full .dropdown{left:0; right:0; width:auto; max-width:none}

    /* Copy BibTeX button */
    .copy-row{display:flex; justify-content:flex-end; margin-bottom:6px}
    .copy-btn{display:inline-flex; align-items:center; gap:6px; padding:3px 8px; border-radius:8px; font-size:12px; border:1px solid rgba(0,0,0,.10); background:#fff0; cursor:pointer}
    .copy-btn:hover{transform:translateY(-1px)}
  </style>
  <script>
    window.MathJax = {
      tex: { inlineMath: [['$','$'], ['\\(','\\)']], displayMath: [['$$','$$'], ['\\[','\\]']], processEscapes: true },
      options: { skipHtmlTags: ['script','noscript','style','textarea','pre','code'] }
    };
  </script>
  <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="site-title">Francisco Castro</div>
      <nav>
        <a href="./index.html">Home</a>
        <a href="./publications.html" aria-current="page">Publications</a>
        <a href="./teaching.html">Teaching</a>
        <a href="./cv.html">CV</a>
      </nav>
    </header>

    <section class="masthead" role="region" aria-label="Page header">
      <div class="avatar" aria-hidden="true"></div>
      <div>
        <h1 class="page-title">Publications</h1>
        <p class="page-subtle">Browse my research: journal papers, conference proceedings, and working papers.</p>
      </div>
    </section>

    <nav class="subnav" aria-label="Publications sections">
      <div class="subnav-inner">
        <div class="subnav-links">
          <a href="#journal">Journal Papers</a>
          <a href="#conference">Conference Proceedings</a>
          <a href="#working">Working Papers</a>
          <a href="#other">Other Articles</a>
        </div>
      </div>
    </nav>

    <section class="pub-sec" data-sec="journal">
      <h2 id="journal">
        <button class="toggle" aria-expanded="true" aria-controls="journal-papers">
          <svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M6 9l6 6 6-6"/>
          </svg>
          Journal Papers
        </button>
      </h2>
      <div class="paper-list" id="journal-papers">
{{JOURNAL_ITEMS}}
      </div>
    </section>



    <section class="pub-sec" data-sec="conference">
      <h2 id="conference">
        <button class="toggle" aria-expanded="true" aria-controls="conf-papers">
          <svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M6 9l6 6 6-6"/>
          </svg>
          Conference Proceedings
        </button>
      </h2>
      <div class="paper-list" id="conf-papers">
{{CONF_ITEMS}}
      </div>
    </section>

    <section class="pub-sec" data-sec="working">
      <h2 id="working">
        <button class="toggle" aria-expanded="true" aria-controls="working-papers">
          <svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M6 9l6 6 6-6"/>
          </svg>
          Working Papers
        </button>
      </h2>
      <div class="paper-list" id="working-papers">
{{WORKING_ITEMS}}
      </div>
    </section>

    <section class="pub-sec" data-sec="other">
      <h2 id="other">
        <button class="toggle" aria-expanded="true" aria-controls="other-articles">
          <svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M6 9l6 6 6-6"/>
          </svg>
          Other Articles
        </button>
      </h2>
      <div class="paper-list" id="other-articles">
{{OTHER_ITEMS}}
      </div>
    </section>

  </div>

  <script>
    // Highlight current section in subnav as you scroll
    (function(){
      const ids = ['journal','conference','working','other'];
      const linkFor = id => document.querySelector('.subnav a[href="#'+id+'"]');
      const links = new Map(ids.map(id => [id, linkFor(id)]));
      const obs = new IntersectionObserver((entries)=>{
        entries.forEach(e => {
          if (e.isIntersecting) {
            links.forEach(a => a && a.classList.remove('active'));
            const a = links.get(e.target.id);
            if (a) a.classList.add('active');
          }
        });
      }, { rootMargin: '-55% 0px -40% 0px', threshold: 0.01 });
      ids.forEach(id => { const el = document.getElementById(id); if (el) obs.observe(el); });
    })();
  </script>
  <script>
    // Close Cite/Media dropdowns when clicking outside or pressing Esc
    (function(){
      function closeAllExcept(target){
        document.querySelectorAll('.links details.tool[open]').forEach(d => {
          if (!target || !d.contains(target)) d.removeAttribute('open');
        });
      }
      document.addEventListener('click', function(e){ closeAllExcept(e.target); });
      document.addEventListener('keydown', function(e){ if (e.key === 'Escape') closeAllExcept(null); });
    })();
  </script>
  <script>
    (function(){
      // Media (n) badge
      document.querySelectorAll('.links details.media').forEach(function(det){
        var count = det.querySelectorAll('.media-list a').length;
        var label = det.querySelector('summary span');
        if (label) { label.textContent = count ? 'Media ('+count+')' : 'Media'; }
      });

      // Copy BibTeX button
      document.querySelectorAll('.links details.cite').forEach(function(det){
        var drop = det.querySelector('.dropdown'); if (!drop) return;
        if (!drop.querySelector('.copy-row')){
          var row = document.createElement('div'); row.className='copy-row';
          var btn = document.createElement('button'); btn.type='button'; btn.className='copy-btn'; btn.textContent='Copy';
          row.appendChild(btn); drop.insertBefore(row, drop.firstChild);
          btn.addEventListener('click', function(){
            var pre = drop.querySelector('pre'); var txt = pre ? pre.innerText : '';
            if (navigator.clipboard && navigator.clipboard.writeText){
              navigator.clipboard.writeText(txt).then(function(){ var prev=btn.textContent; btn.textContent='Copied!'; setTimeout(function(){ btn.textContent=prev;}, 1200); });
            }
          });
        }
      });

      // Smarter overlay positioning on open
      function positionDropdown(det){
        det.classList.remove('align-left','full');
        var drop = det.querySelector('.dropdown'); if (!drop) return;
        var rect = drop.getBoundingClientRect();
        var vw = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
        if (rect.right > vw - 8) det.classList.add('align-left');
        if (rect.width > vw * 0.92 || vw < 500) det.classList.add('full');
      }
      document.querySelectorAll('.links details.tool').forEach(function(det){
        det.addEventListener('toggle', function(){ if (det.open) positionDropdown(det); });
      });
      window.addEventListener('resize', function(){
        document.querySelectorAll('.links details.tool[open]').forEach(positionDropdown);
      });
    })();
  </script>
  <script>
    // Collapsible sections (expanded by default)
    (function(){
      document.querySelectorAll('.pub-sec').forEach(function(sec){
        var btn  = sec.querySelector('h2 .toggle');
        var list = sec.querySelector('.paper-list');
        if (!btn || !list) return;

        // Ensure expanded on load
        sec.classList.remove('collapsed');
        list.hidden = false;
        btn.setAttribute('aria-expanded', 'true');

        btn.addEventListener('click', function(){
          var collapsed = sec.classList.toggle('collapsed');
          list.hidden = collapsed;
          btn.setAttribute('aria-expanded', String(!collapsed));
        });
      });
    })();
  </script>
</body>
</html>
"""

def main():
    if not os.path.exists(CSV_FILE):
        sys.stderr.write("ERROR: publications.csv not found next to build_publications.py\n")
        sys.stderr.write("Create the CSV (see template) and run again.\n")
        sys.exit(1)

    rows = read_rows(CSV_FILE)

    # Bucket by section (preserve CSV order), then reverse within section so last-added shows first
    buckets = {"journal": [], "working": [], "conference": [], "other": []}
    for r in rows:
        buckets[normalize_section(r.get("section",""))].append(article(r))
    for k in buckets:
        buckets[k].reverse()

    # Fill shell
    html_out = (SHELL
                .replace("{{JOURNAL_ITEMS}}", "\n".join(buckets["journal"]) or "\n")
                .replace("{{WORKING_ITEMS}}", "\n".join(buckets["working"]) or "\n")
                .replace("{{CONF_ITEMS}}", "\n".join(buckets["conference"]) or "\n")
                .replace("{{OTHER_ITEMS}}", "\n".join(buckets["other"]) or "\n"))

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"Wrote {OUT_FILE} ({sum(len(v) for v in buckets.values())} items).")

if __name__ == "__main__":
    main()
