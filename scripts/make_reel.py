#!/usr/bin/env python3
"""Gera o Reel do dia (posts/<dia>/reel.mp4, 1080×1920, ~30 s) e a legenda (legenda_reel.txt).

Uso: python3 scripts/make_reel.py posts/2026-11-07 [--sem-voz] [--sem-musica]

Roteiro: usa `post["reel"]` (lista de 4 a 6 frases curtas escrita pela tarefa diária); se não houver,
extrai as primeiras frases de cada card. Cada frase vira um slide (Playwright, mesmas fontes e cores
dos cards) narrado por voz sintética (edge-tts, pt-BR) sobre música sacra de domínio público
(posts/_musica, ver fetch_music.py). Montagem com ffmpeg: zoom lento, fade, voz + música em -14 dB.
Sem voz ou sem música o vídeo sai do mesmo jeito (o log avisa).
"""
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402  (CSS, fontes, data_uri, esc, STATUS, SELO)

RAIZ = Path(__file__).resolve().parent.parent
VOZ = "pt-BR-AntonioNeural"
W, H, FPS = 1080, 1920, 30
ESCALA = 1.2  # renderiza maior para o zoom não borrar

CSS_REEL = f"""
.reel {{ width: {W}px; height: {H}px; background: {render.CHAR}; color: {render.CREAM}; position: relative; overflow: hidden; }}
.r-hero {{ position: absolute; inset: 0; }}
.r-hero img.bg {{ position: absolute; inset: -60px; width: calc(100% + 120px); height: calc(100% + 120px); object-fit: cover; filter: blur(30px) brightness(.5); }}
.r-hero img.fg {{ position: absolute; left: 90px; top: 330px; width: 900px; height: 900px; object-fit: contain; }}
.r-hero img.cv {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: center 30%; filter: brightness(.85); }}
.r-shade {{ position: absolute; left: 0; right: 0; bottom: 0; height: 900px; background: linear-gradient(180deg, rgba(38,34,30,0) 0%, rgba(38,34,30,.92) 55%); }}
.r-title {{ position: absolute; left: 80px; right: 80px; bottom: 560px; }}
.r-title h1 {{ font-family: 'Cinzel'; font-weight: 700; font-size: 72px; line-height: 1.12; color: {render.CREAM}; }}
.r-title .sub {{ font-size: 40px; font-style: italic; color: #CFC7B8; margin-top: 18px; }}
.r-badge {{ display: inline-block; font-family: 'Cinzel'; font-weight: 700; font-size: 20px; letter-spacing: 3px; color: {render.CREAM}; background: {render.RED}; padding: 12px 18px 10px; border-radius: 6px; margin-bottom: 26px; }}
.r-text {{ position: absolute; left: 90px; right: 90px; top: 0; bottom: 0; display: flex; flex-direction: column; justify-content: center; padding-bottom: 160px; }}
.r-kicker {{ font-family: 'Cinzel'; font-weight: 700; font-size: 30px; letter-spacing: 6px; color: {render.RED}; margin-bottom: 44px; }}
.r-body {{ font-family: 'Cormorant'; font-size: 66px; line-height: 1.3; font-weight: 500; }}
.r-rule {{ width: 120px; height: 4px; background: {render.RED}; margin-top: 48px; }}
.r-foot {{ position: absolute; left: 0; right: 0; bottom: 470px; text-align: center; font-family: 'Cinzel'; font-size: 24px; letter-spacing: 6px; color: {render.RED}; }}
.r-end {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; padding-bottom: 200px; text-align: center; }}
.r-end img {{ width: 420px; margin-bottom: 40px; }}
.r-end .h {{ font-family: 'Cinzel'; font-weight: 700; font-size: 44px; letter-spacing: 6px; }}
.r-end .s {{ font-size: 40px; font-style: italic; color: #CFC7B8; margin-top: 24px; }}
.r-end .u {{ font-family: 'Cinzel'; font-size: 30px; letter-spacing: 4px; color: {render.RED}; margin-top: 40px; }}
"""


