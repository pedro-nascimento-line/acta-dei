#!/usr/bin/env python3
"""Baixa a imagem de domínio público/CC do post, conferindo a licença no Wikimedia Commons.

Uso: python3 scripts/fetch_image.py posts/2026-11-10
Lê post.json e, para cada alvo (imagem principal e imagem do story da manhã), resolve nesta ordem:
  1. "imagem_commons": título exato "File:…" (curadoria manual ou do banco de dados);
  2. "imagem_wikipedia": título de artigo da Wikipédia (en ou pt) → imagem principal do artigo (pageimages);
  3. "imagem_busca": termo de busca no Commons (namespace File), filtrando licença e tamanho.
Grava a imagem, preenche "imagem_credito" e registra em imagens.json o que foi usado (título, licença, autor, página).
Se nada passar no filtro de licença, não grava nada: render.py usa o selo como capa e o log avisa.
"""
import json, re, sys, urllib.parse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import commons  # noqa: E402
import io, requests
from PIL import Image

UA = commons.UA


def lead_image(artigo):
    """Imagem principal de um artigo da Wikipédia (en: ou pt: prefixo)."""
    lang, titulo = ("pt", artigo[3:]) if artigo.startswith("pt:") else ("en", artigo.replace("en:", ""))
    d = commons._req(f"https://{lang}.wikipedia.org/w/api.php",
                     params={"action": "query", "titles": titulo, "prop": "pageimages", "piprop": "name", "format": "json", "redirects": 1}).json()
    page = next(iter(d["query"]["pages"].values()))
    nome = page.get("pageimage")
    return f"File:{nome}" if nome else None


def tamanho_ok(i, minimo=600):
    w, h = i.get("width") or 0, i.get("height") or 0
    return min(w, h) >= minimo and max(w, h) >= 1000


def resolver(spec):
    cands = []
    if spec.get("imagem_commons"):
        cands.append(spec["imagem_commons"])
    if spec.get("imagem_wikipedia"):
        t = lead_image(spec["imagem_wikipedia"])
        if t: cands.append(t)
    for t in cands:
        i = commons.info(t)
        print(f"  candidato (artigo): {t[:70]} -> " + (f"{i['licenca']} | {i['width']}x{i['height']} | ok={i['licenca_ok']}" if i else "não está no Commons"))
        if i and i["licenca_ok"] and tamanho_ok(i):
            return i
    termos = spec.get("imagem_busca") or ""
    termos = termos if isinstance(termos, list) else [termos]
    # além dos termos dados, tenta versões mais curtas (tira a última palavra) até achar algo
    fila = []
    for t in termos:
        palavras = t.split()
        while palavras:
            fila.append(" ".join(palavras)); palavras = palavras[:-1]
    vistos = set()
    for t in fila:
        if not t or t in vistos: continue
        vistos.add(t)
        achados = commons.search(t, n=15)
        print(f"  busca '{t}': {len(achados)} candidatos")
        bons = [i for i in achados if i["licenca_ok"] and tamanho_ok(i)]
        if bons:
            bons.sort(key=lambda i: -(i["width"] or 0) * (i["height"] or 0))
            return bons[0]
    # último recurso: a imagem do artigo mesmo pequena (≥ 500 px), melhor que o selo
    for t in cands:
        i = commons.info(t)
        if i and i["licenca_ok"] and tamanho_ok(i, minimo=500):
            return i
    return None


def credito(i):
    autor = re.sub(r"\s+", " ", i["autor"] or "").strip()
    autor = autor[:60] + ("…" if len(autor) > 60 else "")
    return f"{autor + ' · ' if autor else ''}Wikimedia Commons · {i['licenca']}"


def main(pasta):
    pasta = Path(pasta)
    post = json.loads((pasta / "post.json").read_text())
    usadas = {}
    alvos = [("principal", post, "imagem")]
    manha = post.get("stories", {}).get("manha")
    if manha:
        alvos.append(("santo", manha, "imagem"))
    for nome, spec, campo in alvos:
        try:
            if nome == "santo" and not spec.get("imagem_busca"):
                # sem termo de busca para o santo: usa o título do artigo e o nome como reserva
                wiki = (spec.get("imagem_wikipedia") or "").split(":", 1)[-1]
                spec["imagem_busca"] = [t for t in (wiki, spec.get("nome", "")) if t]
            i = resolver(spec)
            if not i:
                print(f"[{nome}] nenhuma imagem com licença aceita; capa cairá no selo")
                spec.pop(campo, None); continue
            destino = pasta / (spec.get(campo) or f"{nome}.jpg")
            destino = destino.with_suffix(".jpg")
            img = Image.open(io.BytesIO(commons._req(i["url"]).content)).convert("RGB")
            img.thumbnail((1600, 1600))  # nunca guarda o original gigante no repositório
            img.save(destino, "JPEG", quality=88, optimize=True)
            spec[campo] = destino.name
            if nome == "principal":
                post["imagem_credito"] = credito(i)
            usadas[nome] = {k: i[k] for k in ("title", "licenca", "autor", "pagina", "url_original")}
            print(f"[{nome}] {i['title']} · {i['licenca']}")
        except Exception as e:  # segue para o próximo alvo; o render usa o fallback
            print(f"[{nome}] falha: {e}")
            spec.pop(campo, None)
    (pasta / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2))
    (pasta / "imagens.json").write_text(json.dumps(usadas, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
