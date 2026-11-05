#!/usr/bin/env python3
"""Gera os cards do carrossel (1080×1350) e os stories (1080×1920) de um post.

Uso: python3 scripts/render.py posts/2026-11-10
Lê  posts/<dia>/post.json  e grava card_01.jpg … card_NN.jpg, story_manha.jpg, story_tarde.jpg, story_noite.jpg.

Formato do post.json (campos principais):
{
  "tipo": "milagre" | "santo",
  "titulo": "Milagre Eucarístico de Lanciano",
  "titulo_en": "The Eucharistic Miracle of Lanciano",
  "subtitulo": "Lanciano, Itália · século VIII",
  "status": "reconhecido" | "investigacao" | null,
  "imagem": "imagem.jpg",                       # relativo à pasta do post (baixada por fetch_image.py)
  "imagem_credito": "Pintura de … (domínio público, Wikimedia Commons)",
  "cards": [ {"kicker": "O fato", "texto": "…"}, {"kicker": "A investigação", "texto": "…"}, … ],
  "decisao": "…",                                # último card: "O que a Igreja decidiu"
  "fontes": ["Vatican.va — carta de João Paulo II, 2004", "…"],
  "stories": {
     "manha": {"nome": "São Leão Magno", "anos": "† 461", "padroeiro": "Padroeiro dos …", "linhas": ["…","…","…"], "imagem": "santo.jpg"},
     "tarde": {"kicker": "Um detalhe que não coube no post", "texto": "…"},
     "noite": {"citacao": "…", "autor": "São Leão Magno"}
  }
}
"""
import base64, json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
BRAND = RAIZ / "brand"
RED, RED_DARK, CREAM, CHAR, GREY = "#A6192E", "#7A1020", "#F7F2E8", "#26221E", "#6B655E"


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


def data_uri(p):
    ext = Path(p).suffix.lower().strip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "svg": "image/svg+xml", "ttf": "font/ttf"}[ext]
    return f"data:{mime};base64,{b64(p)}"


FONTS = f"""
@font-face {{ font-family: 'Cinzel'; src: url({data_uri(BRAND/'fonts/Cinzel.ttf')}) format('truetype'); font-weight: 400 900; }}
@font-face {{ font-family: 'Cormorant'; src: url({data_uri(BRAND/'fonts/CormorantGaramond.ttf')}) format('truetype'); font-weight: 300 700; }}
"""
AVATAR = data_uri(BRAND / "logo_avatar_claro.svg")
AVATAR_DARK = data_uri(BRAND / "logo_avatar_transparente.svg")
SELO = data_uri(BRAND / "logo_selo_claro.svg")

STATUS = {
    "reconhecido": ("RECONHECIDO PELA IGREJA", "CHURCH-RECOGNIZED"),
    "investigacao": ("EM INVESTIGAÇÃO", "UNDER INVESTIGATION"),
}