def frases(txt, n=2, max_len=190):
    partes = [p.strip() for p in re.split(r"(?<=[.!?])\s+", (txt or "").replace("\n", " ")) if p.strip()]
    out, acc = [], ""
    for p in partes:
        if not acc:
            acc = p
        elif len(acc) + 1 + len(p) <= max_len and len(out) + 1 < n:
            acc += " " + p
        else:
            out.append(acc); acc = p
        if len(out) >= n: break
    if acc and len(out) < n: out.append(acc)
    return out[:n]


def roteiro(post):
    """Lista de (kicker, texto) — do campo `reel` ou extraído dos cards."""
    if post.get("reel"):
        itens = post["reel"]
        return [((i.get("kicker") if isinstance(i, dict) else None), (i.get("texto") if isinstance(i, dict) else i)) for i in itens]
    out = []
    for c in post.get("cards", [])[:3]:
        k = (c.get("kicker") or "").split("·")[0].strip()
        for f in frases(c.get("texto", ""), n=1 if len(out) else 1):
            out.append((k, f))
    if post.get("decisao"):
        k = "O QUE A SANTA IGREJA CATÓLICA DECIDIU"
        out.append((k, frases(post["decisao"], n=1)[0]))
    return out[:5]


def slide_capa(post, pasta):
    tem = post.get("imagem") and (pasta / post["imagem"]).exists()
    if tem:
        uri = render.data_uri(pasta / post["imagem"])
        try:
            from PIL import Image
            with Image.open(pasta / post["imagem"]) as im:
                w, h = im.size
        except Exception:
            w, h = 1, 1
        hero = (f'<img class="bg" src="{uri}"><img class="fg" src="{uri}">' if w / h < 0.95
                else f'<img class="cv" src="{uri}">')
    else:
        hero = f'<img class="fg" src="{render.SELO}">'
    st = render.STATUS.get(post.get("status") or "")
    badge = f'<div class="r-badge">{st[0]}</div>' if st else ""
    return f"""<div class="reel"><div class="r-hero">{hero}</div><div class="r-shade"></div>
      <div class="r-title">{badge}<h1>{render.esc(post['titulo'])}</h1><div class="sub">{render.esc(post.get('subtitulo',''))}</div></div>
      <div class="r-foot">ACTA DEI · MYSTERIUM FIDEI</div></div>"""


def slide_texto(kicker, texto):
    k = f'<div class="r-kicker">{render.esc(kicker)}</div>' if kicker else ""
    return f"""<div class="reel"><div class="r-text">{k}<div class="r-body">{render.esc(texto)}</div><div class="r-rule"></div></div>
      <div class="r-foot">ACTA DEI · MYSTERIUM FIDEI</div></div>"""


def slide_final():
    return f"""<div class="reel"><div class="r-end"><img src="{render.AVATAR_DARK}">
      <div class="h">ACTA DEI</div><div class="s">Relato completo e fontes no post de hoje</div>
      <div class="u">@ACTADEI.OFICIAL · LINK NA BIO</div></div></div>"""


def renderizar_slides(htmls, tmp):
    from playwright.sync_api import sync_playwright
    pngs = []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for i, body in enumerate(htmls):
            pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=ESCALA)
            pg.set_content(f"<html><head><style>{render.CSS}{CSS_REEL}</style></head><body style='margin:0'>{body}</body></html>")
            pg.wait_for_timeout(200)
            pg.evaluate("""() => { const t = document.querySelector('.r-body'); if (!t) return;
                let fs = 66; while (t.getBoundingClientRect().height > 1000 && fs > 36) { fs -= 2; t.style.fontSize = fs + 'px'; } }""")
            p = tmp / f"slide_{i:02d}.png"
            pg.screenshot(path=str(p)); pg.close(); pngs.append(p)
        br.close()
    return pngs


def narrar(texto, destino):
    """edge-tts; devolve True se gerou áudio."""
    try:
        r = subprocess.run([sys.executable, "-m", "edge_tts", "--voice", VOZ, "--rate=-6%", "--text", texto,
                            "--write-media", str(destino)], capture_output=True, text=True, timeout=120)
        return r.returncode == 0 and destino.exists() and destino.stat().st_size > 1000
    except Exception as e:
        print(f"  narração falhou: {e}")
        return False


def dur(arq):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                         capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.0


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)], check=True)


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


