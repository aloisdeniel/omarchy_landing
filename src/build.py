#!/usr/bin/env python3
"""Build the static site.

pages/*.html are fragments: <title>, font <link>s, <style>, then markup, then a
<script>, with a <!--CORE--> marker where the shared theme engine belongs and a
<!--WORDMARK--> marker where the official Omarchy wordmark belongs.

Emits two forms of each page:
  out/       full HTML documents, ready to serve (GitHub Pages)
  artifact/  the fragments with core.js inlined, for claude.ai Artifacts,
             which supply their own <!doctype>/<head>/<body> wrapper
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(BASE, "pages")
OUT = os.path.join(BASE, "out")
ART = os.path.join(BASE, "artifact")

SITE = "https://aloisdeniel.github.io/omarchy_landing"

# page -> (url path, meta description)
ROUTES = {
    "index.html": ("", "Omarchy's landing page as a terminal session: commands type themselves, output decodes out of ASCII noise, and an fzf overlay repaints the page in any of 22 themes."),
}

DEBUG_HELPER = """<script>
/* local screenshot helpers; inert without a query string */
addEventListener("load",function(){
  var p=new URLSearchParams(location.search);
  if(p.get("light"))document.documentElement.setAttribute("data-theme","light");
  if(p.get("all"))document.querySelectorAll(".rv,.blk,.rule,.card").forEach(function(n){n.classList.add("in")});
  if(p.get("flat")){var s=document.createElement("style");
    s.textContent="#top{min-height:0!important}";document.head.appendChild(s);}
  if(p.get("theme")&&window.OM)OM.apply(p.get("theme"));
});
</script>"""


def wordmark():
    """The official wordmark from omarchy.org/brand/, refilled with a gradient
    built from the live theme's CSS variables so it repaints with everything else."""
    svg = open(os.path.join(BASE, "assets", "omarchy-wordmark.svg")).read().strip()
    # userSpaceOnUse, not the default objectBoundingBox: the fill lives on the <g>,
    # so a bounding-box gradient would restart inside every one of the 211 rects.
    # These coordinates are the wordmark's own viewBox (4131x950).
    grad = (
        '<defs><linearGradient id="omgrad" gradientUnits="userSpaceOnUse"'
        ' x1="0" y1="0" x2="4131" y2="333">'
        '<stop offset="0" stop-color="var(--accent)"/>'
        '<stop offset="0.34" stop-color="var(--magenta)"/>'
        '<stop offset="0.62" stop-color="var(--cyan)"/>'
        '<stop offset="1" stop-color="var(--green)"/>'
        "</linearGradient></defs>"
    )
    svg = svg.replace('<g fill="#9ece6a"', '<g fill="url(#omgrad)"', 1)
    svg = svg.replace(
        '<svg ', '<svg id="logo" role="img" aria-label="Omarchy" ', 1
    ).replace(
        ' width="4131" height="950"', "", 1
    )
    # inject the gradient definition immediately after the opening <svg ...>
    i = svg.index(">") + 1
    return svg[:i] + grad + svg[i:]


def split_head(fragment):
    """Head material is everything up to and including the first </style>."""
    i = fragment.index("</style>") + len("</style>")
    return fragment[:i], fragment[i:]


def document(head, body, page, debug):
    path, desc = ROUTES[page]
    title = re.search(r"<title>(.*?)</title>", head).group(1)
    url = SITE + "/" + path
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="dark light">
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='26' font-size='26'>&#128421;</text></svg>">
{head}
</head>
<body>
{body}
{DEBUG_HELPER if debug else ""}
</body>
</html>
"""


def main():
    debug = "--debug" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(ROUTES)

    themes = open(os.path.join(BASE, "themes.json")).read()
    core = open(os.path.join(BASE, "core.js")).read().replace("__THEMES__", themes)

    os.makedirs(OUT, exist_ok=True)
    os.makedirs(ART, exist_ok=True)
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    for page in names:
        src = open(os.path.join(PAGES, page)).read()
        fragment = src.replace("<!--CORE-->", "<script>\n" + core + "\n</script>")
        fragment = fragment.replace("<!--WORDMARK-->", wordmark())

        open(os.path.join(ART, page), "w").write(fragment)

        head, body = split_head(fragment)
        path, _ = ROUTES[page]
        dest = os.path.join(OUT, path, "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w").write(document(head, body, page, debug))
        print(f"{page:16s} -> /{path or ''}  ({os.path.getsize(dest)/1048576:.2f} MB)")


if __name__ == "__main__":
    main()
