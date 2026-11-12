#!/usr/bin/env python3
"""Gera os cards do carrossel (1080×1350), os cards do Evangelho do dia (1080×1350) e os stories (1080×1920) de um post.

Uso: python3 scripts/render.py posts/2026-11-10
Lê  posts/<dia>/post.json  e grava card_01.jpg … card_NN.jpg, story_manha.jpg, story_tarde.jpg, story_noite.jpg e,
quando o post tem o bloco "evangelho": evangelho_01.jpg (versículo), evangelho_02.jpg (o fato), legenda_evangelho.txt
e hashtags_evangelho.txt (se ainda não existir).

Bloco "evangelho" (post das 6h):
  "evangelho": {
    "referencia": "João 2,13-22", "referencia_en": "John 2:13-22",
    "versiculo": "Destruí este templo, e em três dias eu o reerguerei.",       # 1 versículo, ≤ 140 caracteres
    "versiculo_en": "Destroy this temple, and in three days I will raise it up.",
    "celebracao": "Dedicação da Basílica de Latrão · Festa",                      # opcional; padrão: título do post
    "leituras": "Ez 47,1-2.8-9.12 · 1Cor 3,9c-11.16-17 · Jo 2,13-22",            # opcional
    "fato": "3 a 4 linhas que ancoram o Evangelho em data, lugar e história (≤ 480 caracteres)",
    "fato_en": "…", "fato_fonte": "Vatican.va — …"
  }

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
  "decisao": "…",                                # último card: "O que a Santa Igreja Católica decidiu"
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
# Vermelho-selo para TEXTO sobre fundo escuro (stories): o #A6192E some no carvão (contraste 2,1:1).
# Mesma matiz, mais luz e traço mais grosso (peso 700) — contraste 4,3:1. Em fundo creme segue o RED.
RED_VIVO = "#F0434F"


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
    "reconhecido": ("RECONHECIDO PELA SANTA IGREJA CATÓLICA", "RECOGNIZED BY THE HOLY CATHOLIC CHURCH"),
    "investigacao": ("EM INVESTIGAÇÃO PELA SANTA IGREJA CATÓLICA", "UNDER INVESTIGATION BY THE HOLY CATHOLIC CHURCH"),
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
.badge {{ position: absolute; top: 44px; right: 44px; z-index: 3; font-family: 'Cinzel'; font-weight: 700; font-size: 19px; letter-spacing: 2.5px;
         color: {CREAM}; background: {RED}; padding: 14px 20px 12px; border-radius: 6px; text-align: center; line-height: 1.25; }}
.badge small {{ display: block; font-size: 13px; letter-spacing: 1.5px; opacity: .85; margin-top: 4px; }}
.hero {{ position: absolute; top: 0; left: 0; width: 1080px; height: 820px; overflow: hidden; }}
.hero img {{ width: 100%; height: 100%; object-fit: cover; object-position: center 25%; display: block; }}
.hero img.bg, .s-hero img.bg {{ position: absolute; inset: -60px; width: calc(100% + 120px); height: calc(100% + 120px); object-fit: cover; object-position: center; filter: blur(34px) brightness(.62) saturate(.9); }}
.hero img.fg, .s-hero img.fg {{ position: relative; z-index: 1; object-fit: contain; object-position: center; }}
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
.s-wrap {{ position: absolute; inset: 0; padding: 270px 90px 0; }}
.s-avatar {{ position: absolute; top: 84px; left: 50%; transform: translateX(-50%); width: 150px; }}
.s-hero {{ width: 900px; height: 860px; margin: 0 auto; overflow: hidden; border: 3px solid {RED}; }}
.s-hero {{ position: relative; }}
.s-hero img {{ width: 100%; height: 100%; object-fit: cover; object-position: center 20%; display: block; }}
.s-name {{ font-family: 'Cinzel'; font-weight: 700; font-size: 66px; line-height: 1.15; text-align: center; margin-top: 56px; }}
.s-years {{ font-family: 'Cinzel'; font-weight: 700; font-size: 34px; letter-spacing: 5px; color: {RED_VIVO}; text-align: center; margin-top: 16px; }}
.s-patron {{ font-size: 40px; font-style: italic; text-align: center; color: #CFC7B8; margin-top: 18px; }}
.s-lines {{ margin: 40px auto 0; width: 900px; font-size: 42px; line-height: 1.4; }}
.s-lines p {{ padding-left: 40px; position: relative; }}
.s-lines p::before {{ content: ''; position: absolute; left: 0; top: 24px; width: 18px; height: 3px; background: {RED_VIVO}; }}
.s-kicker {{ font-family: 'Cinzel'; font-weight: 700; font-size: 32px; letter-spacing: 6px; color: {RED_VIVO}; text-align: center; margin-top: 60px; }}
.s-text {{ font-size: 56px; line-height: 1.35; font-weight: 500; text-align: center; margin-top: 60px; }}
.s-text_en {{ font-size: 40px; line-height: 1.35; text-align: center; color: #CFC7B8; margin-top: 50px; padding-top: 40px; border-top: 2px solid {RED}; }}
.s-quote {{ font-size: 68px; line-height: 1.3; font-style: italic; text-align: center; margin-top: 140px; }}
.s-author {{ font-family: 'Cinzel'; font-weight: 700; font-size: 34px; letter-spacing: 5px; color: {RED_VIVO}; text-align: center; margin-top: 70px; }}
.s-foot {{ position: absolute; left: 0; right: 0; bottom: 330px; text-align: center; font-family: 'Cinzel'; font-weight: 700; font-size: 26px; letter-spacing: 6px; color: {RED_VIVO}; }}
.s-cta {{ position: absolute; left: 0; right: 0; bottom: 410px; text-align: center; font-size: 34px; color: #CFC7B8; font-style: italic; }}
/* story da manhã v2: "Hoje na Igreja" */
.s-date {{ font-size: 36px; font-style: italic; text-align: center; color: #CFC7B8; margin-top: 14px; }}
.s-ev {{ width: 900px; margin: 44px auto 0; padding-top: 34px; border-top: 2px solid {RED}; text-align: center; }}
.s-ev-k {{ font-family: 'Cinzel'; font-weight: 700; font-size: 28px; letter-spacing: 5px; color: {RED_VIVO}; }}
.s-ev-v {{ font-size: 46px; line-height: 1.3; font-style: italic; margin-top: 18px; }}
.s-next {{ font-family: 'Cinzel'; font-size: 24px; letter-spacing: 4px; text-align: center; color: #CFC7B8; margin-top: 44px; }}
.s-next b {{ color: {CREAM}; font-weight: 700; }}
/* Evangelho do dia (1080×1350) */
.ev {{ height: 1350px; padding: 0 96px; display: flex; flex-direction: column; align-items: center; text-align: center; }}
.ev-avatar {{ width: 118px; height: 118px; margin-top: 70px; }}
.ev-kicker {{ font-family: 'Cinzel'; font-weight: 700; font-size: 26px; letter-spacing: 7px; color: {RED}; margin-top: 34px; }}
.ev-date {{ font-size: 36px; font-style: italic; color: {GREY}; margin-top: 12px; }}
.ev-cel {{ font-family: 'Cinzel'; font-size: 23px; letter-spacing: 3px; color: {CHAR}; margin-top: 12px; line-height: 1.4; }}
.ev-main {{ flex: 1; width: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; overflow: hidden; padding: 16px 0; }}
.ev-mark {{ font-family: 'Cinzel'; font-size: 150px; line-height: .55; color: {RED}; opacity: .9; margin-bottom: 18px; }}
.ev-verse {{ font-size: 86px; line-height: 1.16; font-style: italic; font-weight: 500; }}
.ev-rule {{ width: 120px; height: 4px; background: {RED}; margin: 46px auto 26px; }}
.ev-ref {{ font-family: 'Cinzel'; font-weight: 700; font-size: 34px; letter-spacing: 5px; color: {RED}; }}
.ev-ref-en {{ font-family: 'Cinzel'; font-size: 22px; letter-spacing: 3px; color: {GREY}; margin-top: 10px; }}
.ev-en {{ font-size: 34px; font-style: italic; color: {GREY}; line-height: 1.3; margin-bottom: 150px; max-width: 860px; }}
.ev-sub {{ font-size: 32px; font-style: italic; color: {GREY}; margin: -14px 0 36px; }}
.ev-fonte {{ margin-top: .9em; font-size: .52em; color: {GREY}; line-height: 1.4; }}
.ev-fonte b {{ font-family: 'Cinzel'; font-weight: 700; letter-spacing: 3px; color: {RED}; font-size: .85em; }}
"""

