#!/usr/bin/env python3
"""Genera los SVG animados del perfil a partir de scripts/data.json.

Todo lo que se dibuja aqui sale de datos reales de la API de GitHub.
Las animaciones son CSS puro: GitHub sirve el SVG como <img>, asi que
SMIL/CSS corren pero JavaScript no.
"""
import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

C = {
    "bg": "#070a0e",
    "panel": "#0b1017",
    "panel2": "#0d141c",
    "line": "#17222e",
    "dim": "#4a5c6e",
    "text": "#b9c7d4",
    "bright": "#e6eef5",
    "cyan": "#22d3ee",
    "cyan_d": "#0e3a44",
    "amber": "#f0a63a",
}
LEVELS = ["#0d141c", "#0e3a44", "#12707f", "#1aa6bd", "#22d3ee"]
MONO = "ui-monospace,'SFMono-Regular','SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"

RM = ("@media (prefers-reduced-motion:reduce){*{animation:none!important;"
      "opacity:1!important;transform:none!important}}")
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(n):
    return f"{n:,}".replace(",", ".")


def reveal(name, t_in, total, dy=5, dur=0.5, fade_at=None):
    """Keyframes de entrada sincronizados a un ciclo global de `total` segundos."""
    a = t_in / total * 100
    b = min((t_in + dur) / total * 100, 99)
    c = ((fade_at if fade_at is not None else total - 0.7) / total) * 100
    return (f"@keyframes {name}{{0%,{a:.2f}%{{opacity:0;transform:translateY({dy}px)}}"
            f"{b:.2f}%,{c:.2f}%{{opacity:1;transform:translateY(0)}}"
            f"100%{{opacity:0;transform:translateY(0)}}}}")


def grow(name, t_in, total, dur=0.9, fade_at=None):
    """Keyframes de crecimiento horizontal (barras, typing, reglas)."""
    a = t_in / total * 100
    b = min((t_in + dur) / total * 100, 99)
    c = ((fade_at if fade_at is not None else total - 0.7) / total) * 100
    return (f"@keyframes {name}{{0%,{a:.2f}%{{transform:scaleX(0)}}"
            f"{b:.2f}%,{c:.2f}%{{transform:scaleX(1)}}"
            f"100%{{transform:scaleX(1);opacity:0}}}}")


def chrome(w, h, title, tab=None):
    """Marco de terminal: barra de titulo, semaforo y reticula de fondo."""
    return f"""<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="11" fill="{C['panel']}" stroke="{C['line']}"/>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="11" fill="url(#dots)"/>
<path d="M0 34h{w}" stroke="{C['line']}"/>
<circle cx="21" cy="17.5" r="4.5" fill="{C['cyan']}" opacity=".75"/>
<circle cx="37" cy="17.5" r="4.5" fill="{C['line']}"/>
<circle cx="53" cy="17.5" r="4.5" fill="{C['line']}"/>
<text x="{w/2}" y="21.5" text-anchor="middle" font-size="11.5" fill="{C['dim']}" letter-spacing=".6">{esc(title)}</text>
{f'<text x="{w-24}" y="21.5" text-anchor="end" font-size="11" fill="{C["line"]}">{esc(tab)}</text>' if tab else ''}"""


def defs_common():
    return f"""<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
  <circle cx="1" cy="1" r="1" fill="{C['line']}" opacity=".55"/>
</pattern>
<linearGradient id="fade" x1="0" x2="1">
  <stop offset="0" stop-color="{C['cyan']}" stop-opacity="0"/>
  <stop offset=".5" stop-color="{C['cyan']}" stop-opacity=".16"/>
  <stop offset="1" stop-color="{C['cyan']}" stop-opacity="0"/>
</linearGradient>"""


