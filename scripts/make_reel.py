#!/usr/bin/env python3
"""Gera o Reel do dia (posts/<dia>/reel.mp4, 1080×1920, 30–45 s) e a legenda do post (legenda_reel.txt).

Uso: python3 scripts/make_reel.py posts/2026-11-07 [--sem-voz] [--sem-musica] [--sem-ia]

Forma: o vídeo transita por IMAGENS (pinturas, fotos de relíquias, santuários) com a frase narrada
escrita na tela como legenda. Cada frase do roteiro vira um slide. Termina com uma frase de impacto
do próprio santo ou sobre o milagre (stories.noite.citacao), sem chamada para o perfil.

Legenda: um bloco só (painel escuro + texto inteiro), pequeno e junto à base, que surge em fade
(transparente → cheio) no instante em que a voz começa a ler aquele texto. No primeiro slide a tela
fica limpa — só a imagem e o título — até o título terminar de ser lido. Nada de palavra a palavra.

Imagens: uma por cena, sempre do TEMA. Slide 0 = imagem principal do post. Os demais vêm do garimpo no
Wikimedia Commons (imagens_tema.py: arquivos e categorias indicados pela tarefa, categoria do artigo no
Wikidata, imagens dos artigos da Wikipédia, busca por frase exata), escolhidos pelo termo `imagem` de cada
item do roteiro, com o mesmo filtro de licença das artes (PD, CC0, CC BY, CC BY-SA). Cena sem imagem
relevante: ilustração daquela cena por IA (Pollinations), creditada como "Ilustração gerada por IA" —
nunca apresentada como fotografia. O santo do dia só entra quando o post é sobre ele.

Roteiro: `post["reel"]` (4 a 5 frases curtas escritas pela tarefa diária) ou, na falta, a primeira
frase de cada card. Narração: edge-tts (pt-BR). Música: 5 cantos gregorianos de posts/_musica (fetch_music.py), um por dia, em volume baixo.
Sem voz, sem música ou sem IA o vídeo sai do mesmo jeito (o log avisa).
"""
import hashlib, io, json, re, shutil, subprocess, sys, tempfile, urllib.parse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402  (CSS, fontes, data_uri, esc, STATUS)
import commons  # noqa: E402
import imagens_tema  # noqa: E402
from av import ff, duracao as dur, VETO_MUSICA  # noqa: E402
import requests  # noqa: E402
from PIL import Image  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
VOZ = "pt-BR-AntonioNeural"
W, H, FPS = 1080, 1920, 30
ESCALA = 1.2  # renderiza maior para o zoom não borrar
FADE_LEG = 0.7  # segundos que a legenda leva para ir de transparente a cheia
IA_URL = "https://image.pollinations.ai/prompt/"

