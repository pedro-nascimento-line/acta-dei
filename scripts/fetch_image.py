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
import requests

UA = commons.UA


def lead_image(artigo):
    """Imagem principal de um artigo da Wikipédia (en: ou pt: prefixo)."""
    lang, titulo = ("pt", artigo[3:]) if artigo.startswith("pt:") else ("en", artigo.replace("en:", ""))
    d = requests.get(f"https://{lang}.wikipedia.org/w/api.php", headers={"User-Agent": UA}, timeout=60,
                     params={"action": "query", "titles": titulo, "prop": "pageimages", "piprop": "name", "format": "json", "redirects": 1}).json()
    page = next(iter(d["query"]["pages"].values()))
    nome = page.get("pageimage")
    return f"File:{nome}" if nome else None


def resolver(spec):
    cands = []
    if spec.get("imagem_commons"):
        cands.append(spec["imagem_commons"])
    if spec.get("imagem_wikipedia"):
        t = lead_image(spec["imagem_wikipedia"])
        if t: cands.append(t)
    for t in cands:
        i = commons.info(t)
        if i and i["licenca_ok"] and (i["width"] or 0) >= 800:
            return i
    if spec.get("imagem_busca"):
        for i in commons.search(spec["imagem_busca"], n=15):
            if i["licenca_ok"] and (i["width"] or 0) >= 1000:
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
        i = resolver(spec)
        if not i:
            print(f"[{nome}] nenhuma imagem com licença aceita; capa cairá no selo")
            spec.pop(campo, None); continue
        destino = pasta / (spec.get(campo) or f"{nome}.jpg")
        r = requests.get(i["url"], headers={"User-Agent": UA}, timeout=120); r.raise_for_status()
        destino.write_bytes(r.content)
        spec[campo] = destino.name
        if nome == "principal":
            post["imagem_credito"] = credito(i)
        usadas[nome] = {k: i[k] for k in ("title", "licenca", "autor", "pagina", "url_original")}
        print(f"[{nome}] {i['title']} · {i['licenca']}")
    (pasta / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2))
    (pasta / "imagens.json").write_text(json.dumps(usadas, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
