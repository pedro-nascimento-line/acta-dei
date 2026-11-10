#!/usr/bin/env python3
"""Gera o Reel do dia (posts/<dia>/reel.mp4, 1080×1920, 30–45 s) e a legenda do post (legenda_reel.txt).

Uso: python3 scripts/make_reel.py posts/2026-11-07 [--sem-voz] [--sem-musica] [--sem-ia]

Forma: o vídeo transita por IMAGENS (pinturas, fotos de relíquias, santuários) com a frase narrada
escrita na tela como legenda. Cada frase do roteiro vira um slide. Termina com uma frase de impacto
do próprio santo ou sobre o milagre (stories.noite.citacao), sem chamada para o perfil.

Imagens, nesta ordem: as já baixadas para o post (imagem.jpg, santo.jpg); depois o Wikimedia Commons
(mesmo filtro de licença das artes: PD, CC0, CC BY, CC BY-SA); se ainda faltar, ilustrações geradas
por IA (Pollinations, sem chave) com o contexto da frase, sempre creditadas como "ilustração gerada
por IA" na legenda — nunca apresentadas como fotografia.

Roteiro: `post["reel"]` (4 a 5 frases curtas escritas pela tarefa diária) ou, na falta, a primeira
frase de cada card. Narração: edge-tts (pt-BR). Música: posts/_musica (fetch_music.py), em -14 dB.
Sem voz, sem música ou sem IA o vídeo sai do mesmo jeito (o log avisa).
"""
import hashlib, io, json, re, shutil, subprocess, sys, tempfile, urllib.parse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402  (CSS, fontes, data_uri, esc, STATUS)
import commons  # noqa: E402
from av import ff, duracao as dur  # noqa: E402
import requests  # noqa: E402
from PIL import Image  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
VOZ = "pt-BR-AntonioNeural"
W, H, FPS = 1080, 1920, 30
ESCALA = 1.2  # renderiza maior para o zoom não borrar
IA_URL = "https://image.pollinations.ai/prompt/"

