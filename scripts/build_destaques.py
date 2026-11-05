#!/usr/bin/env python3
"""Gera as capas dos destaques do Instagram (1080×1080, área útil no círculo central).

Padrão da marca: fundo creme, anel duplo vermelho (igual ao avatar), ícone em traço vermelho.
Sem texto: o nome do destaque é o título que o Instagram mostra abaixo do círculo.
Saída: brand/destaques/<slug>.png + preview.
"""
import base64
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
OUT = RAIZ / "brand" / "destaques"
RED, CREAM = "#A6192E", "#F7F2E8"
SW = 14  # espessura padrão do traço

# ---------- ícones (desenhados em um quadro de -200..200, centro 0,0) ----------
def santo():
    # cabeça com auréola e ombros
    return f"""
<circle cx="0" cy="-70" r="118" fill="none" stroke="{RED}" stroke-width="8" opacity="0.9"/>
<circle cx="0" cy="-40" r="62" fill="none" stroke="{RED}" stroke-width="{SW}"/>
<path d="M-150 175 A150 150 0 0 1 150 175" fill="none" stroke="{RED}" stroke-width="{SW}" stroke-linecap="round"/>
<path d="M0 95 V175" stroke="{RED}" stroke-width="7" stroke-linecap="round" opacity="0.7"/>
"""

def eucaristico():
    # cálice com hóstia (cruz gravada)
    return f"""
<circle cx="0" cy="-118" r="58" fill="none" stroke="{RED}" stroke-width="{SW}"/>
<path d="M0 -146 V-90 M-24 -118 H24" stroke="{RED}" stroke-width="7" stroke-linecap="round" opacity="0.85"/>
<path d="M-120 -30 H120 Q120 70 0 90 Q-120 70 -120 -30 Z" fill="none" stroke="{RED}" stroke-width="{SW}" stroke-linejoin="round"/>
<path d="M0 90 V150" stroke="{RED}" stroke-width="{SW}"/>
<path d="M-70 170 Q0 140 70 170" fill="none" stroke="{RED}" stroke-width="{SW}" stroke-linecap="round"/>
"""

def aparicao():
    # estrela de oito pontas (Stella Maris)
    import math
    pts = []
    for i in range(16):
        r = 150 if i % 2 == 0 else 58
        a = math.radians(i * 22.5 - 90)
        pts.append(f"{r*math.cos(a):.1f},{r*math.sin(a)-20:.1f}")
    return f"""
<polygon points="{' '.join(pts)}" fill="none" stroke="{RED}" stroke-width="{SW}" stroke-linejoin="round"/>
<circle cx="0" cy="-20" r="18" fill="{RED}"/>
"""

def incorrupto():
    # relicário em arco gótico com cruz no topo
    return f"""
<path d="M-110 170 V-20 Q-110 -120 0 -150 Q110 -120 110 -20 V170 Z" fill="none" stroke="{RED}" stroke-width="{SW}" stroke-linejoin="round"/>
<path d="M-150 170 H150" stroke="{RED}" stroke-width="{SW}" stroke-linecap="round"/>
<path d="M0 -150 V-200 M-22 -178 H22" stroke="{RED}" stroke-width="8" stroke-linecap="round"/>
<path d="M-62 170 V40 Q-62 -30 0 -50 Q62 -30 62 40 V170" fill="none" stroke="{RED}" stroke-width="7" opacity="0.7"/>
"""

def brasil():
    # Cruzeiro do Sul (cinco estrelas), proporções da constelação
    import math
    def star(cx, cy, r):
        pts = []
        for i in range(10):
            rr = r if i % 2 == 0 else r * 0.42
            a = math.radians(i * 36 - 90)
            pts.append(f"{cx+rr*math.cos(a):.1f},{cy+rr*math.sin(a):.1f}")
        return f'<polygon points="{" ".join(pts)}" fill="{RED}"/>'
    # Gacrux (topo), Acrux (base), Mimosa (esq.), Delta (dir.), Epsilon (pequena)
    s = [star(0, -150, 50), star(20, 150, 58), star(-130, -5, 52), star(110, 10, 48), star(-55, 45, 26)]
    return "\n".join(s) + f"""
<path d="M0 -150 L20 150 M-125 -5 L105 10" stroke="{RED}" stroke-width="3" opacity="0.35"/>
"""

