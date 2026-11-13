#!/usr/bin/env python3
"""Regenera index.html (GitHub Pages, link da bio): todos os posts com fontes clicáveis e status."""
import csv, html, json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
STATUS = {"reconhecido": "Reconhecido pela Santa Igreja Católica", "investigacao": "Em investigação pela Santa Igreja Católica"}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap');
:root{--red:#A6192E;--cream:#F7F2E8;--char:#26221E;--grey:#6B655E}
*{box-sizing:border-box}body{margin:0;background:var(--cream);color:var(--char);font-family:'Cormorant Garamond',Georgia,serif;font-size:20px;line-height:1.5}
header{text-align:center;padding:48px 16px 24px}header img{width:140px}header h1{font-family:Cinzel,serif;letter-spacing:4px;font-size:28px;margin:16px 0 4px}
header p{margin:0;color:var(--grey);font-style:italic}
main{max-width:860px;margin:0 auto;padding:16px}
article{border-top:2px solid var(--red);padding:24px 0}
article h2{font-family:Cinzel,serif;font-size:22px;margin:0 0 4px}
.meta{color:var(--grey);font-size:17px}.badge{display:inline-block;background:var(--red);color:var(--cream);font-family:Cinzel,serif;font-size:12px;letter-spacing:2px;padding:4px 10px;border-radius:4px;margin-left:8px;vertical-align:middle}
.cards{display:flex;gap:8px;overflow-x:auto;margin:14px 0}.cards img{height:160px;border:1px solid #d9d0bf}
ul{margin:8px 0 0;padding-left:20px}ul li{margin:2px 0}
footer{text-align:center;color:var(--grey);font-size:16px;padding:40px 16px}
a{color:var(--red)}
"""


def main():
    posts = []
    for pasta in sorted((RAIZ / "posts").glob("????-??-??"), reverse=True):
        pj = pasta / "post.json"
        if not pj.exists():
            continue
        p = json.loads(pj.read_text())
        meta = json.loads((pasta / "meta.json").read_text()) if (pasta / "meta.json").exists() else {}
        posts.append((pasta.name, p, meta))

    itens = []
    for dia, p, meta in posts:
        cards = "".join(f'<img src="posts/{dia}/{c.name}" alt="">' for c in sorted((RAIZ / "posts" / dia).glob("card_*.jpg")))
        fontes = "".join(f"<li>{html.escape(f)}</li>" for f in p.get("fontes", []))
        badge = f'<span class="badge">{STATUS[p["status"]]}</span>' if p.get("status") in STATUS else ""
        link = f' · <a href="https://www.instagram.com/p/{meta["feed_shortcode"]}/">ver no Instagram</a>' if meta.get("feed_shortcode") else ""
        itens.append(f"""<article><h2>{html.escape(p['titulo'])}{badge}</h2>
<div class="meta">{dia} · {html.escape(p.get('subtitulo',''))}{link}</div>
<div class="cards">{cards}</div>
<div><strong>Fontes</strong><ul>{fontes}</ul></div>
<div class="meta">{html.escape(p.get('imagem_credito',''))}</div></article>""")

    n_ok = 0
    logp = RAIZ / "log/publicacoes.csv"
    if logp.exists():
        n_ok = sum(1 for r in csv.DictReader(open(logp)) if r.get("tipo") == "carrossel" and r.get("status") == "ok")

    doc = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Acta Dei · Mysterium Fidei — índice de fontes</title><style>{CSS}</style></head><body>
<header><img src="brand/logo_avatar_claro_1080.png" alt="Acta Dei"><h1>ACTA DEI</h1><p>Mysterium Fidei · Milagres reconhecidos pela Santa Igreja Católica, com data, lugar e testemunhas · {len(posts)} registros</p></header>
<main>{''.join(itens) or '<p style="text-align:center;color:var(--grey)">Os primeiros registros entram em breve.</p>'}</main>
<footer>Cada registro cita as fontes oficiais consultadas. Imagens de domínio público ou Creative Commons (Wikimedia Commons), com crédito. · @actadei.oficial</footer>
</body></html>"""
    (RAIZ / "index.html").write_text(doc)
    print(f"index.html: {len(posts)} posts, {n_ok} publicados")


if __name__ == "__main__":
    main()