CSS_REEL = f"""
.reel {{ width: {W}px; height: {H}px; background: {render.CHAR}; color: {render.CREAM}; position: relative; overflow: hidden; }}
.r-hero {{ position: absolute; inset: 0; }}
.r-hero img.bg {{ position: absolute; inset: -60px; width: calc(100% + 120px); height: calc(100% + 120px); object-fit: cover; filter: blur(30px) brightness(.45); }}
.r-hero img.fg {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: contain; object-position: center 42%; }}
.r-hero img.cv {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: center 28%; }}
.capa .r-hero img.fg {{ object-position: center 58%; }}
.capa .r-hero img.cv {{ object-position: center 40%; }}
.r-shade {{ position: absolute; left: 0; right: 0; bottom: 0; height: 1000px; background: linear-gradient(180deg, rgba(38,34,30,0) 0%, rgba(38,34,30,.55) 40%, rgba(38,34,30,.95) 100%); }}
.r-top {{ position: absolute; left: 0; right: 0; top: 0; height: 700px; background: linear-gradient(180deg, rgba(38,34,30,.88) 0%, rgba(38,34,30,.55) 50%, rgba(38,34,30,0) 100%); }}
/* painel escuro atrás da legenda: o texto é legível sobre qualquer imagem */
.r-cap {{ position: absolute; left: 72px; right: 72px; bottom: 470px; text-align: center; background: rgba(38,34,30,.80);
          padding: 40px 44px 46px; border-radius: 16px; box-shadow: 0 12px 48px rgba(0,0,0,.45); }}
.r-kicker {{ display: inline-block; font-family: 'Cinzel'; font-weight: 700; font-size: 24px; letter-spacing: 5px; color: {render.CREAM}; background: rgba(166,25,46,.92); padding: 12px 20px 10px; border-radius: 6px; margin-bottom: 30px; }}
.r-body {{ font-family: 'Cormorant'; font-size: 58px; line-height: 1.28; font-weight: 600; color: {render.CREAM}; text-shadow: 0 2px 18px rgba(0,0,0,.8); }}
.r-title {{ position: absolute; left: 84px; right: 84px; top: 300px; text-align: center; }}
.r-title h1 {{ font-family: 'Cinzel'; font-weight: 700; font-size: 66px; line-height: 1.12; color: {render.CREAM}; text-shadow: 0 2px 18px rgba(0,0,0,.8); }}
.r-title .sub {{ font-size: 36px; font-style: italic; color: #E6DFD2; margin-top: 16px; text-shadow: 0 2px 12px rgba(0,0,0,.8); }}
.r-badge {{ display: inline-block; font-family: 'Cinzel'; font-weight: 700; font-size: 19px; letter-spacing: 3px; color: {render.CREAM}; background: {render.RED}; padding: 12px 18px 10px; border-radius: 6px; margin-bottom: 26px; }}
.r-quote {{ font-family: 'Cormorant'; font-size: 66px; line-height: 1.25; font-style: italic; font-weight: 600; color: {render.CREAM}; text-shadow: 0 2px 18px rgba(0,0,0,.85); }}
.r-author {{ font-family: 'Cinzel'; font-size: 28px; letter-spacing: 5px; color: #E6DFD2; margin-top: 40px; }}
.r-author::before {{ content: ''; display: block; width: 90px; height: 3px; background: {render.RED}; margin: 0 auto 26px; }}
.r-foot {{ position: absolute; left: 0; right: 0; bottom: 380px; text-align: center; font-family: 'Cinzel'; font-size: 20px; letter-spacing: 6px; color: {render.CREAM}; opacity: .6; }}
.w {{ opacity: 0; transition: none; }}
/* três camadas por slide: base = só a foto (recebe o zoom); ui = degradês, painel, título, kicker, autor, rodapé
   (fixos); legenda = só as palavras (sequência de PNGs transparentes). Assim nada "anda" sob o texto. */
body.base .r-top, body.base .r-shade, body.base .r-title, body.base .r-cap, body.base .r-foot {{ visibility: hidden; }}
html.ui, body.ui, html.legenda, body.legenda {{ background: transparent !important; }}
body.ui .reel, body.legenda .reel {{ background: transparent; }}
body.ui .r-hero {{ visibility: hidden; }}
body.ui .w {{ visibility: hidden; }}
body.legenda .r-hero, body.legenda .r-top, body.legenda .r-shade, body.legenda .r-title, body.legenda .r-foot {{ visibility: hidden; }}
body.legenda .r-kicker, body.legenda .r-author {{ visibility: hidden; }}
body.legenda .r-cap {{ background: transparent; box-shadow: none; }}
body.cover .r-cap, body.cover .r-foot, body.cover .r-top {{ display: none; }}
body.cover .r-shade {{ height: 100%; background: linear-gradient(180deg, rgba(38,34,30,.15) 0%, rgba(38,34,30,.15) 45%, rgba(38,34,30,.88) 75%); }}
body.cover .r-title {{ top: auto; bottom: 560px; }}
body.cover .r-title h1 {{ font-size: 96px; line-height: 1.08; text-shadow: 0 3px 24px rgba(0,0,0,.95); }}
body.cover .r-title .sub {{ font-size: 40px; margin-top: 22px; }}
body.cover .r-title::before {{ content: ''; display: block; width: 140px; height: 5px; background: {render.RED}; margin: 0 auto 34px; }}
body.cover .r-badge {{ font-size: 24px; padding: 14px 22px 12px; margin-bottom: 30px; }}
body.cover .capa .r-hero img.fg {{ object-position: center 35%; }}
"""


# ---------------------------------------------------------------- roteiro
def frases(txt, n=1, max_len=130):
    partes = [p.strip() for p in re.split(r"(?<=[.!?])\s+", (txt or "").replace("\n", " ")) if p.strip()]
    out, acc = [], ""
    for p in partes:
        if not acc:
            acc = p
        elif len(acc) + 1 + len(p) <= max_len:
            acc += " " + p
        else:
            out.append(acc); acc = p
        if len(out) >= n: break
    if acc and len(out) < n: out.append(acc)
    return out[:n]