# ---------------------------------------------------------------- header
def header_svg(d):
    W, H, T = 880, 312, 15.0
    total = fmt(d["total_commits"])
    lines = [
        ("Started", "IT System Solutions Panama - Full-Stack Developer, remoto"),
        ("Mounted", f"{d['repo_count']} repositorios - {total} commits en los ultimos 12 meses"),
        ("Reached target", "Barranquilla, Colombia - presencial / hibrido / remoto"),
        ("Listening on", "portafolio-joel-dev.vercel.app"),
    ]
    css = [RM,
           "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}",
           "@keyframes scan{0%{transform:translateY(-40px)}100%{transform:translateY(320px)}}",
           "@keyframes glow{0%,100%{opacity:.20}50%{opacity:.42}}",
           grow("tp", 0.4, T, 1.5), reveal("nm", 2.1, T, 8, 0.6),
           grow("ul", 2.5, T, 0.8), reveal("sb", 2.9, T, 4, 0.5),
           grow("sep", 3.3, T, 0.9), reveal("pr", 6.6, T, 3, 0.4)]
    for i in range(len(lines)):
        css.append(reveal(f"ok{i}", 4.0 + i * 0.55, T, 4, 0.42))

    body = []
    # linea de comando con efecto de tecleo
    cmd = "ssh joel@saimper.dev -p 22"
    body.append(f"""<g clip-path="url(#typeclip)">
  <text x="28" y="64" font-size="13.5" fill="{C['text']}"><tspan fill="{C['cyan']}">$</tspan> {esc(cmd)}</text>
</g>""")

    # nombre + regla de acento
    body.append(f"""<text x="28" y="120" font-size="44" font-weight="700" fill="{C['bright']}" letter-spacing="7" style="animation:nm {T}s infinite">JOEL SOLANO</text>
<rect x="28" y="132" width="367" height="3" fill="{C['cyan']}" style="animation:ul {T}s infinite;transform-box:fill-box;transform-origin:left"/>
<text x="28" y="158" font-size="13" letter-spacing=".4" style="animation:sb {T}s infinite"><tspan fill="{C['cyan']}">Full-Stack Developer</tspan><tspan fill="{C['dim']}">  ::  Laravel / PHP / MySQL / Astro / Node</tspan></text>
<rect x="28" y="176" width="824" height="1" fill="{C['line']}" style="animation:sep {T}s infinite;transform-box:fill-box;transform-origin:left"/>""")

    y = 204
    for i, (verb, txt) in enumerate(lines):
        body.append(f"""<text x="28" y="{y}" font-size="12.5" style="animation:ok{i} {T}s infinite"><tspan fill="{C['dim']}">[</tspan><tspan fill="{C['cyan']}">  OK  </tspan><tspan fill="{C['dim']}">]</tspan><tspan fill="{C['text']}" dx="8">{esc(verb)}</tspan><tspan fill="{C['dim']}" dx="6">{esc(txt)}</tspan></text>""")
        y += 22

    body.append(f"""<g style="animation:pr {T}s infinite">
  <text x="28" y="292" font-size="13" fill="{C['dim']}">joel@dev<tspan fill="{C['line']}">:</tspan>~<tspan fill="{C['cyan']}">$</tspan></text>
  <rect x="122" y="281" width="8" height="14" fill="{C['cyan']}" style="animation:blink 1.05s steps(1) infinite"/>
</g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{MONO}" role="img" aria-label="Joel Solano - Full-Stack Developer">
<defs>
{defs_common()}
<clipPath id="typeclip"><rect x="28" y="50" width="330" height="20" style="animation:tp {T}s infinite;transform-box:fill-box;transform-origin:left"/></clipPath>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="11"/></clipPath>
<linearGradient id="scanl" x1="0" x2="0" y1="0" y2="1">
  <stop offset="0" stop-color="{C['cyan']}" stop-opacity="0"/>
  <stop offset=".5" stop-color="{C['cyan']}" stop-opacity=".05"/>
  <stop offset="1" stop-color="{C['cyan']}" stop-opacity="0"/>
</linearGradient>
<radialGradient id="halo" cx=".2" cy=".35">
  <stop offset="0" stop-color="{C['cyan']}" stop-opacity=".13"/>
  <stop offset="1" stop-color="{C['cyan']}" stop-opacity="0"/>
</radialGradient>
<style>{''.join(css)}</style>
</defs>
<rect width="{W}" height="{H}" rx="11" fill="{C['bg']}"/>
{chrome(W, H, "joel@barranquilla: ~/dev", "ssh")}
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#halo)" style="animation:glow 5s ease-in-out infinite"/>
  {''.join(body)}
  <rect y="34" width="{W}" height="40" fill="url(#scanl)" style="animation:scan 7s linear infinite"/>
</g>
</svg>"""


# ----------------------------------------------------------------- stack
TOOLS = ["Laravel", "PHP 8", "MySQL", "Pest", "PHPStan", "Pint", "Tailwind",
         "Astro", "Node.js", "Vue", "TypeScript", "nginx", "Supervisor",
         "n8n", "Git"]


def stack_svg(d):
    W, H, T = 880, 322, 13.0
    langs = list(d["languages"].items())[:7]
    tot = sum(d["languages"].values())
    css = [RM, "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}",
           reveal("hd", 0.3, T, 4, 0.4), reveal("hd2", 0.5, T, 4, 0.4)]
    body = []

    body.append(f"""<text x="28" y="62" font-size="12.5" style="animation:hd {T}s infinite"><tspan fill="{C['cyan']}">$</tspan><tspan fill="{C['text']}" dx="7">cloc --by-lang</tspan><tspan fill="{C['dim']}" dx="7">{d['repo_count']} repos</tspan></text>
<text x="470" y="62" font-size="12.5" style="animation:hd2 {T}s infinite"><tspan fill="{C['cyan']}">$</tspan><tspan fill="{C['text']}" dx="7">stack --active</tspan></text>
<path d="M28 74h388M470 74h382" stroke="{C['line']}"/>""")

    # columna izquierda: bytes reales por lenguaje
    y = 98
    for i, (name, size) in enumerate(langs):
        pct = size / tot * 100
        w = max(2.0, pct / 100 * 232)
        css.append(grow(f"b{i}", 0.9 + i * 0.16, T, 1.0))
        css.append(reveal(f"bt{i}", 0.9 + i * 0.16, T, 2, 0.4))
        body.append(f"""<g style="animation:bt{i} {T}s infinite">
  <text x="28" y="{y+4}" font-size="12" fill="{C['text']}">{esc(name)}</text>
  <rect x="118" y="{y-8}" width="232" height="11" rx="2.5" fill="{C['panel2']}"/>
  <rect x="118" y="{y-8}" width="{w:.1f}" height="11" rx="2.5" fill="{C['cyan'] if i == 0 else LEVELS[3] if i < 3 else LEVELS[2]}" style="animation:b{i} {T}s infinite;transform-box:fill-box;transform-origin:left"/>
  <text x="416" y="{y+4}" text-anchor="end" font-size="11.5" fill="{C['dim']}">{pct:5.1f}%</text>
</g>""")
        y += 27

    # columna derecha: herramientas del dia a dia
    cx, cy = 470, 88
    for i, tool in enumerate(TOOLS):
        col, row = i % 3, i // 3
        x = cx + col * 128
        yy = cy + row * 38
        css.append(reveal(f"t{i}", 1.4 + i * 0.09, T, 5, 0.38))
        body.append(f"""<g style="animation:t{i} {T}s infinite">
  <rect x="{x}" y="{yy}" width="118" height="28" rx="4" fill="{C['panel2']}" stroke="{C['line']}"/>
  <rect x="{x}" y="{yy}" width="2.5" height="28" rx="1.2" fill="{C['cyan']}" opacity=".85"/>
  <text x="{x+14}" y="{yy+18}" font-size="11.5" fill="{C['text']}">{esc(tool)}</text>
</g>""")

    css.append(reveal("ft", 3.2, T, 3, 0.4))
    body.append(f"""<g style="animation:ft {T}s infinite">
  <path d="M28 288h824" stroke="{C['line']}"/>
  <text x="28" y="307" font-size="11.5"><tspan fill="{C['dim']}">Infraestructura propia:</tspan><tspan fill="{C['text']}" dx="6">VPS autoadministrado, nginx + PHP-FPM, colas con Supervisor, despliegue manual</tspan></text>
</g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{MONO}" role="img" aria-label="Stack tecnico">
<defs>{defs_common()}<style>{''.join(css)}</style></defs>
<rect width="{W}" height="{H}" rx="11" fill="{C['bg']}"/>
{chrome(W, H, "stack -- distribucion real de codigo", "tokei")}
{''.join(body)}
</svg>"""


# --------------------------------------------------------------- heatmap
def heatmap_svg(d):
    by_day = {k: v for k, v in d["by_day"].items()}
    today = datetime.date.today()
    start = today - datetime.timedelta(days=364)
    start -= datetime.timedelta(days=(start.weekday() + 1) % 7)  # alinear a domingo

    counts = sorted(v for v in by_day.values() if v > 0)
    if counts:
        q = [counts[int(len(counts) * f)] for f in (0.25, 0.5, 0.8)]
    else:
        q = [1, 2, 3]

    def level(n):
        if n <= 0:
            return 0
        if n <= q[0]:
            return 1
        if n <= q[1]:
            return 2
        if n <= q[2]:
            return 3
        return 4

    weeks = []
    cur = start
    while cur <= today:
        col = []
        for _ in range(7):
            col.append((cur, by_day.get(cur.isoformat(), 0)) if cur <= today else None)
            cur += datetime.timedelta(days=1)
        weeks.append(col)
    nw = len(weeks)

    # racha mas larga de dias consecutivos con actividad
    streak = best = 0
    day = start
    while day <= today:
        streak = streak + 1 if by_day.get(day.isoformat(), 0) else 0
        best = max(best, streak)
        day += datetime.timedelta(days=1)

    CELL, STEP = 12.0, 14.8
    X0, Y0 = 66, 106
    W, H, T = 880, 296, 14.0
    css = [RM, "@keyframes sweep{0%,32%{transform:translateX(-160px);opacity:0}"
                "36%{opacity:1}62%{opacity:1}66%,100%{transform:translateX(880px);opacity:0}}",
           "@keyframes pulse{0%,100%{opacity:.55}50%{opacity:1}}",
           reveal("hd", 0.25, T, 4, 0.4), reveal("ft", 4.6, T, 4, 0.5)]
    css.append("rect[class^=k]{transform-box:fill-box;transform-origin:center}")
    for w in range(nw):
        css.append(f"@keyframes k{w}{{0%,{(0.5+w*0.055)/T*100:.2f}%{{opacity:0;transform:scale(.35)}}"
                   f"{(0.9+w*0.055)/T*100:.2f}%,{(T-0.7)/T*100:.2f}%{{opacity:1;transform:scale(1)}}"
                   f"100%{{opacity:0;transform:scale(.35)}}}}"
                   f".k{w}{{animation:k{w} {T}s infinite}}")

    body, months = [], []
    last_m = None
    for wi, col in enumerate(weeks):
        x = X0 + wi * STEP
        for di, cell in enumerate(col):
            if cell is None:
                continue
            date, n = cell
            if di == 0:
                if date.month != last_m:
                    last_m = date.month
                    months.append((x, MESES[date.month - 1]))
            lv = level(n)
            extra = f' opacity=".9"' if lv == 4 else ""
            # sin <title>: GitHub sirve el SVG como <img> y los tooltips no llegan al usuario
            body.append(f'<rect x="{x:.1f}" y="{Y0+di*STEP:.1f}" width="{CELL}" height="{CELL}" rx="2.4" '
                        f'fill="{LEVELS[lv]}"{extra} class="k{wi}"/>')

    mtxt = "".join(f'<text x="{x:.1f}" y="96" font-size="10.5" fill="{C["dim"]}">{m}</text>' for x, m in months)
    dtxt = "".join(f'<text x="58" y="{Y0+i*STEP+9:.1f}" text-anchor="end" font-size="10" fill="{C["dim"]}">{lb}</text>'
                   for i, lb in ((1, "Lun"), (3, "Mie"), (5, "Vie")))

    legend_x = 640
    legend = "".join(f'<rect x="{legend_x+38+i*16}" y="266" width="11" height="11" rx="2.4" fill="{c}"/>'
                     for i, c in enumerate(LEVELS))

    stats = [(fmt(d["total_commits"]), "commits"), (str(d["active_days"]), "dias activos"),
             (str(best), "dias seguidos"), (str(d["repo_count"]), "repositorios")]
    sx = 28
    stat_svg = []
    for val, lab in stats:
        stat_svg.append(f'<text x="{sx}" y="277" font-size="16" font-weight="700" fill="{C["cyan"]}">{val}'
                        f'<tspan font-size="11" font-weight="400" fill="{C["dim"]}" dx="7">{lab}</tspan></text>')
        sx += 150
    grid_w = nw * STEP

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{MONO}" role="img" aria-label="Actividad de commits del ultimo ano">
<defs>{defs_common()}
<clipPath id="gclip"><rect x="{X0}" y="{Y0-4}" width="{grid_w:.0f}" height="{7*STEP:.0f}"/></clipPath>
<style>{''.join(css)}</style></defs>
<rect width="{W}" height="{H}" rx="11" fill="{C['bg']}"/>
{chrome(W, H, "git log --author=Saimper --since=1.year --all", "activity")}
<g style="animation:hd {T}s infinite">
  <text x="28" y="62" font-size="12.5"><tspan fill="{C['cyan']}">$</tspan><tspan fill="{C['text']}" dx="7">contribuciones reales</tspan><tspan fill="{C['dim']}" dx="8">repos publicos y privados, ultimos 12 meses</tspan></text>
  <path d="M28 74h824" stroke="{C['line']}"/>
</g>
{mtxt}{dtxt}
<g>{''.join(body)}</g>
<g clip-path="url(#gclip)"><rect x="0" y="{Y0-4}" width="150" height="{7*STEP:.0f}" fill="url(#fade)" style="animation:sweep {T}s linear infinite"/></g>
<g style="animation:ft {T}s infinite">
  <path d="M28 250h824" stroke="{C['line']}"/>
  {''.join(stat_svg)}
  <text x="{legend_x}" y="275" font-size="10.5" fill="{C['dim']}">menos</text>
  {legend}
  <text x="{legend_x+128}" y="275" font-size="10.5" fill="{C['dim']}">mas</text>
</g>
</svg>"""


# -------------------------------------------------------------- timeline
ROLES = [
    ("CUN", "Ingenieria de Sistemas", (2021, 8), None, False),
    ("ParqueSoft", "Software QA Tester", (2023, 4), (2023, 6), False),
    ("Freelance", "Desarrollador web", (2024, 1), None, True),
    ("Comaderas", "Auxiliar de TI", (2024, 9), (2025, 3), False),
    ("IT System Solutions", "Full-Stack Developer", (2026, 2), None, True),
]


def timeline_svg():
    W, H, T = 880, 366, 13.0
    x0, x1 = 210, 852
    t_start, t_end = 2021 + 6 / 12, 2026 + 9 / 12

    def px(ym):
        t = ym[0] + (ym[1] - 1) / 12
        return x0 + (t - t_start) / (t_end - t_start) * (x1 - x0)

    css = [RM, "@keyframes pulse{0%,100%{opacity:.35;r:4}50%{opacity:1;r:6.5}}",
           reveal("hd", 0.3, T, 4, 0.4), grow("ax", 0.6, T, 1.0)]
    AXIS = 310
    body, ticks = [], []
    for yr in range(2021, 2027):
        x = px((yr, 1))
        if x < x0 - 4:
            continue
        ticks.append(f'<path d="M{x:.1f} {AXIS+1}v7" stroke="{C["line"]}"/>'
                     f'<text x="{x:.1f}" y="{AXIS+23}" text-anchor="middle" font-size="11" fill="{C["dim"]}">{yr}</text>')

    y = 106
    for i, (org, role, s, e, current) in enumerate(ROLES):
        xs = px(s)
        xe = px((datetime.date.today().year, datetime.date.today().month)) if e is None else px(e)
        w = max(xe - xs, 12)
        css.append(reveal(f"l{i}", 1.0 + i * 0.28, T, 4, 0.4))
        css.append(grow(f"g{i}", 1.15 + i * 0.28, T, 0.85))
        fill = C["cyan"] if current else LEVELS[2]
        end_lab = "actual" if e is None else f"{e[1]:02d}/{e[0]}"
        body.append(f"""<g style="animation:l{i} {T}s infinite">
  <text x="28" y="{y+4}" font-size="12.5" fill="{C['bright']}">{esc(org)}</text>
  <text x="28" y="{y+20}" font-size="10.5" fill="{C['dim']}">{esc(role)}</text>
  <rect x="{xs:.1f}" y="{y-8}" width="{w:.1f}" height="14" rx="3" fill="{fill}" opacity="{.95 if current else .8}" style="animation:g{i} {T}s infinite;transform-box:fill-box;transform-origin:left"/>
  <text x="{xs:.1f}" y="{y+24}" font-size="10" fill="{C['dim']}">{s[1]:02d}/{s[0]} - {end_lab}</text>
  {f'<circle cx="{xs+w:.1f}" cy="{y-1}" r="4" fill="{C["cyan"]}" style="animation:pulse 2.2s ease-in-out infinite"/>' if current else ''}
</g>""")
        y += 42

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{MONO}" role="img" aria-label="Trayectoria profesional">
<defs>{defs_common()}<style>{''.join(css)}</style></defs>
<rect width="{W}" height="{H}" rx="11" fill="{C['bg']}"/>
{chrome(W, H, "journalctl --unit=carrera --since=2021", "timeline")}
<g style="animation:hd {T}s infinite">
  <text x="28" y="62" font-size="12.5"><tspan fill="{C['cyan']}">$</tspan><tspan fill="{C['text']}" dx="7">trayectoria</tspan><tspan fill="{C['dim']}" dx="8">roles solapados, duracion real</tspan></text>
  <path d="M28 74h824" stroke="{C['line']}"/>
</g>
{''.join(body)}
<rect x="{x0}" y="{AXIS}" width="{x1-x0}" height="1" fill="{C['line']}" style="animation:ax {T}s infinite;transform-box:fill-box;transform-origin:left"/>
{''.join(ticks)}
<text x="28" y="{AXIS+23}" font-size="11"><tspan fill="{C['dim']}">Ahora:</tspan><tspan fill="{C['text']}" dx="6">ITSS Panama</tspan><tspan fill="{C['dim']}" dx="6">+ freelance</tspan></text>
</svg>"""


# -------------------------------------------------------------- proyectos
# Descripciones tomadas del README de cada repo; los privados se listan sin detalle.
PROJECT_INFO = {
    "vicidial-modern": ("Laravel + Vue", "Modernizacion de plataforma VICIdial"),
    "ITSS": ("Laravel", "Plataforma interna IT System Solutions"),
    "crm1.0": ("Laravel + Blade", "CRM BPO multi-tenant: cobranza, CX, venta"),
    "FactuChat": ("Laravel", "Facturacion conversacional"),
    "gps-integration": ("Express + Next.js", "Integracion GPS orquestada con n8n"),
    "vicidial-five": ("PHP", "Modulos sobre VICIdial"),
    "Portafolio-JoelDev": ("Astro", "Portafolio personal"),
    "Tienda-Web": ("Laravel + MySQL", "Gestion de inventario y ventas"),
    "Help-Desk": ("Laravel", "Mesa de ayuda e incidencias"),
    "Biblioteca": ("Node.js MVC", "Gestion de prestamos y usuarios"),
    "MaximunSegurity": ("Laravel", "Control de seguridad"),
    "Pruebas-E2E": ("JavaScript", "Suite de pruebas end-to-end"),
}
SKIP = {"daily-log", "Saimper"}

# Ponlo en True si algun cliente no quiere que el nombre de su repo aparezca:
# los privados pasan a listarse como "proyecto privado" conservando el volumen de trabajo.
ANONIMIZAR_PRIVADOS = False


def projects_svg(d):
    rows = [r for r in d["repos"] if r["name"] not in SKIP and r["commits"] > 0][:8]
    priv_n = 0
    W, T = 880, 13.0
    H = 96 + len(rows) * 30 + 38
    top = max((r["commits"] for r in rows), default=1)
    css = [RM, reveal("hd", 0.3, T, 4, 0.4), reveal("ft", 2.9, T, 3, 0.4)]
    body = []
    y = 104
    for i, r in enumerate(rows):
        stack, desc = PROJECT_INFO.get(r["name"], (r["lang"] or "-", ""))
        name = r["name"]
        if ANONIMIZAR_PRIVADOS and r["private"]:
            priv_n += 1
            name, desc = f"proyecto-privado-{priv_n}", "trabajo de cliente"
        bw = max(3.0, r["commits"] / top * 96)
        css.append(reveal(f"p{i}", 0.9 + i * 0.14, T, 4, 0.4))
        css.append(grow(f"pb{i}", 1.0 + i * 0.14, T, 0.8))
        vis = "priv" if r["private"] else "pub"
        desc = desc[:42]
        body.append(f"""<g style="animation:p{i} {T}s infinite">
  <text x="28" y="{y}" font-size="10.5" fill="{C['line']}">{vis}</text>
  <text x="72" y="{y}" font-size="12.5" fill="{C['bright']}">{esc(name)}</text>
  <text x="250" y="{y}" font-size="11.5" fill="{C['cyan']}">{esc(stack)}</text>
  <text x="404" y="{y}" font-size="11" fill="{C['dim']}">{esc(desc)}</text>
  <rect x="756" y="{y-9}" width="96" height="11" rx="2" fill="{C['panel2']}"/>
  <rect x="756" y="{y-9}" width="{bw:.1f}" height="11" rx="2" fill="{LEVELS[3] if i else C['cyan']}" style="animation:pb{i} {T}s infinite;transform-box:fill-box;transform-origin:left"/>
  <text x="748" y="{y}" text-anchor="end" font-size="11" fill="{C['text']}">{r['commits']}</text>
</g>""")
        y += 30

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{MONO}" role="img" aria-label="Proyectos ordenados por actividad">
<defs>{defs_common()}<style>{''.join(css)}</style></defs>
<rect width="{W}" height="{H}" rx="11" fill="{C['bg']}"/>
{chrome(W, H, "ls -la ~/proyectos --sort=commits", "12m")}
<g style="animation:hd {T}s infinite">
  <text x="28" y="62" font-size="12.5"><tspan fill="{C['cyan']}">$</tspan><tspan fill="{C['text']}" dx="7">proyectos por actividad</tspan><tspan fill="{C['dim']}" dx="8">commits propios en los ultimos 12 meses</tspan></text>
  <path d="M28 74h824" stroke="{C['line']}"/>
</g>
{''.join(body)}
<g style="animation:ft {T}s infinite">
  <path d="M28 {H-32}h824" stroke="{C['line']}"/>
  <text x="28" y="{H-14}" font-size="10.5" fill="{C['dim']}">Los repos privados son trabajo de cliente: se listan por transparencia, sin exponer codigo ni datos.</text>
</g>
</svg>"""


# ------------------------------------------------------------ link chips
def link_svg(label, value, glyph_path):
    w, h = 276, 46
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{MONO}" role="img" aria-label="{esc(label)}">
<defs><style>{RM}@keyframes sh{{0%,100%{{opacity:.5}}50%{{opacity:1}}}}</style></defs>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="8" fill="{C['panel']}" stroke="{C['line']}"/>
<rect x=".5" y=".5" width="3" height="{h-1}" rx="1.5" fill="{C['cyan']}"/>
<g transform="translate(20,13)" fill="none" stroke="{C['cyan']}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{glyph_path}</g>
<text x="52" y="20" font-size="9.5" fill="{C['dim']}" letter-spacing="1.4">{esc(label)}</text>
<text x="52" y="34" font-size="10.5" fill="{C['text']}">{esc(value)}</text>
<circle cx="{w-14}" cy="14" r="2.5" fill="{C['cyan']}" style="animation:sh 2.4s ease-in-out infinite"/>
</svg>"""


GLYPHS = {
    "portfolio": '<circle cx="10" cy="10" r="9"/><path d="M1 10h18M10 1a14 14 0 0 1 0 18a14 14 0 0 1 0-18"/>',
    "linkedin": '<rect x="1" y="1" width="18" height="18" rx="3"/><path d="M6 8.5V15M6 5.5v.01M10.5 15v-4a2.5 2.5 0 0 1 5 0v4"/>',
    "email": '<rect x="1" y="3.5" width="18" height="13" rx="2.5"/><path d="M1.8 5l8.2 6 8.2-6"/>',
    "github": '<path d="M7.5 18c-4 1.2-4-2.2-5.5-2.7m11 4.7v-3.4c0-1 .1-1.4-.5-2 2.6-.3 5-1.3 5-5.5a4.3 4.3 0 0 0-1.2-3 4 4 0 0 0-.1-3s-1-.3-3.2 1.2a11 11 0 0 0-5.8 0C4.9-.2 3.9.1 3.9.1a4 4 0 0 0-.1 3A4.3 4.3 0 0 0 2.6 6.2c0 4.2 2.4 5.2 5 5.5-.6.6-.6 1.2-.5 2V17"/>',
}


def main():
    os.makedirs(ASSETS, exist_ok=True)
    with open(os.path.join(ROOT, "scripts", "data.json")) as f:
        d = json.load(f)

    out = {
        "header.svg": header_svg(d),
        "stack.svg": stack_svg(d),
        "heatmap.svg": heatmap_svg(d),
        "timeline.svg": timeline_svg(),
        "projects.svg": projects_svg(d),
        "link-portfolio.svg": link_svg("PORTAFOLIO", "portafolio-joel-dev.vercel.app", GLYPHS["portfolio"]),
        "link-linkedin.svg": link_svg("LINKEDIN", "in/joel-solano", GLYPHS["linkedin"]),
        "link-email.svg": link_svg("EMAIL", "joeldavidsolanooerez@gmail.com", GLYPHS["email"]),
    }
    for name, svg in out.items():
        path = os.path.join(ASSETS, name)
        with open(path, "w") as f:
            f.write(svg)
        print(f"{name:22} {len(svg)/1024:6.1f} KB")


if __name__ == "__main__":
    main()
