# omarchy_landing

Two alternative designs for a redesigned **omarchy.org** landing page, plus an index
page that links them.

**Live:** https://aloisdeniel.github.io/omarchy_landing/

Both keep the live site's content and running order — news bar, ASCII logo,
"Beautiful, Fun & Opinionated Linux by DHH", the malleable-OS paragraph, the fourteen
links, the five videos, the footer — and differ only in how that page looks and behaves.

## The two directions

| # | Name | Idea | URL |
|---|------|------|-----|
| 01 | **Omarchy TTY** | The page as a terminal session. Blocks type their own command, output decodes out of ASCII noise, links are a coloured tree, picker is an fzf overlay off a tmux status bar. | [`/tty/`](https://aloisdeniel.github.io/omarchy_landing/tty/) |
| 02 | **Omarchy Broadside** | An editorial poster: full-bleed wallpaper at full strength, very large very light type, and a permanent filmstrip of all 22 wallpapers along the bottom. | [`/broadside/`](https://aloisdeniel.github.io/omarchy_landing/broadside/) |

Four other directions were explored and set aside before the first commit — a Hyprland
desktop, a `fastfetch` card, an arcade CRT, and an engineering spec sheet.

## What both share

- **Themes.** All 22 real Omarchy themes. Palettes are parsed from each theme's
  `colors.toml`; wallpapers are the real backgrounds, downscaled and re-encoded.
  Picking a theme repaints the whole page — type, rules, borders, buttons, wallpaper.
  The picker previews each theme as three colours, and lives in page *chrome* — a
  tmux-style status bar in the TTY, a persistent filmstrip rail in the Broadside —
  never as a content section.
- **Buttons.** The flat row of fourteen links becomes four groups — Install, Build,
  Gather, Back it — each owning a different colour from the active theme.
- **Type.** JetBrains Mono only, weights 100–800.
- **Motion.** Scroll-triggered, retro/ASCII/futurist in flavour, and both pages
  honour `prefers-reduced-motion`.

## Build

```
cd src
python3 build_data.py     # palettes + wallpapers -> themes.json (base64 inlined)
python3 build.py          # pages/*.html + core.js -> out/ and artifact/
python3 -m http.server -d out 8000
```

`build.py` emits each page twice:

- `src/out/` — full HTML documents at their final URLs (`/`, `/tty/`, `/broadside/`).
  This is what GitHub Pages serves.
- `src/artifact/` — the same pages as bare fragments, for publishing to claude.ai
  Artifacts, which supply their own `<!doctype>`/`<head>`/`<body>` wrapper.

Pass `--debug` to add query-string helpers to the `out/` build, useful for
screenshotting: `?light=1` stamps the light theme, `?all=1` forces every reveal
animation to its end state, `?flat=1` collapses viewport-height sections.

Pages are self-contained — every wallpaper is embedded as a data URI, so they run with
no network beyond the Google Fonts stylesheet. That puts each page around 1.5 MB.

### Deploy

`.github/workflows/pages.yml` runs the build on every push to `main` and publishes
`src/out` to GitHub Pages. Nothing generated is committed; the repository holds only
sources.

### Layout

```
src/
  core.js              theme engine + content model, shared by both pages
  pages/
    index.html         the directory page
    tty.html           direction 01
    broadside.html     direction 02
  assets/palettes/     colors.toml pulled from omacom/omarchy@quattro
  assets/wallpapers/   one wallpaper per theme, 1440x900 webp
  assets/picks.txt     which upstream wallpaper each theme uses
  build_data.py        palettes + wallpapers -> themes.json
  build.py             inlines themes.json + core.js, emits out/ and artifact/
```

## Sources

Content and links from [omarchy.org](https://omarchy.org). Palettes and wallpapers from
[omacom/omarchy](https://github.com/omacom/omarchy) (`quattro` branch). Omarchy is a
pending trademark; this repository is design exploration, not an official page.