def roteiro(post):
    """Lista de (kicker, texto): do campo `reel` ou a primeira frase de cada card + decisão."""
    if post.get("reel"):
        return [((i.get("kicker") if isinstance(i, dict) else None), (i.get("texto") if isinstance(i, dict) else i))
                for i in post["reel"] if (i.get("texto") if isinstance(i, dict) else i)]
    out = []
    for c in post.get("cards", [])[:3]:
        k = (c.get("kicker") or "").split("·")[0].strip()
        f = frases(c.get("texto", ""))
        if f: out.append((k, f[0]))
    if post.get("decisao"):
        f = frases(post["decisao"])
        if f: out.append(("O QUE A SANTA IGREJA CATÓLICA DECIDIU", f[0]))
    return out[:5]


def citacao_final(post):
    n = (post.get("stories") or {}).get("noite") or {}
    if n.get("citacao"):
        return n["citacao"].strip(" “”\""), (n.get("autor") or "").strip()
    return None, None


# ---------------------------------------------------------------- imagens
def _md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def _salvar(img_bytes, destino):
    im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    if min(im.size) < 500:
        raise ValueError(f"imagem pequena: {im.size}")
    im.thumbnail((1600, 1600))
    im.save(destino, "JPEG", quality=88, optimize=True)


def imagens_commons(post, pasta, faltam, ja_titulos):
    termos = []
    for spec in (post, (post.get("stories") or {}).get("manha") or {}):
        w = (spec.get("imagem_wikipedia") or "").split(":", 1)[-1]
        if w: termos.append(w)
    b = post.get("imagem_busca") or []
    termos += b if isinstance(b, list) else [b]
    termos.append(post.get("titulo", ""))
    out, vistos = [], set(ja_titulos)
    for termo in [t for t in termos if t]:
        if len(out) >= faltam: break
        try:
            cands = commons.search(termo, n=12)
        except Exception as e:
            print(f"  busca '{termo}' falhou: {e}"); continue
        for i in cands:
            if len(out) >= faltam: break
            if not i["licenca_ok"] or i["title"] in vistos: continue
            if re.search(r"(map|mapa|coat of arms|bras[aã]o|flag|bandeira|logo|seal|stamp|selo|diagram|plan\b)", i["title"], re.I): continue
            destino = pasta / f"reel_img_{len(ja_titulos) + len(out) + 1:02d}.jpg"
            try:
                _salvar(commons._req(i["url"]).content, destino)
            except Exception as e:
                print(f"  descartada {i['title'][:50]}: {e}"); continue
            vistos.add(i["title"])
            out.append({"arquivo": destino.name, "title": i["title"], "licenca": i["licenca"], "autor": i["autor"], "pagina": i["pagina"], "origem": "commons"})
            print(f"  + commons: {i['title'][:60]} · {i['licenca']}")
    return out


def imagem_ia(prompt, destino, seed):
    url = IA_URL + urllib.parse.quote(prompt[:600]) + f"?width=1080&height=1920&nologo=true&seed={seed}&model=flux"
    r = requests.get(url, headers={"User-Agent": commons.UA}, timeout=180)
    r.raise_for_status()
    _salvar(r.content, destino)


def prompt_ia(post, texto):
    tema = post.get("titulo_en") or post.get("titulo", "")
    return (f"Oil painting in the manner of the Old Masters, Catholic sacred art, {tema}. Scene: {texto}. "
            f"Solemn, reverent, dramatic chiaroscuro, warm candlelight, muted palette. No text, no letters, no watermark, no modern objects.")


