#!/usr/bin/env python3
"""Garimpa no Wikimedia Commons imagens que mostram O TEMA do post (o relicário, a igreja do milagre, a pintura
do episódio, o túmulo do santo), e não só "algo católico". Usado pelo make_reel.py.

Fontes, da mais confiável para a menos:
  1. arquivos indicados pela tarefa diária (post.imagens_reel.arquivos: títulos exatos "File:…");
  2. categorias do Commons do tema (post.imagens_reel.categorias + a categoria oficial de cada artigo da Wikipédia,
     lida do Wikidata, propriedade P373), com um nível de subcategorias;
  3. imagens usadas nos artigos da Wikipédia sobre o tema (post.imagens_reel.artigos + post.imagem_wikipedia);
  4. busca por frase exata no Commons (post.imagens_reel.termos e o termo de cada cena do Reel).
Cada candidato ganha uma nota: fonte + quantas palavras-chave do tema aparecem no título e na descrição.
Resultado de busca sem palavra-chave suficiente é descartado — melhor uma ilustração identificada como IA
do que uma foto bonita que não tem nada a ver com o assunto.

Teste local: python3 scripts/imagens_tema.py posts/2026-11-12   (lista o que escolheria, sem baixar)
"""
import json, re, sys, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import commons  # noqa: E402

WIKIDATA = "https://www.wikidata.org/w/api.php"
DESCARTE = re.compile(r"(\bmap\b|mapa|karte|carte\b|coat of arms|bras[aã]o|stemma|wappen|\bflag\b|bandeira|bandiera|logo|"
                      r"\bseal\b|stamp|francobollo|selo|diagram|\bplan\b|pianta|schema|signature|firma|\.svg|\.pdf|\.djvu|"
                      r"\.ogg|\.ogv|\.webm|\.mp3|\.wav|\.tif.*IA |\(IA )", re.I)
PARADAS = set("""a o as os de da do das dos e em no na nos nas um uma para por com sem sobre que
the of and in on at to for with from by an la le les el los las di del della delle dei degli il lo gli
und der die das von zu im am san santo santa sao saint sankt st ste basilica basilique chiesa church igreja
eglise iglesia kirche cathedral catedral cattedrale duomo chapel capela cappella file jpg jpeg png
miracle milagre miracolo milagro wunder eucaristico eucharistic eucaristica eucharistique
desde entre sobre contra quando mais anos italia brasil franca espanha portugal reconhecido""".split())


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def chaves_de(textos):
    """Palavras que identificam o tema (nomes próprios, objetos), sem as genéricas da lista PARADAS."""
    out = []
    for t in textos:
        for w in norm(t).split():
            if len(w) >= 4 and w not in PARADAS and not w.isdigit() and w not in out:
                out.append(w)
    return out


def acertos(cand, chaves):
    texto = norm(cand["title"] + " " + cand.get("descricao", ""))
    return sum(1 for k in chaves if re.search(rf"\b{re.escape(k)}", texto))


def _artigo(spec):
    """'it:Miracolo eucaristico di Siena' -> ('it', 'Miracolo eucaristico di Siena'); sem prefixo = en."""
    m = re.match(r"^([a-z]{2,3}):(.+)$", spec.strip())
    return (m.group(1), m.group(2)) if m else ("en", spec.strip())


def categoria_wikidata(lang, titulo):
    try:
        d = commons._req(WIKIDATA, params={"action": "wbgetentities", "sites": f"{lang}wiki", "titles": titulo,
                                           "props": "claims", "format": "json", "redirects": "yes"}).json()
        for ent in d.get("entities", {}).values():
            for c in ent.get("claims", {}).get("P373", []):
                v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
                if v:
                    return "Category:" + v
    except Exception as e:
        print(f"  wikidata falhou ({lang}:{titulo}): {e}")
    return None


def arquivos_categoria(cat, profundidade=1, limite=60):
    titulos, subcats = [], []
    try:
        d = commons._get({"action": "query", "list": "categorymembers", "cmtitle": cat, "cmlimit": 200,
                          "cmtype": "file|subcat"})
        for m in d.get("query", {}).get("categorymembers", []):
            (titulos if m["ns"] == 6 else subcats).append(m["title"])
    except Exception as e:
        print(f"  categoria falhou ({cat}): {e}")
    if profundidade > 0:
        for sc in subcats[:6]:
            titulos += arquivos_categoria(sc, profundidade - 1, limite=20)
    return titulos[:limite]


