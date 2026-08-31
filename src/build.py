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
import base64, json, os, re, sys

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
  if(p.get("all"))document.querySelectorAll(".rv,.blk,.rule,.card").forEach(function(n){n.classList.add("in")});
  if(p.get("flat")){var s=document.createElement("style");
    s.textContent="#top{min-height:0!important}";document.head.appendChild(s);}
  if(p.get("theme")&&window.OM)OM.apply(p.get("theme"));
  /* freeze the wordmark sweep at t seconds, for frame-by-frame screenshots.
     forced !important so it also works where prefers-reduced-motion is on. */
  if(p.get("t")!==null){var lg=document.querySelector("#logo i");
    if(lg){var dur=getComputedStyle(lg).getPropertyValue("--sweep").trim()||"90s";
      lg.style.setProperty("animation-duration",dur,"important");
      lg.style.setProperty("animation-delay","-"+p.get("t")+"s","important");
      lg.style.setProperty("animation-play-state","paused","important");}}
});
</script>"""


def wordmark_markup():
    """The wordmark is a CSS gradient masked to the official shape, not an SVG
    with a gradient fill: only the CSS form can be animated and paused for
    prefers-reduced-motion. The glow sits on the wrapper because CSS applies
    filters *before* masks, so a filter on the masked element would be clipped
    away with everything outside the letterforms."""
    return '<span id="logo" role="img" aria-label="Omarchy"><i></i></span>'


def wordmark_url():
    """The official wordmark from omarchy.org/brand/, as a mask image. Only its
    alpha matters, so the source fill colour is irrelevant. base64 rather than
    percent-encoding, to keep quotes and hashes out of the CSS."""
    svg = open(os.path.join(BASE, "assets", "omarchy-wordmark.svg"), "rb").read().strip()
    return 'url("data:image/svg+xml;base64,' + base64.b64encode(svg).decode() + '")'


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
        fragment = fragment.replace("<!--WORDMARK-->", wordmark_markup())
        fragment = fragment.replace("/*WORDMARK-URL*/", wordmark_url())

        open(os.path.join(ART, page), "w").write(fragment)

        head, body = split_head(fragment)
        path, _ = ROUTES[page]
        dest = os.path.join(OUT, path, "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w").write(document(head, body, page, debug))
        print(f"{page:16s} -> /{path or ''}  ({os.path.getsize(dest)/1048576:.2f} MB)")


if __name__ == "__main__":
    main()