def montar_imagens(post, pasta, slides, sem_ia):
    """Uma imagem por slide. Devolve lista de dicts com arquivo + crédito (ordem dos slides)."""
    n = len(slides)
    lista, md5s = [], set()
    cred_principal = post.get("imagem_credito", "")
    for nome, cred in ((post.get("imagem"), cred_principal), (((post.get("stories") or {}).get("manha") or {}).get("imagem"), "Wikimedia Commons")):
        if nome and (pasta / nome).exists():
            h = _md5(pasta / nome)
            if h not in md5s:
                md5s.add(h); lista.append({"arquivo": nome, "credito": cred, "origem": "post"})
    # reaproveita imagens de execuções anteriores (reel_imagens.json)
    idx = pasta / "reel_imagens.json"
    if idx.exists():
        for e in json.loads(idx.read_text()):
            if (pasta / e["arquivo"]).exists() and _md5(pasta / e["arquivo"]) not in md5s and len(lista) < n:
                md5s.add(_md5(pasta / e["arquivo"])); lista.append(e)
    if len(lista) < n:
        ja = [e.get("title") for e in lista if e.get("title")]
        for e in imagens_commons(post, pasta, n - len(lista), ja):
            h = _md5(pasta / e["arquivo"])
            if h in md5s:
                (pasta / e["arquivo"]).unlink(missing_ok=True); continue
            md5s.add(h); e["credito"] = f"{(e['autor'] or '').strip()[:40] + ' · ' if e['autor'] else ''}Wikimedia Commons · {e['licenca']}"
            lista.append(e)
    if len(lista) < n and not sem_ia:
        for k, (_, texto) in enumerate(slides):
            if len(lista) >= n: break
            destino = pasta / f"reel_ia_{len(lista) + 1:02d}.jpg"
            try:
                imagem_ia(prompt_ia(post, texto), destino, seed=1000 + k)
                lista.append({"arquivo": destino.name, "credito": "Ilustração gerada por IA", "origem": "ia"})
                print(f"  + IA: {destino.name} ← {texto[:50]}")
            except Exception as e:
                print(f"  IA falhou ({texto[:40]}): {e}")
    idx.write_text(json.dumps([e for e in lista if e.get("origem") != "post"], ensure_ascii=False, indent=2))
    if not lista:
        lista = [{"arquivo": None, "credito": "", "origem": "selo"}]
    # distribui: uma por slide, repetindo em ciclo se faltar
    return [lista[i % len(lista)] for i in range(n)]


# ---------------------------------------------------------------- slides
def hero_html(pasta, e):
    if not e.get("arquivo"):
        return f'<img class="fg" src="{render.SELO}" style="padding:200px">'
    p = pasta / e["arquivo"]
    uri = render.data_uri(p)
    with Image.open(p) as im:
        w, h = im.size
    if w / h > 1.05:   # paisagem: inteira sobre fundo desfocado
        return f'<img class="bg" src="{uri}"><img class="fg" src="{uri}">'
    return f'<img class="cv" src="{uri}">'


def palavras_html(texto, classe, aspas=False):
    ws = texto.split()
    spans = " ".join(f'<span class="w" data-i="{i}">{render.esc(w)}</span>' for i, w in enumerate(ws))
    if aspas:
        spans = f'<span class="w" data-i="0">“</span>{spans}<span class="w" data-i="{len(ws) - 1}">”</span>'
    return f'<div class="{classe}">{spans}</div>'


def slide(pasta, e, corpo, topo=""):
    return f"""<div class="reel{' capa' if topo else ''}"><div class="r-hero">{hero_html(pasta, e)}</div><div class="r-top"></div><div class="r-shade"></div>
      {topo}<div class="r-cap">{corpo}</div><div class="r-foot">ACTA DEI · MYSTERIUM FIDEI</div></div>"""


AJUSTE_JS = """() => { for (const sel of ['.r-body', '.r-quote']) { const t = document.querySelector(sel); if (!t) continue;
    let fs = parseFloat(getComputedStyle(t).fontSize); while (t.getBoundingClientRect().height > 560 && fs > 34) { fs -= 2; t.style.fontSize = fs + 'px'; } } }"""