CSS_REEL = f"""
.reel {{ width: {W}px; height: {H}px; background: {render.CHAR}; color: {render.CREAM}; position: relative; overflow: hidden; }}
.r-hero {{ position: absolute; inset: 0; }}
.r-hero img.bg {{ position: absolute; inset: -60px; width: calc(100% + 120px); height: calc(100% + 120px); object-fit: cover; filter: blur(30px) brightness(.45); }}
.r-hero img.fg {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: contain; object-position: center 42%; }}
.r-hero img.cv {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: center 28%; }}
.capa .r-hero img.fg {{ object-position: center 56%; }}
.capa .r-hero img.cv {{ object-position: center 40%; }}
.r-shade {{ position: absolute; left: 0; right: 0; bottom: 0; height: 760px; background: linear-gradient(180deg, rgba(38,34,30,0) 0%, rgba(38,34,30,.30) 45%, rgba(38,34,30,.82) 100%); }}
.r-top {{ position: absolute; left: 0; right: 0; top: 0; height: 700px; background: linear-gradient(180deg, rgba(38,34,30,.88) 0%, rgba(38,34,30,.55) 50%, rgba(38,34,30,0) 100%); }}
.reel:not(.capa) .r-top {{ display: none; }}   /* sem título, a imagem fica inteira no alto */
/* legenda: painel escuro pequeno, junto à base (acima da faixa que a interface do Instagram cobre) */
.r-cap {{ position: absolute; left: 72px; right: 72px; bottom: 380px; text-align: center; background: rgba(38,34,30,.80);
          padding: 28px 40px 32px; border-radius: 14px; box-shadow: 0 10px 40px rgba(0,0,0,.45); }}
.r-kicker {{ display: inline-block; font-family: 'Cinzel'; font-weight: 700; font-size: 20px; letter-spacing: 4px; color: {render.CREAM}; background: rgba(166,25,46,.92); padding: 9px 16px 7px; border-radius: 5px; margin-bottom: 18px; }}
.r-body {{ font-family: 'Cormorant'; font-size: 46px; line-height: 1.26; font-weight: 600; color: {render.CREAM}; }}
.r-title {{ position: absolute; left: 84px; right: 84px; top: 250px; text-align: center; }}
.r-title h1 {{ font-family: 'Cinzel'; font-weight: 700; font-size: 66px; line-height: 1.12; color: {render.CREAM}; text-shadow: 0 2px 18px rgba(0,0,0,.8); }}
.r-title .sub {{ font-size: 36px; font-style: italic; color: #E6DFD2; margin-top: 16px; text-shadow: 0 2px 12px rgba(0,0,0,.8); }}
.r-badge {{ display: inline-block; font-family: 'Cinzel'; font-weight: 700; font-size: 19px; letter-spacing: 3px; color: {render.CREAM}; background: {render.RED}; padding: 12px 18px 10px; border-radius: 6px; margin-bottom: 26px; }}
.r-quote {{ font-family: 'Cormorant'; font-size: 50px; line-height: 1.24; font-style: italic; font-weight: 600; color: {render.CREAM}; }}
.r-author {{ font-family: 'Cinzel'; font-size: 23px; letter-spacing: 4px; line-height: 1.45; color: #E6DFD2; margin-top: 24px; }}
.r-author::before {{ content: ''; display: block; width: 80px; height: 3px; background: {render.RED}; margin: 0 auto 18px; }}
/* três camadas por slide: base = só a foto (recebe o zoom); ui = degradês e título (fixos, desde o início);
   legenda = painel + kicker + texto + autor (um PNG transparente que entra em fade quando a voz começa). */
body.base .r-top, body.base .r-shade, body.base .r-title, body.base .r-cap {{ visibility: hidden; }}
html.ui, body.ui, html.legenda, body.legenda {{ background: transparent !important; }}
body.ui .reel, body.legenda .reel {{ background: transparent; }}
body.ui .r-hero, body.ui .r-cap {{ visibility: hidden; }}
body.legenda .r-hero, body.legenda .r-top, body.legenda .r-shade, body.legenda .r-title {{ visibility: hidden; }}
body.cover .r-cap, body.cover .r-top {{ display: none; }}
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


def imagem_ia(prompt, destino, seed):
    url = IA_URL + urllib.parse.quote(prompt[:600]) + f"?width=1080&height=1920&nologo=true&seed={seed}&model=flux"
    r = requests.get(url, headers={"User-Agent": commons.UA}, timeout=180)
    r.raise_for_status()
    _salvar(r.content, destino)


def prompt_ia(post, texto):
    tema = post.get("titulo_en") or post.get("titulo", "")
    return (f"Oil painting in the manner of the Old Masters, Catholic sacred art, {tema}. Scene: {texto}. "
            f"Solemn, reverent, dramatic chiaroscuro, warm candlelight, muted palette. No text, no letters, no watermark, no modern objects.")


def termos_cenas(post, slides):
    """Termo de imagem de cada slide: `reel[i].imagem` escrito pela tarefa diária (ex.: "Sacre Particole");
    a citação final usa `imagens_reel.citacao`, se houver."""
    reel = [i for i in (post.get("reel") or []) if (i.get("texto") if isinstance(i, dict) else i)]
    out = []
    for k, (kick, _) in enumerate(slides):
        if kick == "CITACAO":
            out.append((post.get("imagens_reel") or {}).get("citacao", ""))
        else:
            it = reel[k] if k < len(reel) else None
            out.append(it.get("imagem", "") if isinstance(it, dict) else "")
    return out


def _credito_commons(i):
    autor = re.sub(r"\s+", " ", (i.get("autor") or "").replace("Creator:", "")).strip()[:40]
    return f"{autor + ' · ' if autor else ''}Wikimedia Commons · {i['licenca']}"


def montar_imagens(post, pasta, slides, sem_ia):
    """Uma imagem POR CENA, ligada ao tema. Slide 0 = imagem principal do post; os outros = garimpo no Commons
    (imagens_tema.py) pela cena; sem nada relevante, ilustração da cena por IA (creditada). Nunca o santo do dia
    num post de milagre, nem foto católica genérica."""
    n = len(slides)
    termos = termos_cenas(post, slides)
    escolha, md5s = [None] * n, set()

    def usar(k, e):
        h = _md5(pasta / e["arquivo"])
        if h in md5s:
            return False
        md5s.add(h); escolha[k] = e
        return True

    if post.get("imagem") and (pasta / post["imagem"]).exists():
        usar(0, {"arquivo": post["imagem"], "credito": post.get("imagem_credito", ""), "origem": "post"})
    # reaproveita o que já foi escolhido para esta cena numa geração anterior (só do formato novo, com "cena")
    idx = pasta / "reel_imagens.json"
    if idx.exists():
        try:
            for e in json.loads(idx.read_text()):
                k = e.get("cena")
                if isinstance(k, int) and k < n and escolha[k] is None and (pasta / e["arquivo"]).exists() \
                        and e.get("termo", "") == termos[k]:
                    usar(k, e)
        except Exception as ex:
            print(f"  reel_imagens.json ignorado: {ex}")
    faltam = [k for k in range(n) if escolha[k] is None]
    if faltam:
        extras = []
        manha = (post.get("stories") or {}).get("manha") or {}
        if post.get("tipo") == "santo" and manha.get("imagem") and (pasta / manha["imagem"]).exists():
            extras.append({"arquivo": manha["imagem"], "credito": "Wikimedia Commons", "origem": "post"})
        try:
            cands = imagens_tema.coletar(post, termos)
        except Exception as ex:
            print(f"  garimpo no Commons falhou: {ex}"); cands = []
        usados = set()
        for k in faltam:
            if extras and usar(k, extras[0]):
                extras.pop(0); continue
            for i in imagens_tema.ordenar_para_cena(cands, termos[k], usados)[:6]:
                usados.add(i["title"])
                destino = pasta / f"reel_img_{k:02d}.jpg"
                try:
                    _salvar(commons._req(i["url"]).content, destino)
                except Exception as ex:
                    print(f"  descartada {i['title'][:50]}: {ex}"); continue
                if usar(k, {"arquivo": destino.name, "title": i["title"], "licenca": i["licenca"], "autor": i["autor"],
                            "pagina": i["pagina"], "credito": _credito_commons(i), "origem": "commons",
                            "cena": k, "termo": termos[k]}):
                    print(f"  cena {k}: {i['title'][5:70]} · {i['licenca']} (nota {i['nota']:.0f})")
                    break
    for k in [k for k in range(n) if escolha[k] is None]:
        if sem_ia: break
        kick, texto = slides[k]
        destino = pasta / f"reel_ia_{k:02d}.jpg"
        try:
            imagem_ia(prompt_ia(post, f"{termos[k]}. {texto}" if termos[k] else texto), destino, seed=1000 + k)
            escolha[k] = {"arquivo": destino.name, "credito": "Ilustração gerada por IA", "origem": "ia", "cena": k, "termo": termos[k]}
            print(f"  cena {k}: IA ← {texto[:50]}")
        except Exception as ex:
            print(f"  IA falhou ({texto[:40]}): {ex}")
    idx.write_text(json.dumps([e for e in escolha if e and e.get("origem") != "post"], ensure_ascii=False, indent=2))
    boas = [e for e in escolha if e]
    if not boas:
        return [{"arquivo": None, "credito": "", "origem": "selo"}] * n
    # cena sem imagem: repete uma das imagens DO TEMA (nunca uma genérica)
    return [e or boas[k % len(boas)] for k, e in enumerate(escolha)]


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


def texto_html(texto, classe, aspas=False):
    t = render.esc(texto)
    return f'<div class="{classe}">{"“" + t + "”" if aspas else t}</div>'


def slide(pasta, e, corpo, topo=""):
    return f"""<div class="reel{' capa' if topo else ''}"><div class="r-hero">{hero_html(pasta, e)}</div><div class="r-top"></div><div class="r-shade"></div>
      {topo}<div class="r-cap">{corpo}</div></div>"""


# a legenda nunca passa de ~5 linhas: se passar, a fonte encolhe (mínimo 34 px)
AJUSTE_JS = """() => { for (const sel of ['.r-body', '.r-quote']) { const t = document.querySelector(sel); if (!t) continue;
    let fs = parseFloat(getComputedStyle(t).fontSize); while (t.getBoundingClientRect().height > 300 && fs > 34) { fs -= 2; t.style.fontSize = fs + 'px'; } } }"""


def renderizar_slide(br, body, tmp, i):
    """Gera as três camadas do slide: base (só a foto, que recebe o zoom), ui (degradês e título, fixos)
    e legenda (painel + texto inteiro, PNG transparente que o ffmpeg faz surgir em fade). Devolve (base, ui, cap)."""
    html = f"<html><head><style>{render.CSS}{CSS_REEL}</style></head><body style='margin:0'>{body}</body></html>"
    saidas = []
    for modo, escala in (("base", ESCALA), ("ui", 1), ("legenda", 1)):
        pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=escala)
        pg.set_content(html); pg.wait_for_timeout(150); pg.evaluate(AJUSTE_JS)
        pg.evaluate("(m) => { document.documentElement.classList.add(m); document.body.classList.add(m); }", modo)
        png = tmp / f"{modo}_{i:02d}.png"
        pg.screenshot(path=str(png), omit_background=(modo != "base")); pg.close()
        saidas.append(png)
    return saidas


def gerar_capa(br, html, destino):
    """Imagem de capa do Reel (1080×1920): a imagem da capa com o título no centro, sem legenda.
    A Meta recorta o centro para a miniatura do feed, por isso o título fica no meio."""
    pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    pg.set_content(html); pg.wait_for_timeout(150)
    pg.evaluate("() => document.body.classList.add('cover')")   # só 'cover': o modo 'base' esconderia o título
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


def musica(dia):
    idx = RAIZ / "posts/_musica/musica.json"
    if not idx.exists():
        return None
    est = [e for e in json.loads(idx.read_text())
           if (RAIZ / "posts/_musica" / e["arquivo"]).exists() and not VETO_MUSICA.search(e["title"])]
    if not est:
        return None
    import datetime as _dt
    try:
        n = _dt.date.fromisoformat(dia).toordinal()   # dias seguidos nunca repetem a faixa
    except ValueError:
        n = sum(int(c) for c in re.sub(r"\D", "", dia))
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
            plano.append((slide(pasta, e, texto_html(t, "r-body"), topo), [(post["titulo"] + ".", False), (t, True)]))
        elif k == "CITACAO":
            corpo = texto_html(t, "r-quote", aspas=True) + (f'<div class="r-author">{render.esc(autor)}</div>' if autor else "")
            partes = [(t, True)] + ([(autor.replace("·", ","), False)] if autor else [])
            plano.append((slide(pasta, e, corpo), partes))
        else:
            kick = f'<div class="r-kicker">{render.esc(k)}</div>' if k else ""
            plano.append((slide(pasta, e, kick + texto_html(t, "r-body")), [(t, True)]))

    ATRASO = 0.45  # silêncio antes da voz em cada slide
    # fase 1: narração (fora do Playwright, que mantém seu próprio loop de eventos)
    narr = []
    for i, (html, partes) in enumerate(plano):
        audios, t_cursor, t_leg, com_voz = [], ATRASO, ATRASO, not sem_voz
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
                t_leg = t_cursor   # a legenda entra quando a voz começa a ler este texto (no slide 0: depois do título)
            t_cursor += d_parte + 0.35
        narr.append((audios, t_leg, com_voz, t_cursor))
    # fase 2: quadros e montagem
    from playwright.sync_api import sync_playwright
    segs, total = [], 0.0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        html_capa = f"<html><head><style>{render.CSS}{CSS_REEL}</style></head><body style='margin:0'>{plano[0][0]}</body></html>"
        gerar_capa(br, html_capa, pasta / "reel_capa.jpg")
        for i, (html, partes) in enumerate(plano):
            audios, t_leg, com_voz, t_cursor = narr[i]
            d = max(3.0, t_cursor + 0.6)
            base, ui, cap = renderizar_slide(br, html, tmp, i)
            frames = int(round(d * FPS))
            z = "min(zoom+0.0006,1.09)" if i % 2 == 0 else "if(eq(on,1),1.09,max(zoom-0.0006,1.0))"
            zoom = f"zoompan=z='{z}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}"
            # entradas: 0 = foto (zoom), 1 = degradês e título (fixos), 2 = legenda (fade de transparente a cheio), 3 = áudio
            t_fade = max(t_leg - FADE_LEG / 2, 0.1)   # metade do fade antes da voz: o texto já está legível na 1ª palavra
            vf = (f"[0:v]{zoom}[zb];[1:v]format=rgba[ui];[zb][ui]overlay=0:0[zu];"
                  f"[2:v]format=rgba,fade=t=in:st={t_fade:.2f}:d={FADE_LEG}:alpha=1[cap];"
                  f"[zu][cap]overlay=0:0,fade=t=in:st=0:d=0.4,fade=t=out:st={d-0.4:.2f}:d=0.4,format=yuv420p[v]")
            seg = tmp / f"seg_{i:02d}.mp4"
            entradas = ["-loop", "1", "-framerate", FPS, "-i", base, "-loop", "1", "-framerate", FPS, "-i", ui,
                        "-loop", "1", "-framerate", FPS, "-i", cap]
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
            print(f"  slide {i}: {d:.1f}s {'voz' if com_voz else 'sem voz'} · {imgs[i].get('arquivo') or 'selo'} · legenda aos {t_fade:.1f}s · {partes[0][0][:40]}")
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
        # começa do início do canto (sem cortar a entrada da schola); se o canto for mais curto que o Reel, repete
        ff("-i", concat, "-stream_loop", "-1", "-i", arq,
           "-filter_complex", f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.18,afade=t=in:d=2,atrim=0:{total:.2f},afade=t=out:st={max(total-3,0):.2f}:d=3[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.95[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", saida)
        nome = e.get("nome") or e["title"].replace("File:", "").rsplit(".", 1)[0][:70]
        print(f"  música: {nome} · {e['licenca']}")
        creditos.append(f"Música: {nome} · Wikimedia Commons · {e['licenca']}")
    else:
        ff("-i", concat, "-c", "copy", "-movflags", "+faststart", saida)
        print("  sem música (estante vazia: rode scripts/fetch_music.py)")
    (pasta / "legenda_reel.txt").write_text(legenda_reel(post, itens, cit, autor, creditos) + "\n")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"reel.mp4: {total:.1f}s, {saida.stat().st_size // 1000} kB, {len(segs)} slides")


if __name__ == "__main__":
    main(sys.argv[1], sem_voz="--sem-voz" in sys.argv, sem_musica="--sem-musica" in sys.argv, sem_ia="--sem-ia" in sys.argv)