def legenda_reel(post, itens):
    st = render.STATUS.get(post.get("status") or "")
    linhas = [post["titulo"].upper()]
    if st: linhas.append(f"■ {st[0]}")
    if post.get("subtitulo"): linhas.append(post["subtitulo"])
    linhas.append("")
    linhas += [t for _, t in itens]
    linhas += ["", "O relato completo, com as fontes, está no carrossel de hoje e no índice do link da bio."]
    if post.get("titulo_en"):
        linhas += ["", "· · ·", "", post["titulo_en"], "Full story and sources in today's post and in the link in bio."]
    return "\n".join(linhas)


def main(pasta, sem_voz=False, sem_musica=False):
    pasta = Path(pasta)
    post = json.loads((pasta / "post.json").read_text())
    itens = roteiro(post)
    if not itens:
        sys.exit("post sem texto para o reel")
    gancho = itens[0][1]
    htmls = [slide_capa(post, pasta)] + [slide_texto(k, t) for k, t in itens[1:]] + [slide_final()]
    falas = [f"{post['titulo']}. {gancho}"] + [t for _, t in itens[1:]] + ["Relato completo e fontes no post de hoje. Acta Dei."]
    tmp = Path(tempfile.mkdtemp(prefix="reel_"))
    pngs = renderizar_slides(htmls, tmp)
    segs, total = [], 0.0
    for i, (png, fala) in enumerate(zip(pngs, falas)):
        voz = tmp / f"voz_{i:02d}.mp3"
        tem_voz = (not sem_voz) and narrar(fala, voz)
        d = (dur(voz) + 1.1) if tem_voz else max(3.2, 0.07 * len(fala))
        d = max(3.0, min(d, 14.0))
        frames = int(round(d * FPS))
        zoom = f"zoompan=z='min(zoom+0.0006,1.08)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}"
        vf = f"[0:v]{zoom},fade=t=in:st=0:d=0.35,fade=t=out:st={d-0.35:.2f}:d=0.35,format=yuv420p[v]"
        seg = tmp / f"seg_{i:02d}.mp4"
        if tem_voz:
            ff("-loop", "1", "-framerate", FPS, "-i", png, "-i", voz,
               "-filter_complex", f"{vf};[1:a]adelay=500|500,apad[a]", "-map", "[v]", "-map", "[a]",
               "-t", f"{d:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", seg)
        else:
            ff("-loop", "1", "-framerate", FPS, "-i", png, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
               "-filter_complex", vf, "-map", "[v]", "-map", "1:a",
               "-t", f"{d:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", seg)
        segs.append(seg); total += d
        print(f"  slide {i}: {d:.1f}s {'voz' if tem_voz else 'sem voz'} · {fala[:60]}")
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{s}'\n" for s in segs))
    concat = tmp / "concat.mp4"
    ff("-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", concat)
    saida = pasta / "reel.mp4"
    m = None if sem_musica else musica(pasta.name)
    if m:
        arq, e = m
        ini = 0 if e["segundos"] <= total + 5 else (sum(int(c) for c in re.sub(r"\D", "", pasta.name)) * 7) % int(e["segundos"] - total - 3)
        ff("-i", concat, "-ss", ini, "-i", arq,
           "-filter_complex", f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.2,afade=t=in:d=2,atrim=0:{total:.2f},afade=t=out:st={max(total-3,0):.2f}:d=3[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.95[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", saida)
        print(f"  música: {e['title'][:60]} · {e['licenca']}")
        credito = f"Música: {e['title'].replace('File:', '')} · Wikimedia Commons · {e['licenca']}"
    else:
        ff("-i", concat, "-c", "copy", "-movflags", "+faststart", saida)
        print("  sem música (estante vazia: rode scripts/fetch_music.py)")
        credito = ""
    (pasta / "legenda_reel.txt").write_text(legenda_reel(post, itens) + (f"\n\n{credito}" if credito else "") + "\n")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"reel.mp4: {total:.1f}s, {saida.stat().st_size // 1000} kB, {len(segs)} slides")


if __name__ == "__main__":
    main(sys.argv[1], sem_voz="--sem-voz" in sys.argv, sem_musica="--sem-musica" in sys.argv)