CSS = f"""
{FONTS}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 1080px; background: {CREAM}; color: {CHAR}; font-family: 'Cormorant', serif; -webkit-font-smoothing: antialiased; }}
.page {{ position: relative; width: 1080px; overflow: hidden; }}
.card {{ height: 1350px; }}
.story {{ height: 1920px; background: {CHAR}; color: {CREAM}; }}
.cinzel {{ font-family: 'Cinzel', serif; }}
.red {{ color: {RED}; }}
.badge {{ position: absolute; top: 44px; right: 44px; z-index: 3; font-family: 'Cinzel'; font-weight: 700; font-size: 22px; letter-spacing: 3px;
         color: {CREAM}; background: {RED}; padding: 14px 22px 12px; border-radius: 6px; text-align: center; line-height: 1.25; }}
.badge small {{ display: block; font-size: 15px; letter-spacing: 2px; opacity: .85; }}
.hero {{ position: absolute; top: 0; left: 0; width: 1080px; height: 820px; overflow: hidden; }}
.hero img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.hero::after {{ content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(38,34,30,0) 60%, rgba(38,34,30,.55) 100%); }}
.filete {{ position: absolute; left: 44px; right: 44px; top: 44px; height: 732px; border: 3px solid {RED}; z-index: 2; pointer-events: none; }}
.band {{ position: absolute; top: 820px; left: 0; width: 1080px; height: 530px; padding: 56px 72px 0; }}
.rule {{ width: 120px; height: 4px; background: {RED}; margin: 0 0 28px; }}
h1 {{ font-family: 'Cinzel'; font-weight: 700; font-size: 64px; line-height: 1.12; letter-spacing: 1px; }}
h1.small {{ font-size: 52px; }}
.sub {{ font-size: 40px; font-style: italic; color: {GREY}; margin-top: 18px; }}
.sub_en {{ font-size: 32px; color: {GREY}; margin-top: 6px; }}
.foot {{ position: absolute; left: 72px; right: 72px; bottom: 44px; display: flex; align-items: center; justify-content: space-between; font-family: 'Cinzel'; font-size: 22px; letter-spacing: 4px; color: {RED}; }}
.foot img {{ width: 72px; height: 72px; }}
.credit {{ position: absolute; left: 72px; bottom: 136px; font-size: 22px; color: {GREY}; font-style: italic; }}
/* cards de texto */
.text {{ padding: 120px 96px 0; font-size: 50px; }}
.kicker {{ font-family: 'Cinzel'; font-weight: 700; font-size: .6em; letter-spacing: 6px; color: {RED}; margin-bottom: 36px; }}
.body {{ font-size: 1em; line-height: 1.32; font-weight: 500; }}
.body p + p {{ margin-top: .6em; }}
.body_en {{ font-size: .72em; line-height: 1.32; color: {GREY}; margin-top: .9em; padding-top: .7em; border-top: 2px solid {RED}; }}
.num {{ position: absolute; top: 56px; right: 96px; font-family: 'Cinzel'; font-size: 26px; letter-spacing: 4px; color: {GREY}; }}
.decisao {{ font-size: 1.08em; line-height: 1.3; font-weight: 600; }}
.fontes {{ margin-top: 1em; font-size: .6em; line-height: 1.45; color: {GREY}; }}
.fontes li {{ list-style: none; padding-left: 36px; position: relative; }}
.fontes li::before {{ content: '·'; position: absolute; left: 8px; color: {RED}; font-weight: 700; }}
.selo-final {{ position: absolute; right: 80px; bottom: 150px; width: 260px; opacity: .95; }}
/* stories */
.s-wrap {{ position: absolute; inset: 0; padding: 200px 90px 0; }}
.s-avatar {{ position: absolute; top: 84px; left: 50%; transform: translateX(-50%); width: 150px; }}
.s-hero {{ width: 900px; height: 900px; margin: 0 auto; overflow: hidden; border: 3px solid {RED}; }}
.s-hero img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.s-name {{ font-family: 'Cinzel'; font-weight: 700; font-size: 66px; line-height: 1.15; text-align: center; margin-top: 56px; }}
.s-years {{ font-family: 'Cinzel'; font-size: 34px; letter-spacing: 5px; color: {RED}; text-align: center; margin-top: 16px; }}
.s-patron {{ font-size: 40px; font-style: italic; text-align: center; color: #CFC7B8; margin-top: 18px; }}
.s-lines {{ margin: 40px auto 0; width: 900px; font-size: 42px; line-height: 1.4; }}
.s-lines p {{ padding-left: 40px; position: relative; }}
.s-lines p::before {{ content: ''; position: absolute; left: 0; top: 24px; width: 18px; height: 3px; background: {RED}; }}
.s-kicker {{ font-family: 'Cinzel'; font-weight: 700; font-size: 32px; letter-spacing: 6px; color: {RED}; text-align: center; margin-top: 60px; }}
.s-text {{ font-size: 56px; line-height: 1.35; font-weight: 500; text-align: center; margin-top: 60px; }}
.s-text_en {{ font-size: 40px; line-height: 1.35; text-align: center; color: #CFC7B8; margin-top: 50px; padding-top: 40px; border-top: 2px solid {RED}; }}
.s-quote {{ font-size: 68px; line-height: 1.3; font-style: italic; text-align: center; margin-top: 140px; }}
.s-author {{ font-family: 'Cinzel'; font-size: 34px; letter-spacing: 5px; color: {RED}; text-align: center; margin-top: 70px; }}
.s-foot {{ position: absolute; left: 0; right: 0; bottom: 120px; text-align: center; font-family: 'Cinzel'; font-size: 26px; letter-spacing: 6px; color: {RED}; }}
.s-cta {{ position: absolute; left: 0; right: 0; bottom: 230px; text-align: center; font-size: 34px; color: #CFC7B8; font-style: italic; }}
"""


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def paras(txt):
    return "".join(f"<p>{esc(p.strip())}</p>" for p in (txt or "").split("\n\n") if p.strip())