def renderizar_slide(br, body, tmp, i, tempos, passos=3, passo_s=0.07):
    """Gera três camadas: o PNG base (só a foto, que recebe o zoom), o PNG da interface (degradês, painel da
    legenda, título, kicker, autor, rodapé — fixo) e a sequência de PNGs transparentes das palavras, uma por
    estado (cada palavra surge em `passos` degraus de opacidade). Devolve (base, ui, [(png, duração)])."""
    html = f"<html><head><style>{render.CSS}{CSS_REEL}</style></head><body style='margin:0'>{body}</body></html>"
    pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=ESCALA)
    pg.set_content(html); pg.wait_for_timeout(150); pg.evaluate(AJUSTE_JS)
    pg.evaluate("() => document.body.classList.add('base')")
    base = tmp / f"slide_{i:02d}.png"
    pg.screenshot(path=str(base)); pg.close()
    # interface fixa (escala 1 = tamanho do vídeo final)
    pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    pg.set_content(html); pg.wait_for_timeout(150); pg.evaluate(AJUSTE_JS)
    pg.evaluate("() => { document.documentElement.classList.add('ui'); document.body.classList.add('ui'); }")
    ui = tmp / f"ui_{i:02d}.png"
    pg.screenshot(path=str(ui), omit_background=True); pg.close()
    # legenda (escala 1)
    pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    pg.set_content(html); pg.wait_for_timeout(150); pg.evaluate(AJUSTE_JS)
    pg.evaluate("() => { document.documentElement.classList.add('legenda'); document.body.classList.add('legenda'); }")
    n = pg.evaluate("() => { const s = new Set(); document.querySelectorAll('.w').forEach(e => s.add(e.dataset.i)); return s.size; }")
    seq, t_ant = [], 0.0
    estados = []  # (instante, índice da palavra, opacidade)
    for k in range(n):
        t0 = tempos[k] if k < len(tempos) else (tempos[-1] + 0.3 if tempos else 0.3 * k)
        for q in range(1, passos + 1):
            estados.append((t0 + (q - 1) * passo_s, k, q / passos))
    estados.sort()
    # primeiro quadro: nada visível, dura até a primeira palavra
    vazio = tmp / f"cap_{i:02d}_000.png"
    pg.screenshot(path=str(vazio), omit_background=True)
    seq.append([vazio, max(estados[0][0], 0.05) if estados else 1.0])
    for j, (t, k, op) in enumerate(estados):
        pg.evaluate("([k, op]) => document.querySelectorAll(`.w[data-i='${k}']`).forEach(e => e.style.opacity = op)", [k, op])
        png = tmp / f"cap_{i:02d}_{j + 1:03d}.png"
        pg.screenshot(path=str(png), omit_background=True)
        prox = estados[j + 1][0] if j + 1 < len(estados) else t + 1.0
        seq.append([png, max(prox - t, 0.03)])
    pg.close()
    return base, ui, seq


def gerar_capa(br, html, destino):
    """Imagem de capa do Reel (1080×1920): a imagem da capa com o título no centro, sem legenda.
    A Meta recorta o centro para a miniatura do feed, por isso o título fica no meio."""
    pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    pg.set_content(html); pg.wait_for_timeout(150)
    pg.evaluate("() => document.body.classList.add('base', 'cover')")
    pg.screenshot(path=str(destino), type="jpeg", quality=90); pg.close()


# ---------------------------------------------------------------- áudio
def narrar(texto, destino):
    """edge-tts pela API: grava o mp3 e devolve a lista de instantes (s) em que cada palavra começa.
    Devolve None se a voz falhar."""
    try:
        import asyncio, edge_tts

        async def _run():
            com = edge_tts.Communicate(texto, VOZ, rate="-6%")
            marcas = []
            with open(destino, "wb") as f:
                async for ch in com.stream():
                    if ch["type"] == "audio":
                        f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        marcas.append(ch["offset"] / 1e7)
            return marcas
        marcas = asyncio.run(_run())
        if not destino.exists() or destino.stat().st_size < 1000:
            print("  narração falhou: áudio vazio"); return None
        return marcas
    except Exception as e:
        print(f"  narração falhou: {str(e)[:200]}")
        return None


def tempos_palavras(marcas, n_palavras, inicio, dur_total):
    """Mapeia as marcas da voz (M) nas palavras exibidas (N) por posição; sem marcas, ritmo uniforme."""
    if marcas and n_palavras:
        M = len(marcas)
        if M == n_palavras:
            return [inicio + m for m in marcas]
        return [inicio + marcas[min(M - 1, round(k * (M - 1) / max(n_palavras - 1, 1)))] for k in range(n_palavras)]
    passo = dur_total / max(n_palavras, 1)
    return [inicio + k * passo for k in range(n_palavras)]


def musica(dia):
    idx = RAIZ / "posts/_musica/musica.json"
    if not idx.exists():
        return None
    est = [e for e in json.loads(idx.read_text()) if (RAIZ / "posts/_musica" / e["arquivo"]).exists()]
    if not est:
        return None
    n = sum(int(c) for c in re.sub(r"\D", "", dia))  # escolha estável por dia
    e = est[n % len(est)]
    return RAIZ / "posts/_musica" / e["arquivo"], e