def palavras():
    # aspas tipográficas em Cormorant Garamond
    return f"""
<text x="0" y="250" text-anchor="middle" font-family="Cormorant Garamond" font-weight="700" font-size="640" fill="{RED}">”</text>
"""

def fontes():
    # livro aberto com linhas
    return f"""
<path d="M0 -110 Q-80 -150 -170 -120 V120 Q-80 90 0 130 Q80 90 170 120 V-120 Q80 -150 0 -110 Z" fill="none" stroke="{RED}" stroke-width="{SW}" stroke-linejoin="round"/>
<path d="M0 -110 V130" stroke="{RED}" stroke-width="{SW}"/>
<path d="M-130 -70 Q-70 -90 -35 -70 M-130 -20 Q-70 -40 -35 -20 M-130 30 Q-70 10 -35 30 M35 -70 Q70 -90 130 -70 M35 -20 Q70 -40 130 -20 M35 30 Q70 10 130 30" fill="none" stroke="{RED}" stroke-width="7" stroke-linecap="round" opacity="0.75"/>
"""

CAPAS = [
    ("01_santo_do_dia", "Santo do dia", santo),
    ("02_milagres_eucaristicos", "Milagres Eucarísticos", eucaristico),
    ("03_aparicoes", "Aparições", aparicao),
    ("04_incorruptos", "Incorruptos", incorrupto),
    ("05_brasil", "Brasil", brasil),
    ("06_palavras", "Palavras", palavras),
    ("07_fontes", "Fontes", fontes),
]


def svg(icon_fn, escala=1.3):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
<defs><linearGradient id="red" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#B9253A"/><stop offset="100%" stop-color="#7A1020"/></linearGradient></defs>
<rect width="1080" height="1080" fill="{CREAM}"/>
<circle cx="540" cy="540" r="420" fill="none" stroke="url(#red)" stroke-width="18"/>
<circle cx="540" cy="540" r="386" fill="none" stroke="url(#red)" stroke-width="5"/>
<g transform="translate(540 540) scale({escala})">{icon_fn()}</g>
</svg>"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    font = base64.b64encode((RAIZ / "brand/fonts/CormorantGaramond.ttf").read_bytes()).decode()
    css = f"@font-face{{font-family:'Cormorant Garamond';src:url(data:font/ttf;base64,{font});font-weight:700}}body{{margin:0}}svg{{display:block}}"
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1080})
        for slug, nome, fn in CAPAS:
            s = svg(fn)
            (OUT / f"{slug}.svg").write_text(s)
            pg.set_content(f"<html><head><style>{css}</style></head><body>{s}</body></html>")
            pg.wait_for_timeout(150)
            pg.screenshot(path=str(OUT / f"{slug}.png"))
            print("ok", slug, nome)
        # preview em tamanho real de destaque (círculos ~ 90 px) + grande
        tiles = "".join(
            f'<div class="t"><div class="c" style="background-image:url({slug}.png)"></div><span>{nome}</span></div>'
            for slug, nome, _ in CAPAS)
        prev = f"""<html><head><meta charset="utf-8"><style>{css}
body{{background:#fff;font-family:-apple-system,Helvetica,sans-serif;padding:24px;width:1032px}}
.row{{display:flex;gap:18px;margin-bottom:28px}} .t{{text-align:center;width:96px}}
.c{{width:90px;height:90px;border-radius:50%;background-size:cover;background-position:center;border:2px solid #dbdbdb;margin:0 auto 6px}}
span{{font-size:12px;color:#262626}}
.big{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}} .big img{{width:100%;border-radius:50%}}
</style></head><body><div class="row">{tiles}</div><div class="big">{''.join(f'<img src="{s}.png">' for s,_,_ in CAPAS)}</div></body></html>"""
        (OUT / "preview.html").write_text(prev)
        pg2 = b.new_page(viewport={"width": 1080, "height": 760})
        pg2.goto(f"file://{OUT}/preview.html")
        pg2.wait_for_timeout(300)
        pg2.screenshot(path=str(OUT / "preview.png"), full_page=True)
        b.close()


if __name__ == "__main__":
    main()