DIAS_PT = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
HASHTAGS_EVANGELHO = ("#evangelhododia #evangelho #liturgiadiaria #palavradedeus #santaigrejacatolica "
                      "#gospeloftheday #dailygospel #catholic #catholicfaith #holycatholicchurch #actadei #mysteriumfidei")


def data_extenso(pasta):
    """'segunda-feira, 9 de novembro de 2026' a partir do nome da pasta (AAAA-MM-DD)."""
    import datetime as _dt
    try:
        d = _dt.date.fromisoformat(Path(pasta).name)
    except ValueError:
        d = _dt.date.today()
    return f"{DIAS_PT[d.weekday()]}, {d.day} de {MESES_PT[d.month - 1]} de {d.year}", d


def img_tag(path, box_ratio, perda_max=0.15):
    """Regra de enquadramento: se o recorte `cover` descartasse mais de `perda_max` (15%) da imagem,
    ela entra inteira sobre um fundo desfocado dela mesma; senão, recorte normal. Vale para retrato,
    quadrado e panorâmica. `box_ratio` = largura/altura da moldura."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            w, h = im.size
    except Exception:
        w, h = 1, 1
    r = w / h
    perda = 1 - min(r / box_ratio, box_ratio / r)
    uri = data_uri(path)
    if perda > perda_max:
        return f'<img class="bg" src="{uri}"><img class="fg" src="{uri}">'
    return f'<img src="{uri}">'


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
    img = img_tag(pasta / post["imagem"], 1080 / 820) if tem_img else f'<img src="{SELO}" style="object-fit:contain;padding:90px;background:#EFE8DA">'
    small = " small" if len(post["titulo"]) > 34 else ""
    return f"""<div class="page card">
      {badge(post.get("status"))}
      <div class="hero">{img}</div><div class="filete"></div>
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
      <div class="text"><div class="kicker">O QUE A SANTA IGREJA CATÓLICA DECIDIU · THE HOLY CATHOLIC CHURCH'S DECISION</div>
        <div class="decisao">{paras(post['decisao'])}</div>{en}
        <ul class="fontes"><li style="font-family:Cinzel;letter-spacing:3px;font-size:.8em;color:{RED}">FONTES · SOURCES</li>{fontes}</ul></div>
      {foot(n, total)}</div>"""


def story_manha(s, pasta, post=None):
    """Story das 7h. Sem bloco "evangelho": o story clássico do santo do dia. Com ele: "Hoje na Igreja" —
    santo do dia + referência e versículo do Evangelho + o que vem ao meio-dia (ponte entre as peças da manhã)."""
    tem = s.get("imagem") and (pasta / s["imagem"]).exists()
    ev = (post or {}).get("evangelho")
    if not ev:
        hero = f'<div class="s-hero">{img_tag(pasta / s["imagem"], 900 / 860)}</div>' if tem else '<div style="height:380px"></div>'
        linhas = "".join(f"<p>{esc(l)}</p>" for l in s.get("linhas", []))
        return f"""<div class="page story">
          <div class="s-wrap">{hero}
            <div class="s-name">{esc(s['nome'])}</div><div class="s-years">{esc(s.get('anos',''))}</div>
            <div class="s-patron">{esc(s.get('padroeiro',''))}</div><div class="s-lines">{linhas}</div></div>
          <div class="s-foot">SANTO DO DIA · SAINT OF THE DAY</div></div>"""
    data_pt, _ = data_extenso(pasta)
    hero = f'<div class="s-hero" style="height:600px;margin-top:40px">{img_tag(pasta / s["imagem"], 900 / 600)}</div>' if tem else '<div style="height:120px"></div>'
    linhas = "".join(f"<p>{esc(l)}</p>" for l in s.get("linhas", [])[:2])
    feed = (post or {}).get("titulo", "")
    proximo = f'<div class="s-next">AO MEIO-DIA · <b>{esc(feed).upper()}</b></div>' if feed and feed != s.get("nome") else \
              '<div class="s-next">AO MEIO-DIA · <b>A HISTÓRIA COMPLETA NO FEED</b></div>'
    return f"""<div class="page story">
      <div class="s-wrap" style="padding-top:80px">
        <img src="{AVATAR_DARK}" style="display:block;width:150px;margin:0 auto">
        <div class="s-kicker" style="margin-top:30px">HOJE NA IGREJA · TODAY IN THE CHURCH</div>
        <div class="s-date">{esc(data_pt.rsplit(' de ', 1)[0])}</div>
        {hero}
        <div class="s-name">{esc(s['nome'])}</div><div class="s-years">{esc(s.get('anos',''))}</div>
        <div class="s-lines" style="margin-top:28px;font-size:38px">{linhas}</div>
        <div class="s-ev"><div class="s-ev-k">EVANGELHO · {esc(ev.get('referencia','')).upper()}</div>
          <div class="s-ev-v">“{esc(ev.get('versiculo',''))}”</div></div>
        {proximo}</div>
      <div class="s-foot">ACTA DEI · MYSTERIUM FIDEI</div></div>"""


def evangelho_versiculo(ev, post, pasta):
    """Card 1 do Evangelho: o que a pessoa encaminha. Um versículo, a referência, a data e a celebração."""
    data_pt, _ = data_extenso(pasta)
    cel = ev.get("celebracao") or post.get("titulo", "")
    en = f'<div class="ev-en">“{esc(ev["versiculo_en"])}”</div>' if ev.get("versiculo_en") else '<div style="height:150px"></div>'
    ref_en = f'<div class="ev-ref-en">{esc(ev["referencia_en"]).upper()}</div>' if ev.get("referencia_en") else ""
    return f"""<div class="page card ev">
      <img class="ev-avatar" src="{AVATAR}">
      <div class="ev-kicker">EVANGELHO DO DIA · GOSPEL OF THE DAY</div>
      <div class="ev-date">{esc(data_pt)}</div>
      <div class="ev-cel">{esc(cel).upper()}</div>
      <div class="ev-main"><div class="ev-mark">“</div>
        <div class="ev-verse">{esc(ev['versiculo'])}</div>
        <div class="ev-rule"></div><div class="ev-ref">{esc(ev.get('referencia','')).upper()}</div>{ref_en}</div>
      {en}
      {foot(1, 2)}</div>"""


def evangelho_fato(ev, post, pasta):
    """Card 2 do Evangelho: "O fato" — data, lugar e história que ancoram a leitura. Não é homilia."""
    cel = ev.get("celebracao") or post.get("titulo", "")
    en = f'<div class="body_en">{paras(ev["fato_en"])}</div>' if ev.get("fato_en") else ""
    fonte = f'<div class="ev-fonte"><b>FONTE · SOURCE</b><br>{esc(ev["fato_fonte"])}</div>' if ev.get("fato_fonte") else ""
    return f"""<div class="page card"><div class="num">02</div>
      <div class="text"><div class="kicker">O FATO · THE FACT</div>
        <div class="ev-sub">Evangelho de hoje: {esc(ev.get('referencia',''))} · {esc(cel)}</div>
        <div class="body">{paras(ev['fato'])}</div>{en}{fonte}</div>
      {foot(2, 2)}</div>"""


def legenda_evangelho(ev, post, pasta):
    data_pt, _ = data_extenso(pasta)
    cel = ev.get("celebracao") or post.get("titulo", "")
    partes = [f"EVANGELHO DO DIA · {data_pt}", cel, "",
              f"“{ev['versiculo']}”", ev.get("referencia", ""), "",
              "O FATO", ev["fato"].strip()]
    if ev.get("fato_fonte"):
        partes += ["", f"Fonte: {ev['fato_fonte']}"]
    leitura = f"Leitura completa: {ev.get('referencia','')}" + (f" · Leituras do dia: {ev['leituras']}" if ev.get("leituras") else "")
    partes += [leitura, "Índice de fontes no link da bio", "", "· · ·", ""]
    if ev.get("versiculo_en"):
        partes += [f"GOSPEL OF THE DAY · {ev.get('referencia_en') or ev.get('referencia','')}", f"“{ev['versiculo_en']}”"]
    if ev.get("fato_en"):
        partes += ["", ev["fato_en"].strip()]
    partes += ["Sources index in the bio link"]
    return "\n".join(partes).strip()


def story_tarde(s):
    en = f'<div class="s-text_en">{esc(s["texto_en"])}</div>' if s.get("texto_en") else ""
    return f"""<div class="page story">
      <div class="s-wrap" style="padding-top:420px"><div class="s-kicker">{esc(s.get('kicker','UM DETALHE A MAIS'))}</div>
        <div class="s-text">{esc(s['texto'])}</div>{en}</div>
      <div class="s-cta">O relato completo está no post de hoje · Full story in today's post</div>
      <div class="s-foot">ACTA DEI · MYSTERIUM FIDEI</div></div>"""


def story_noite(s):
    return f"""<div class="page story">
      <div class="s-wrap" style="padding-top:520px"><div class="s-quote">“{esc(s['citacao'])}”</div>
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
    ev = post.get("evangelho")
    if ev and ev.get("versiculo") and ev.get("fato"):
        htmls.append(("evangelho_01.jpg", evangelho_versiculo(ev, post, pasta), 1350))
        htmls.append(("evangelho_02.jpg", evangelho_fato(ev, post, pasta), 1350))
        (pasta / "legenda_evangelho.txt").write_text(legenda_evangelho(ev, post, pasta)[:2000])
        if not (pasta / "hashtags_evangelho.txt").exists():
            (pasta / "hashtags_evangelho.txt").write_text(HASHTAGS_EVANGELHO)
    st = post.get("stories", {})
    if st.get("manha"): htmls.append(("story_manha.jpg", story_manha(st["manha"], pasta, post), 1920))
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
            pg.evaluate("""() => { const v = document.querySelector('.ev-verse'), m = document.querySelector('.ev-main'); if (!v || !m) return;
                let fs = parseFloat(getComputedStyle(v).fontSize);
                while (m.scrollHeight > m.clientHeight + 2 && fs > 40) { fs -= 2; v.style.fontSize = fs + 'px'; } }""")
            pg.evaluate("""() => { const t = document.querySelector('.s-wrap'); if (!t || !t.lastElementChild) return;
                let z = 1.0; const limite = 1920 - 380;
                while (t.lastElementChild.getBoundingClientRect().bottom > limite && z > 0.6) { z -= 0.02; t.style.zoom = z; } }""")
            pg.wait_for_timeout(100)
            pg.screenshot(path=str(pasta / nome), type="jpeg", quality=92)
            pg.close()
        br.close()
    print("gerados:", ", ".join(n for n, _, _ in htmls))
    return [n for n, _, _ in htmls]


if __name__ == "__main__":
    render(sys.argv[1])
