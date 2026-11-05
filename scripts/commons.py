#!/usr/bin/env python3
"""Busca e baixa imagens do Wikimedia Commons, conferindo a licença.

Uso:
  python3 scripts/commons.py search "Miracle of Lanciano"          # lista candidatos com licença
  python3 scripts/commons.py get "File:Nome.jpg" destino.jpg        # baixa + imprime crédito em JSON

Só aceita domínio público (PD-*), CC0, CC BY e CC BY-SA. Rejeita NC, ND e 'fair use'.
"""
import json, re, sys, time, urllib.parse, requests

API = "https://commons.wikimedia.org/w/api.php"
UA = "ActaDeiBot/1.1 (https://github.com/actadeioficial/acta-dei; actadei.oficial@gmail.com) python-requests"
ACEITAS = re.compile(r"^(pd|public domain|cc0|cc-by(-sa)?(-[0-9.]+)?|cc by(-sa)?( [0-9.]+)?)", re.I)
REJEITADAS = re.compile(r"(nc|nd|fair|non-?free|copyright)", re.I)


def _req(url, params=None, tentativas=4):
    """GET com espera educada e repetição em 429/503 (a Wikimedia limita IPs de nuvem sem User-Agent descritivo)."""
    espera = 5
    for i in range(tentativas):
        r = requests.get(url, params=params, headers={"User-Agent": UA, "Accept": "*/*"}, timeout=90)
        if r.status_code in (429, 503) and i < tentativas - 1:
            print(f"  [{r.status_code}] aguardando {espera}s antes de repetir: {url[:80]}")
            time.sleep(espera); espera *= 3; continue
        r.raise_for_status()
        time.sleep(1.0)  # ritmo: no máximo ~1 requisição por segundo
        return r


def _get(params):
    return _req(API, dict(params, format="json")).json()


def _parse(page):
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


def info_batch(titles):
    """imageinfo de vários arquivos em UMA requisição (até 50)."""
    out = []
    for i in range(0, len(titles), 50):
        d = _get({"action": "query", "titles": "|".join(titles[i:i + 50]), "prop": "imageinfo",
                  "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 1600})
        for page in d["query"]["pages"].values():
            x = _parse(page)
            if x: out.append(x)
    return out


def info(title):
    """imageinfo + extmetadata de um arquivo."""
    r = info_batch([title])
    return r[0] if r else None


def search(termo, n=10):
    d = _get({"action": "query", "list": "search", "srsearch": termo,
              "srnamespace": 6, "srlimit": n})
    titulos = [hit["title"] for hit in d["query"]["search"]]
    out = []
    for i in info_batch(titulos):
        print(f"  candidato: {i['title'][:70]} | {i['licenca']} | {i['width']}x{i['height']} | ok={i['licenca_ok']}")
        if i["mime"] in ("image/jpeg", "image/png") and (i["width"] or 0) >= 800:
            out.append(i)
    return out


def download(title, destino):
    i = info(title)
    if not i:
        raise SystemExit(f"arquivo não encontrado: {title}")
    if not i["licenca_ok"]:
        raise SystemExit(f"licença não aceita ({i['licenca']}): {title}")
    open(destino, "wb").write(_req(i["url"]).content)
    return i


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "search":
        for i in search(sys.argv[2]):
            print(("OK " if i["licenca_ok"] else "-- ") + f"{i['title']} | {i['licenca']} | {i['width']}x{i['height']} | {i['autor'][:40]}")
    elif cmd == "get":
        print(json.dumps(download(sys.argv[2], sys.argv[3]), ensure_ascii=False, indent=2))