# ---------------------------------------------------------------- legenda do post
def legenda_reel(post, itens, cit, autor, creditos):
    st = render.STATUS.get(post.get("status") or "")
    linhas = [post["titulo"].upper()]
    if st: linhas.append(f"■ {st[0]}")
    if post.get("subtitulo"): linhas.append(post["subtitulo"])
    linhas.append("")
    linhas += [t for _, t in itens]
    if cit:
        linhas += ["", f"“{cit}”", f"— {autor}" if autor else ""]
    linhas += ["", "Fontes e relato completo no índice do link da bio."]
    if post.get("titulo_en"):
        linhas += ["", "· · ·", "", post["titulo_en"], "Sources in the link in bio."]
    if creditos:
        linhas += ["", "Imagens: " + "; ".join(creditos)]
    return "\n".join(l for l in linhas if l is not None)


# ---------------------------------------------------------------- principal
def main(pasta, sem_voz=False, sem_musica=False, sem_ia=False):
    pasta = Path(pasta)
    post = json.loads((pasta / "post.json").read_text())
    itens = roteiro(post)
    if not itens:
        sys.exit("post sem texto para o reel")
    cit, autor = citacao_final(post)
    # slides: capa (título + gancho) · frases · citação final
    slides = [("", itens[0][1])] + [(k or "", t) for k, t in itens[1:]]
    if cit:
        slides.append(("CITACAO", cit))
    imgs = montar_imagens(post, pasta, slides, sem_ia)
    st = render.STATUS.get(post.get("status") or "")
    tmp = Path(tempfile.mkdtemp(prefix="reel_"))
    # cada slide: html, partes da narração [(texto, mostra_legenda)]
    plano = []
    for i, ((k, t), e) in enumerate(zip(slides, imgs)):
        if i == 0:
            badge = f'<div class="r-badge">{st[0]}</div>' if st else ('<div class="r-badge">SANTO DO DIA</div>' if post.get("tipo") == "santo" else "")
            topo = f'<div class="r-title">{badge}<h1>{render.esc(post["titulo"])}</h1><div class="sub">{render.esc(post.get("subtitulo", ""))}</div></div>'
            plano.append((slide(pasta, e, palavras_html(t, "r-body"), topo), [(post["titulo"] + ".", False), (t, True)]))
        elif k == "CITACAO":
            corpo = palavras_html(t, "r-quote", aspas=True) + f'<div class="r-author">{render.esc(autor)}</div>'
            partes = [(t, True)] + ([(autor.replace("·", ","), False)] if autor else [])
            plano.append((slide(pasta, e, corpo), partes))
        else:
            kick = f'<div class="r-kicker">{render.esc(k)}</div>' if k else ""
            plano.append((slide(pasta, e, kick + palavras_html(t, "r-body")), [(t, True)]))

    ATRASO = 0.45  # silêncio antes da voz em cada slide
    # fase 1: narração (fora do Playwright, que mantém seu próprio loop de eventos)
    narr = []
    for i, (html, partes) in enumerate(plano):
        audios, t_cursor, tempos, com_voz = [], ATRASO, [], not sem_voz
        for j, (texto, mostra) in enumerate(partes):
            voz = tmp / f"voz_{i:02d}_{j}.mp3"
            marcas = narrar(texto, voz) if com_voz else None
            if marcas is None:
                com_voz = False
                d_parte = max(2.0, 0.07 * len(texto))
            else:
                d_parte = dur(voz)
                audios.append(voz)
            if mostra:
                tempos = tempos_palavras(marcas, len(texto.split()), t_cursor, d_parte)
            t_cursor += d_parte + 0.35
        narr.append((audios, tempos, com_voz, t_cursor))
    # fase 2: quadros e montagem
    from playwright.sync_api import sync_playwright
    segs, total = [], 0.0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        html_capa = f"<html><head><style>{render.CSS}{CSS_REEL}</style></head><body style='margin:0'>{plano[0][0]}</body></html>"
        gerar_capa(br, html_capa, pasta / "reel_capa.jpg")
        for i, (html, partes) in enumerate(plano):
            audios, tempos, com_voz, t_cursor = narr[i]
            d = max(3.0, t_cursor + 0.6)
            base, ui, seq = renderizar_slide(br, html, tmp, i, tempos)
            # fecha a sequência da legenda exatamente na duração do slide
            soma = sum(x[1] for x in seq)
            if soma < d:
                seq[-1][1] += d - soma
            lista_cap = tmp / f"caps_{i:02d}.txt"
            lista_cap.write_text("".join(f"file '{png}'\nduration {du:.3f}\n" for png, du in seq) + f"file '{seq[-1][0]}'\n")
            frames = int(round(d * FPS))
            z = "min(zoom+0.0006,1.09)" if i % 2 == 0 else "if(eq(on,1),1.09,max(zoom-0.0006,1.0))"
            zoom = f"zoompan=z='{z}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}"
            # entradas: 0 = foto (zoom), 1 = interface fixa, 2 = sequência das palavras, 3 = áudio
            vf = (f"[0:v]{zoom}[zb];[1:v]format=rgba[ui];[zb][ui]overlay=0:0[zu];[2:v]format=rgba,fps={FPS}[cap];"
                  f"[zu][cap]overlay=0:0:shortest=1,fade=t=in:st=0:d=0.4,fade=t=out:st={d-0.4:.2f}:d=0.4,format=yuv420p[v]")
            seg = tmp / f"seg_{i:02d}.mp4"
            entradas = ["-loop", "1", "-framerate", FPS, "-i", base, "-loop", "1", "-framerate", FPS, "-i", ui,
                        "-f", "concat", "-safe", "0", "-i", lista_cap]
            if com_voz and audios:
                lista_voz = tmp / f"vozes_{i:02d}.txt"
                lista_voz.write_text("".join(f"file '{a}'\n" for a in audios))
                voz_i = tmp / f"voz_{i:02d}.mp3"
                ff("-f", "concat", "-safe", "0", "-i", lista_voz, "-c", "copy", voz_i)
                ff(*entradas, "-i", voz_i,
                   "-filter_complex", f"{vf};[3:a]adelay={int(ATRASO*1000)}|{int(ATRASO*1000)},apad[a]", "-map", "[v]", "-map", "[a]",
                   "-t", f"{d:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", seg)
            else:
                ff(*entradas, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                   "-filter_complex", vf, "-map", "[v]", "-map", "3:a",
                   "-t", f"{d:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", seg)
            segs.append(seg); total += d
            print(f"  slide {i}: {d:.1f}s {'voz' if com_voz else 'sem voz'} · {imgs[i].get('arquivo') or 'selo'} · {len(seq)} quadros de legenda · {partes[0][0][:40]}")
        br.close()
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{s_}'\n" for s_ in segs))
    concat = tmp / "concat.mp4"
    ff("-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", concat)
    saida = pasta / "reel.mp4"
    m = None if sem_musica else musica(pasta.name)
    creditos, vistos = [], set()
    for e in imgs:
        c = e.get("credito") or ""
        if c and c not in vistos:
            vistos.add(c); creditos.append(c)
    if m:
        arq, e = m
        ini = 0 if e["segundos"] <= total + 5 else (sum(int(c) for c in re.sub(r"\D", "", pasta.name)) * 7) % int(e["segundos"] - total - 3)
        ff("-i", concat, "-ss", ini, "-i", arq,
           "-filter_complex", f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.2,afade=t=in:d=2,atrim=0:{total:.2f},afade=t=out:st={max(total-3,0):.2f}:d=3[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.95[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", saida)
        print(f"  música: {e['title'][:60]} · {e['licenca']}")
        creditos.append(f"Música: {e['title'].replace('File:', '')[:70]} · Wikimedia Commons · {e['licenca']}")
    else:
        ff("-i", concat, "-c", "copy", "-movflags", "+faststart", saida)
        print("  sem música (estante vazia: rode scripts/fetch_music.py)")
    (pasta / "legenda_reel.txt").write_text(legenda_reel(post, itens, cit, autor, creditos) + "\n")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"reel.mp4: {total:.1f}s, {saida.stat().st_size // 1000} kB, {len(segs)} slides")


if __name__ == "__main__":
    main(sys.argv[1], sem_voz="--sem-voz" in sys.argv, sem_musica="--sem-musica" in sys.argv, sem_ia="--sem-ia" in sys.argv)
