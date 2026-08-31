# omarchy_landing

A redesigned landing page for **omarchy.org**, built as a terminal session.

**Live:** https://aloisdeniel.github.io/omarchy_landing/

The page keeps the live site's content and running order — news bar, wordmark,
"Beautiful, Fun & Opinionated Linux by DHH", the malleable-OS paragraph, the fourteen
links, the five videos, the footer — and differs only in how it looks and behaves.

## The idea

The whole page reads as one shell session. Each section is a command that types itself
as you scroll, then prints its output; headings resolve out of ASCII noise as they land.
The fourteen links become a colour-coded tree, and the theme picker is an fzf-style
overlay hanging off a tmux-style status bar pinned to the bottom.

Five other directions were explored and set aside — a Hyprland desktop, a `fastfetch`
card, an arcade CRT, an engineering spec sheet, and an editorial broadside.

## Details

- **Themes.** All 22 real Omarchy themes. Palettes are parsed from each theme's
  `colors.toml`; wallpapers are the real backgrounds, downscaled and re-encoded.
  Picking one repaints everything — type, rules, borders, buttons, the wordmark
  gradient and the wallpaper. The picker previews each theme as three colours and
  lives in page *chrome*, never as a content section. Press <kbd>T</kbd> to open it,
  <kbd>[</kbd> and <kbd>]</kbd> to step through.
- **A different theme every load.** The page picks one at random on each visit, so the
  collection is the first thing you see — drawn only from the themes matching your
  system appearance (17 dark, 5 light), so a dark desktop is never flashed a white
  page. `localStorage` holds only the theme you were last shown, and that one is
  excluded from the next draw; within a pool this small a plain random pick repeats
  often enough that a reload changing nothing reads as a bug rather than as chance.
  A theme you choose by hand ignores both rules, holds for that visit, and is not
  restored afterwards.
- **Wordmark.** The official SVG wordmark from [omarchy.org/brand](https://omarchy.org/brand/),
  refilled at build time with a gradient whose stops are the live theme's CSS variables.
  The gradient is `userSpaceOnUse`, so it sweeps once across the whole wordmark rather
  than restarting inside each of its 211 rectangles.
- **Buttons.** The flat row of fourteen links becomes four groups — Install, Build,
  Gather, Back it — each owning a different colour from the active theme.
- **Type.** JetBrains Mono only, weights 100–800.
- **Motion.** Scroll-triggered, and the page honours `prefers-reduced-motion`.
- **Responsive.** The desktop layout is the design; small screens get a single override
  layer at the end of the stylesheet (`≤680px` and `≤430px`) that shrinks the type,
  opens up the vertical rhythm, drops the wordmark to 80/76% width, stacks the two
  actions full-width, and moves each link's tag onto the title row with its description
  beneath. The status bar respects `env(safe-area-inset-*)`, so it clears the iPhone
  home indicator.

## Build

```
cd src
python3 build_data.py     # palettes + wallpapers -> themes.json (base64 inlined)
python3 build.py          # pages/index.html + core.js -> out/ and artifact/
python3 -m http.server -d out 8000
```

`build.py` emits the page twice:

- `src/out/` — a full HTML document, ready to serve. This is what GitHub Pages publishes.
- `src/artifact/` — the same page as a bare fragment, for publishing to claude.ai
  Artifacts, which supply their own `<!doctype>`/`<head>`/`<body>` wrapper.

Pass `--debug` to add query-string helpers to the `out/` build, useful for
screenshotting: `?theme=gruvbox` applies a theme on load, `?all=1` forces every reveal
animation to its end state, `?flat=1` collapses the viewport-height hero.

The page is self-contained — every wallpaper is embedded as a data URI, so it runs with
no network beyond the Google Fonts stylesheet. That puts it around 1.5 MB.

### Deploy

`.github/workflows/pages.yml` runs the build on every push to `main` and publishes
`src/out` to GitHub Pages. Nothing generated is committed; the repository holds only
sources.

### Layout

```
src/
  core.js                       theme engine + content model
  pages/index.html              the page itself
  assets/omarchy-wordmark.svg   official wordmark, from omarchy.org/brand
  assets/palettes/              colors.toml pulled from omacom/omarchy@quattro
  assets/wallpapers/            one wallpaper per theme, 1440x900 webp
  assets/picks.txt              which upstream wallpaper each theme uses
  build_data.py                 palettes + wallpapers -> themes.json
  build.py                      inlines themes.json, core.js and the wordmark
```

## Sources

Content, links and wordmark from [omarchy.org](https://omarchy.org). Palettes and
wallpapers from [omacom/omarchy](https://github.com/omacom/omarchy) (`quattro` branch).
Omarchy is a pending trademark; this repository is design exploration, not an official
page.
