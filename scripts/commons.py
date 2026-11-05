#!/usr/bin/env python3
"""Busca e baixa imagens do Wikimedia Commons, conferindo a licença.

Uso:
  python3 scripts/commons.py search "Miracle of Lanciano"          # lista candidatos com licença
  python3 scripts/commons.py get "File:Nome.jpg" destino.jpg        # baixa + imprime crédito em JSON

Só aceita domínio público (PD-*), CC0, CC BY e CC BY-SA. Rejeita NC, ND e 'fair use'.
"""
import json, re, sys, urllib.parse, requests

API = "https://commons.wikimedia.org/w/api.php"
UA = "ActaDei/1.0 (projeto editorial; contato via github)"
ACEITAS = re.compile(r"^(pd|public domain|cc0|cc-by(-sa)?(-[0-9.]+)?|cc by(-sa)?( [0-9.]+)?)", re.I)
REJEITADAS = re.compile(r"(nc|nd|fair|non-?free|copyright)", re.I)


def _get(params):
    params = dict(params, format="json")
    r = requests.get(API, params=params, headers={"User-Agent": UA}, timeout=60)
    r.raise_for_status()
    return r.json()


def info(title):
    """imageinfo + extmetadata de um arquivo."""
    d = _get({"action": "query", "titles": title, "prop": "imageinfo",
              "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 1600})
    page = next(iter(d["query"]["pages"].values()))
    if "imageinfo" not in page:
        return None
    ii = page["imageinfo"][0]
    em = ii.get("extmetadata", {})
    g = lambda k: re.sub("<[^>]+>", "", em.get(k, {}).get("value", "")).strip()
    lic = g("LicenseShortName") or g("License")
    return {
        "title": page["title"],
        "url": ii.get("thumburl") or ii["url"],
        "url_original": ii["url"],
        "width": ii.get("width"), "height": ii.get("height"), "mime": ii.get("mime"),
        "licenca": lic,
        "licenca_ok": bool(ACEITAS.search(lic)) and not REJEITADAS.search(lic),
        "autor": g("Artist"), "credito": g("Credit"), "data_obra": g("DateTimeOriginal"),
        "descricao": g("ImageDescription")[:300],
        "pagina": f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(page['title'])}",
    }


def search(termo, n=10):
    d = _get({"action": "query", "list": "search", "srsearch": termo,
              "srnamespace": 6, "srlimit": n})
    out = []
    for hit in d["query"]["search"]:
        i = info(hit["title"])
        if i and i["mime"] in ("image/jpeg", "image/png") and (i["width"] or 0) >= 800:
            out.append(i)
    return out


def download(title, destino):
    i = info(title)
    if not i:
        raise SystemExit(f"arquivo não encontrado: {title}")
    if not i["licenca_ok"]:
        raise SystemExit(f"licença não aceita ({i['licenca']}): {title}")
    r = requests.get(i["url"], headers={"User-Agent": UA}, timeout=120)
    r.raise_for_status()
    open(destino, "wb").write(r.content)
    return i


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "search":
        for i in search(sys.argv[2]):
            print(("OK " if i["licenca_ok"] else "-- ") + f"{i['title']} | {i['licenca']} | {i['width']}x{i['height']} | {i['autor'][:40]}")
    elif cmd == "get":
        print(json.dumps(download(sys.argv[2], sys.argv[3]), ensure_ascii=False, indent=2))
