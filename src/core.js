/* ---- Omarchy shared core: theme engine + content model ---- */
window.OM = (function () {
  var THEMES = __THEMES__;
  var KEY = "omarchy.theme.v1";

  function lum(h) {
    var r = parseInt(h.slice(1, 3), 16) / 255,
        g = parseInt(h.slice(3, 5), 16) / 255,
        b = parseInt(h.slice(5, 7), 16) / 255;
    function f(c) { return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  }
  function contrast(a, b) {
    var l1 = lum(a), l2 = lum(b);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  }
  /* readable ink for a filled swatch */
  function ink(c) { return lum(c) > 0.42 ? "#0a0a0a" : "#fbfbfb"; }
  /* nudge a hue until it clears the ground it sits on */
  function readable(c, ground) {
    if (contrast(c, ground) >= 3.4) return c;
    var up = lum(ground) < 0.42;
    var r = parseInt(c.slice(1, 3), 16), g = parseInt(c.slice(3, 5), 16), b = parseInt(c.slice(5, 7), 16);
    for (var i = 0; i < 14; i++) {
      r = up ? Math.min(255, r + 14) : Math.max(0, r - 14);
      g = up ? Math.min(255, g + 14) : Math.max(0, g - 14);
      b = up ? Math.min(255, b + 14) : Math.max(0, b - 14);
      var hx = "#" + [r, g, b].map(function (v) { return ("0" + v.toString(16)).slice(-2); }).join("");
      if (contrast(hx, ground) >= 3.4) return hx;
    }
    return up ? "#f2f2f2" : "#111111";
  }

  var byId = {};
  THEMES.forEach(function (t) { byId[t.id] = t; });

  var current = null;
  var listeners = [];

  function apply(id) {
    var t = byId[id] || THEMES[0];
    current = t;
    var s = document.documentElement.style;
    s.setProperty("--bg", t.bg);
    s.setProperty("--fg", t.fg);
    s.setProperty("--accent", t.accent);
    s.setProperty("--accent-ink", ink(t.accent));
    s.setProperty("--dim", t.dim);
    s.setProperty("--wallpaper", "url('" + t.img + "')");
    ["red", "green", "yellow", "blue", "magenta", "cyan"].forEach(function (k) {
      s.setProperty("--" + k, t.p[k]);
      s.setProperty("--" + k + "-lit", readable(t.b[k] || t.p[k], t.bg));
      s.setProperty("--" + k + "-ink", ink(t.p[k]));
    });
    t.swatch.forEach(function (c, i) { s.setProperty("--sw" + (i + 1), c); });
    document.documentElement.setAttribute("data-mode", t.mode);
    document.documentElement.setAttribute("data-omtheme", t.id);
    try { localStorage.setItem(KEY, t.id); } catch (e) {}
    listeners.forEach(function (fn) { fn(t); });
    return t;
  }

  function onChange(fn) { listeners.push(fn); if (current) fn(current); }

  function boot(fallbackDark, fallbackLight) {
    var id = null;
    try { id = localStorage.getItem(KEY); } catch (e) {}
    if (!id || !byId[id]) {
      var root = document.documentElement.getAttribute("data-theme");
      var light = root === "light" ||
        (!root && window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches);
      id = light ? (fallbackLight || "rose-pine") : (fallbackDark || "tokyo-night");
    }
    return apply(id);
  }

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* reveal-on-scroll: adds .in when the element crosses into view */
  function reveal(nodes, opts) {
    opts = opts || {};
    nodes = Array.prototype.slice.call(nodes);
    if (reduced) { nodes.forEach(function (n) { n.classList.add("in"); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var n = e.target;
        var d = parseFloat(n.dataset.delay || 0);
        setTimeout(function () {
          n.classList.add("in");
          if (opts.each) opts.each(n);
        }, d);
        io.unobserve(n);
      });
    }, { rootMargin: opts.rootMargin || "0px 0px -12% 0px", threshold: opts.threshold || 0.12 });
    nodes.forEach(function (n) { io.observe(n); });
  }

  /* ASCII decode: text resolves out of noise, left to right */
  var GLYPHS = "!<>-_\\/[]{}—=+*^?#01ABCDEFXYZ%$&@~";
  function scramble(el, text, opts) {
    opts = opts || {};
    text = text == null ? (el.dataset.text || el.textContent) : text;
    el.dataset.text = text;
    if (reduced) { el.textContent = text; return; }
    var speed = opts.speed || 1.6;      // chars resolved per frame
    var spread = opts.spread || 14;     // noise tail length
    var pos = 0, raf;
    function frame() {
      var out = "";
      for (var i = 0; i < text.length; i++) {
        var ch = text[i];
        if (i < pos) out += ch;
        else if (ch === " " || ch === "\n") out += ch;
        else if (i < pos + spread) out += GLYPHS[(Math.random() * GLYPHS.length) | 0];
        else out += " ";
      }
      el.textContent = out;
      pos += speed;
      if (pos < text.length + spread) raf = requestAnimationFrame(frame);
      else el.textContent = text;
    }
    cancelAnimationFrame(raf);
    frame();
  }

  /* typewriter, resolves a promise when done */
  function type(el, text, ms) {
    return new Promise(function (res) {
      if (reduced) { el.textContent = text; res(); return; }
      var i = 0;
      (function step() {
        el.textContent = text.slice(0, ++i);
        if (i < text.length) setTimeout(step, ms || 18); else res();
      })();
    });
  }

  var ISO = "https://iso.omarchy.org/omarchy-4.0.1.iso";

  /* the 14 destinations, grouped by what you actually came to do.
     each group owns one theme colour. */
  var GROUPS = [
    { key: "install", title: "Install", hue: "green",
      note: "Get Omarchy running on your machine.",
      links: [
        { label: "ISO", href: ISO, meta: "4.0.1", desc: "Bootable image, ~3 GB" },
        { label: "Manual", href: "https://omarchy.org/manual/", meta: "docs", desc: "Install, configure, live in it" },
        { label: "Plugins", href: "https://omarchyplugins.com/", meta: "registry", desc: "Extend the default setup" }
      ] },
    { key: "build", title: "Build", hue: "blue",
      note: "The source, the hardware, the guarantees.",
      links: [
        { label: "GitHub", href: "https://github.com/omacom/omarchy", meta: "source", desc: "Read it, fork it, send a patch" },
        { label: "Security", href: "https://omarchy.org/security/", meta: "policy", desc: "How issues are handled" },
        { label: "AIR", href: "https://omarchy.org/air/", meta: "spec", desc: "Agent Interface Requirements" },
        { label: "Workstations", href: "https://omarchy.org/workstations/", meta: "hardware", desc: "Machines it runs best on" }
      ] },
    { key: "gather", title: "Gather", hue: "magenta",
      note: "Where the Omarchs actually hang out.",
      links: [
        { label: "Discord", href: "https://discord.gg/tXFUdasqhY", meta: "chat", desc: "Help, showcases, arguments" },
        { label: "Meetups", href: "https://omarchy.org/meetups/", meta: "irl", desc: "Find one near you" },
        { label: "Teams", href: "https://omarchy.org/teams/", meta: "people", desc: "Who builds this" },
        { label: "News", href: "https://omarchy.org/news/", meta: "blog", desc: "Releases and announcements" }
      ] },
    { key: "back", title: "Back it", hue: "yellow",
      note: "Keep it free, opinionated and unbought.",
      links: [
        { label: "Patrons", href: "https://omarchy.org/patrons/", meta: "support", desc: "Fund the work directly" },
        { label: "Sponsorships", href: "https://omarchy.org/sponsorships/", meta: "corporate", desc: "For companies shipping on it" },
        { label: "Merch", href: "https://supply.37signals.com/collections/omarchy", meta: "store", desc: "Wear the trademark" }
      ] }
  ];

  var VIDEOS = [
    { id: "F7fe9pa8OeE", title: "Omarchy Quattro", by: "David Heinemeier Hansson" },
    { id: "KO2T0oET9go", title: "If you use AI, switch to Omarchy immediately", by: "Alex Finn" },
    { id: "9SDkU5VDQEQ", title: "You need to switch to Linux RIGHT NOW!!", by: "NetworkChuck" },
    { id: "5JPYJfN7HY0", title: "They finally fixed linux", by: "typecraft" },
    { id: "qBKMe8AatY0", title: "I Didn't Expect Omarchy 4 to Be This Good", by: "LinuxBTW" }
  ];

  var NEWS = {
    label: "Omacom Foundation launches with $10 million",
    href: "https://omarchy.org/news/2026/08/omacom-foundation-launches-with-8-million"
  };

  var COPY = {
    tagline: "Beautiful, Fun & Opinionated Linux by",
    taglineName: "DHH",
    taglineHref: "https://dhh.dk",
    lead: "The malleable OS for the age of agents. Where you can vibe your way through every alteration, tweak, and desire.",
    leadCta: "Be the Omarch",
    leadCtaHref: "https://omarchs.fyi",
    leadTail: " and command your agent!"
  };

  return {
    themes: THEMES, byId: byId, apply: apply, boot: boot, onChange: onChange,
    get current() { return current; },
    reduced: reduced, reveal: reveal, scramble: scramble, type: type,
    lum: lum, ink: ink, readable: readable, contrast: contrast,
    GROUPS: GROUPS, VIDEOS: VIDEOS, NEWS: NEWS, COPY: COPY, ISO: ISO
  };
})();