def badge(status):
    if not status or status not in STATUS:
        return ""
    pt, en = STATUS[status]
    return f'<div class="badge">{pt}<small>{en}</small></div>'


def foot(n, total):
    return f'<div class="foot"><span>ACTA DEI · MYSTERIUM FIDEI</span><span>{n:02d} / {total:02d}</span><img src="{AVATAR}"></div>'


def card_capa(post, total, pasta):
    tem_img = post.get("imagem") and (pasta / post["imagem"]).exists()
    img = data_uri(pasta / post["imagem"]) if tem_img else SELO
    fit = "" if tem_img else ' style="object-fit:contain;padding:90px;background:#EFE8DA"'
    small = " small" if len(post["titulo"]) > 34 else ""
    return f"""<div class="page card">
      {badge(post.get("status"))}
      <div class="hero"><img src="{img}"{fit}></div><div class="filete"></div>
      <div class="band"><div class="rule"></div>
        <h1 class="{small}">{esc(post['titulo'])}</h1>
        <div class="sub">{esc(post.get('subtitulo',''))}</div>
        <div class="sub_en">{esc(post.get('titulo_en',''))}</div>
      </div>
      <div class="credit">{esc(post.get('imagem_credito',''))}</div>
      {foot(1, total)}</div>"""


def card_texto(c, n, total):
    en = f'<div class="body_en">{paras(c["texto_en"])}</div>' if c.get("texto_en") else ""
    return f"""<div class="page card"><div class="num">{n:02d}</div>
      <div class="text"><div class="kicker">{esc(c.get('kicker',''))}</div>
        <div class="body">{paras(c['texto'])}</div>{en}</div>{foot(n, total)}</div>"""


def card_decisao(post, n, total):
    fontes = "".join(f"<li>{esc(f)}</li>" for f in post.get("fontes", []))
    en = f'<div class="body_en">{paras(post["decisao_en"])}</div>' if post.get("decisao_en") else ""
    return f"""<div class="page card"><div class="num">{n:02d}</div>
      <div class="text"><div class="kicker">O QUE A IGREJA DECIDIU · THE CHURCH'S DECISION</div>
        <div class="decisao">{paras(post['decisao'])}</div>{en}
        <ul class="fontes"><li style="font-family:Cinzel;letter-spacing:3px;font-size:.8em;color:{RED}">FONTES · SOURCES</li>{fontes}</ul></div>
      {foot(n, total)}</div>"""