def imagens_artigo(lang, titulo):
    try:
        d = commons._req(f"https://{lang}.wikipedia.org/w/api.php",
                         params={"action": "query", "titles": titulo, "prop": "images", "imlimit": 100,
                                 "redirects": 1, "format": "json"}).json()
        out = []
        for p in d.get("query", {}).get("pages", {}).values():
            out += [re.sub(r"^[^:]+:", "File:", i["title"]) for i in p.get("images", [])]
        return out
    except Exception as e:
        print(f"  artigo falhou ({lang}:{titulo}): {e}")
        return []


def busca_frase(termo, n=25):
    q = f'"{termo}"' if " " in termo.strip() else termo
    try:
        d = commons._get({"action": "query", "list": "search", "srsearch": q, "srnamespace": 6, "srlimit": n})
        return [h["title"] for h in d["query"]["search"]]
    except Exception as e:
        print(f"  busca falhou ({termo}): {e}")
        return []


def coletar(post, termos_cenas=(), max_candidatos=40):
    """Lista de candidatos (dicts do commons.info) ordenada pela nota, só com licença aceita e tamanho útil."""
    ir = post.get("imagens_reel") or {}
    artigos = list(ir.get("artigos") or [])
    if post.get("imagem_wikipedia"):
        artigos.append(post["imagem_wikipedia"])
    if post.get("tipo") == "santo":
        w = ((post.get("stories") or {}).get("manha") or {}).get("imagem_wikipedia")
        if w: artigos.append(w)
    termos = list(ir.get("termos") or [])
    busca = post.get("imagem_busca") or []
    termos += busca if isinstance(busca, list) else [busca]
    termos += [t for t in termos_cenas if t]
    chaves = chaves_de(termos + [_artigo(a)[1] for a in artigos] + [post.get("titulo", ""), post.get("subtitulo", "").split("·")[0]])
    print(f"  palavras-chave do tema: {', '.join(chaves[:20])}")

    fonte = {}  # título -> peso da fonte

    def add(titulos, peso):
        for t in titulos:
            t = t.replace("_", " ").strip()
            if t.startswith("File:") and not DESCARTE.search(t):
                fonte[t] = max(fonte.get(t, 0), peso)

    add(ir.get("arquivos") or [], 100)
    cats = list(ir.get("categorias") or [])
    for a in artigos:
        lang, tit = _artigo(a)
        c = categoria_wikidata(lang, tit)
        if c and c not in cats: cats.append(c)
        add(imagens_artigo(lang, tit), 30)
    for c in cats:
        c = c if c.startswith("Category:") else "Category:" + c
        add(arquivos_categoria(c), 40)
    for t in termos:
        add(busca_frase(t), 0)

    if not fonte:
        return []
    cands = []
    for i in commons.info_batch(list(fonte)):
        if not i["licenca_ok"] or i.get("mime") not in ("image/jpeg", "image/png", "image/tiff", "image/webp"):
            continue
        if min(i.get("width") or 0, i.get("height") or 0) < 500 or DESCARTE.search(i.get("descricao", "")):
            continue
        h = acertos(i, chaves)
        peso = fonte.get(i["title"].replace("_", " "), 0)
        if peso == 0 and h < min(2, len(chaves)):   # busca solta: precisa citar o tema
            continue
        i["nota"] = peso + 12 * h + min((i.get("width") or 0) * (i.get("height") or 0) / 1e6, 6)
        i["acertos"] = h
        cands.append(i)
    cands.sort(key=lambda x: -x["nota"])
    for c in cands[:12]:
        print(f"  [{c['nota']:5.1f}] {c['title'][5:75]} · {c['licenca']}")
    return cands[:max_candidatos]


def ordenar_para_cena(cands, termo, usados=()):
    """Candidatos ainda não usados, do mais adequado para a cena (cita o termo da cena) ao menos adequado."""
    ch = chaves_de([termo]) if termo else []
    resto = [c for c in cands if c["title"] not in usados]
    return sorted(resto, key=lambda c: -(c["nota"] + (60 * acertos(c, ch) if ch else 0)))


if __name__ == "__main__":
    post = json.loads((Path(sys.argv[1]) / "post.json").read_text())
    cenas = [i.get("imagem", "") if isinstance(i, dict) else "" for i in post.get("reel", [])]
    cands, usados = coletar(post, cenas), set()
    for k, termo in enumerate(cenas):
        o = ordenar_para_cena(cands, termo, usados)
        print(f"cena {k} ({termo or '-'}) →", o[0]["title"] if o else "(IA)")
        if o: usados.add(o[0]["title"])
