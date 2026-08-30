import base64, json, os, re, colorsys

BASE = os.path.dirname(os.path.abspath(__file__))

ORDER = ["tokyo-night","catppuccin","gruvbox","kanagawa","nord","everforest","osaka-jade",
         "rose-pine","ristretto","matte-black","retro-82","hackerman","ethereal","miasma",
         "lumon","last-horizon","solitude","vantablack","lupine","catppuccin-latte",
         "flexoki-light","white"]

LABEL = {"tokyo-night":"Tokyo Night","catppuccin":"Catppuccin","catppuccin-latte":"Catppuccin Latte",
 "gruvbox":"Gruvbox","kanagawa":"Kanagawa","nord":"Nord","everforest":"Everforest",
 "osaka-jade":"Osaka Jade","rose-pine":"Rosé Pine","ristretto":"Ristretto","matte-black":"Matte Black",
 "retro-82":"Retro 82","hackerman":"Hackerman","ethereal":"Ethereal","miasma":"Miasma","lumon":"Lumon",
 "last-horizon":"Last Horizon","solitude":"Solitude","vantablack":"Vantablack","lupine":"Lupine",
 "flexoki-light":"Flexoki Light","white":"White"}

WP_TITLE = {"tokyo-night":"Oma Cityscape","catppuccin":"Waves","catppuccin-latte":"Color Fade",
 "gruvbox":"The Backwater","kanagawa":"The Great Wave","nord":"City View","everforest":"Tree Tops",
 "osaka-jade":"Glowing City","rose-pine":"Funky Shapes","ristretto":"Industrial Moon",
 "matte-black":"Dark Waters","retro-82":"Gateway","hackerman":"Synth Scape","ethereal":"Cosmic",
 "miasma":"Nature of Fear","lumon":"United in Severance","last-horizon":"New Horizons",
 "solitude":"Ether","vantablack":"Twisted Stairs","lupine":"Abstract Wave","flexoki-light":"Orb",
 "white":"White"}

def parse(path):
    d = {}
    for line in open(path):
        m = re.match(r'\s*([a-z_0-9]+)\s*=\s*"([^"]+)"', line)
        if m: d[m.group(1)] = m.group(2)
    return d

def lum(hx):
    r,g,b = [int(hx[i:i+2],16)/255 for i in (1,3,5)]
    f = lambda c: c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)

def sat(hx):
    r,g,b = [int(hx[i:i+2],16)/255 for i in (1,3,5)]
    h,l,s = colorsys.rgb_to_hls(r,g,b)
    return s

def hue(hx):
    r,g,b = [int(hx[i:i+2],16)/255 for i in (1,3,5)]
    h,l,s = colorsys.rgb_to_hls(r,g,b)
    return h*360

out = []
for t in ORDER:
    d = parse(os.path.join(BASE, "assets", "palettes", f"{t}.toml"))
    bg = d["background"]; fg = d["foreground"]; accent = d["accent"]
    if "color1" in d:   # legacy ANSI schema
        pal = {"red":d["color1"],"green":d["color2"],"yellow":d["color3"],
               "blue":d["color4"],"magenta":d["color5"],"cyan":d["color6"]}
        bright = {"red":d.get("color9"),"green":d.get("color10"),"yellow":d.get("color11"),
                  "blue":d.get("color12"),"magenta":d.get("color13"),"cyan":d.get("color14")}
        dim = d.get("color8", d.get("color0"))
    else:
        pal = {k:d.get(k, accent) for k in ("red","green","yellow","blue","magenta","cyan")}
        bright = {k:d.get("bright_"+k, pal[k]) for k in pal}
        dim = d.get("muted", d.get("selection", accent))
    mode = d.get("mode") or ("light" if lum(bg) > 0.4 else "dark")

    # candidate colors for the 3-swatch preview: most distinct hues, decent saturation
    cands = list(dict.fromkeys([accent] + [pal[k] for k in ("blue","magenta","red","yellow","green","cyan")]))
    picked = []
    for c in cands:
        if len(picked) >= 3: break
        if any(abs(((hue(c)-hue(p)+180)%360)-180) < 22 and abs(sat(c)-sat(p)) < .25 for p in picked):
            continue
        picked.append(c)
    while len(picked) < 3: picked.append(fg)

    out.append({
        "id": t, "label": LABEL[t], "mode": mode,
        "bg": bg, "fg": fg, "accent": accent, "dim": dim,
        "wp": WP_TITLE[t],
        "p": pal, "b": bright,
        "swatch": picked,
    })

for o in out:
    p = f"assets/wallpapers/{o['id']}.webp"
    o["img"] = "data:image/webp;base64," + base64.b64encode(open(p,'rb').read()).decode()

open(os.path.join(BASE, "themes.json"), "w").write(json.dumps(out, separators=(",",":")))
print("themes:", len(out), "size:", os.path.getsize(os.path.join(BASE, "themes.json")))