def story_manha(s, pasta):
    tem = s.get("imagem") and (pasta / s["imagem"]).exists()
    hero = f'<div class="s-hero"><img src="{data_uri(pasta / s["imagem"])}"></div>' if tem else '<div style="height:380px"></div>'
    linhas = "".join(f"<p>{esc(l)}</p>" for l in s.get("linhas", []))
    return f"""<div class="page story"><img class="s-avatar" src="{AVATAR_DARK}">
      <div class="s-wrap">{hero}
        <div class="s-name">{esc(s['nome'])}</div><div class="s-years">{esc(s.get('anos',''))}</div>
        <div class="s-patron">{esc(s.get('padroeiro',''))}</div><div class="s-lines">{linhas}</div></div>
      <div class="s-foot">SANTO DO DIA · SAINT OF THE DAY</div></div>"""


def story_tarde(s):
    en = f'<div class="s-text_en">{esc(s["texto_en"])}</div>' if s.get("texto_en") else ""
    return f"""<div class="page story"><img class="s-avatar" src="{AVATAR_DARK}">
      <div class="s-wrap" style="padding-top:340px"><div class="s-kicker">{esc(s.get('kicker','UM DETALHE A MAIS'))}</div>
        <div class="s-text">{esc(s['texto'])}</div>{en}</div>
      <div class="s-cta">O relato completo está no post de hoje · Full story in today's post</div>
      <div class="s-foot">ACTA DEI · MYSTERIUM FIDEI</div></div>"""


def story_noite(s):
    return f"""<div class="page story"><img class="s-avatar" src="{AVATAR_DARK}">
      <div class="s-wrap" style="padding-top:420px"><div class="s-quote">“{esc(s['citacao'])}”</div>
        <div class="s-author">{esc(s.get('autor',''))}</div>
        {f'<div class="s-text_en" style="font-style:italic">“{esc(s["citacao_en"])}”</div>' if s.get('citacao_en') else ''}</div>
      <div class="s-foot">ACTA DEI · MYSTERIUM FIDEI</div></div>"""


def render(pasta):
    pasta = Path(pasta)
    post = json.loads((pasta / "post.json").read_text())
    cards = post.get("cards", [])
    total = 1 + len(cards) + (1 if post.get("decisao") else 0)
    htmls = [("card_01.jpg", card_capa(post, total, pasta), 1350)]
    for i, c in enumerate(cards, start=2):
        htmls.append((f"card_{i:02d}.jpg", card_texto(c, i, total), 1350))
    if post.get("decisao"):
        htmls.append((f"card_{total:02d}.jpg", card_decisao(post, total, total), 1350))
    st = post.get("stories", {})
    if st.get("manha"): htmls.append(("story_manha.jpg", story_manha(st["manha"], pasta), 1920))
    if st.get("tarde"): htmls.append(("story_tarde.jpg", story_tarde(st["tarde"]), 1920))
    if st.get("noite"): htmls.append(("story_noite.jpg", story_noite(st["noite"]), 1920))

    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for nome, body, h in htmls:
            pg = br.new_page(viewport={"width": 1080, "height": h}, device_scale_factor=1)
            pg.set_content(f"<html><head><style>{CSS}</style></head><body>{body}</body></html>")
            pg.wait_for_timeout(250)
            pg.evaluate("""() => { const t = document.querySelector('.text'); if (!t) return;
                let fs = 50; const limite = 1350 - 150;
                while (t.getBoundingClientRect().bottom > limite && fs > 26) { fs -= 1; t.style.fontSize = fs + 'px'; } }""")
            pg.evaluate("""() => { const t = document.querySelector('.s-wrap'); if (!t) return;
                let z = 1.0; const limite = 1920 - 340;
                while (t.getBoundingClientRect().bottom > limite && z > 0.6) { z -= 0.02; t.style.zoom = z; } }""")
            pg.wait_for_timeout(100)
            pg.screenshot(path=str(pasta / nome), type="jpeg", quality=92)
            pg.close()
        br.close()
    print("gerados:", ", ".join(n for n, _, _ in htmls))
    return [n for n, _, _ in htmls]


if __name__ == "__main__":
    render(sys.argv[1])
