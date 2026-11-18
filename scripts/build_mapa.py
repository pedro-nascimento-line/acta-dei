#!/usr/bin/env python3
"""Mapa dos milagres + uma página por milagre (GitHub Pages, link da bio).

Gera posts/mapa/index.html (mapa interativo: cada milagre publicado é uma cruz; passar o mouse mostra o cartão,
clicar abre a página) e posts/mapa/<id>.html (relato, decisão, fotos com crédito, vídeos públicos, como visitar,
fontes, link do post). Fica dentro de posts/ porque é a pasta que os workflows já versionam; /mapa/ na raiz do site
redireciona para cá.

Dados de cada milagre: o post.json mais recente com aquele id_milagre (posts/AAAA-MM-DD/), o meta.json (link do
post no Instagram), o reel_imagens.json (fotos do Commons), o catálogo data/milagres.json e, para os posts antigos,
data/mapa_extras.json. Campos novos do post.json (escritos pela tarefa diária): coordenadas [lat, lon],
visitar {lugar, cidade}, videos [urls ou ids do YouTube], fontes_links [urls, na ordem de fontes], relato_completo.

Coordenadas: post.json > mapa_extras > cache > Wikidata (P625 dos artigos da Wikipédia do post) > Nominatim (local,
país) > coordenadas_aprox. Vídeos: conferidos pelo oEmbed do YouTube (some se o vídeo sair do ar). Os dois caches
ficam em posts/mapa/cache.json. Sem internet, usa o que tiver no cache.

Chamado pelo build_index.py (roda no build das artes e depois de cada publicação). Teste: python3 scripts/build_mapa.py
"""
import html, json, re, sys, time, urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "posts" / "mapa"   # sem "_" no nome: o GitHub Pages (Jekyll) ignora pastas que começam com "_"
UA = "ActaDeiBot/1.2 (https://github.com/pedro-nascimento-line/acta-dei)"
STATUS = {"reconhecido": "Reconhecido pela Santa Igreja Católica", "investigacao": "Em investigação pela Santa Igreja Católica"}
PERFIL = "https://www.instagram.com/actadei.oficial/"
esc = html.escape

FONTES_CSS = "@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&display=swap');"
BASE_CSS = """
:root{--red:#A6192E;--red2:#F0434F;--cream:#F7F2E8;--char:#26221E;--grey:#6B655E;--line:#E2D8C6}
*{box-sizing:border-box}html,body{margin:0}body{background:var(--cream);color:var(--char);font-family:'Cormorant Garamond',Georgia,serif;font-size:20px;line-height:1.55}
a{color:var(--red)}.cz{font-family:Cinzel,serif;letter-spacing:2px}
.top{display:flex;align-items:center;gap:14px;padding:14px 20px;background:var(--char);color:var(--cream)}
.top img{width:44px;height:44px;border-radius:50%}
.leaflet-tile-pane{filter:grayscale(.75) sepia(.22) brightness(1.04) contrast(.92)}  /* mapa-base em tons da paleta */.top b{font-family:Cinzel,serif;letter-spacing:3px;font-size:17px}.top span{font-style:italic;color:#CFC7B8;font-size:17px}
.top a{color:var(--cream);text-decoration:none}.top .dir{margin-left:auto;font-family:Cinzel,serif;font-size:13px;letter-spacing:2px}
@media(max-width:600px){.top span{display:none}.top .dir{font-size:11px;letter-spacing:1px}}
.badge{display:inline-block;background:var(--red);color:var(--cream);font-family:Cinzel,serif;font-size:11px;letter-spacing:2px;padding:4px 9px;border-radius:4px}
.badge.inv{background:#7a6a55}
footer{text-align:center;color:var(--grey);font-size:16px;padding:40px 16px 60px}
"""


# ------------------------------------------------------------------ rede (tolerante a falha)
def _get(url, params=None, timeout=25):
    try:
        import requests
        r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"  mapa: {url[:60]} falhou: {e}")
    return None


def _artigo(spec):
    m = re.match(r"^([a-z]{2,3}):(.+)$", (spec or "").strip())
    return (m.group(1), m.group(2)) if m else ("en", (spec or "").strip())


def coord_wikidata(artigos):
    for a in artigos:
        lang, tit = _artigo(a)
        if not tit:
            continue
        d = _get("https://www.wikidata.org/w/api.php", {"action": "wbgetentities", "sites": f"{lang}wiki", "titles": tit,
                                                        "props": "claims", "format": "json", "redirects": "yes"})
        for ent in (d or {}).get("entities", {}).values():
            for c in ent.get("claims", {}).get("P625", []):
                v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
                if v:
                    return [round(v["latitude"], 5), round(v["longitude"], 5)]
        time.sleep(1)
    return None


def coord_nominatim(consulta):
    d = _get("https://nominatim.openstreetmap.org/search", {"q": consulta, "format": "json", "limit": 1})
    time.sleep(1.1)  # política de uso: 1 requisição por segundo
    if d:
        return [round(float(d[0]["lat"]), 5), round(float(d[0]["lon"]), 5)]
    return None


def video_id(v):
    v = (v or "").strip()
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{11})", v)
    return m.group(1) if m else (v if re.fullmatch(r"[A-Za-z0-9_-]{11}", v) else None)


def video_info(vid, cache):
    if vid in cache:
        return cache[vid]
    d = _get("https://www.youtube.com/oembed", {"url": f"https://www.youtube.com/watch?v={vid}", "format": "json"})
    info = {"titulo": d.get("title", ""), "canal": d.get("author_name", "")} if d else None
    if info:
        cache[vid] = info  # indisponível (fora do ar, privado, rede falhou) não entra no cache: confere de novo depois
    return info


# ------------------------------------------------------------------ dados
def coletar():
    cat = {}
    try:
        cat = {m["id"]: m for m in json.loads((RAIZ / "data/milagres.json").read_text())["milagres"]}
    except Exception as e:
        print(f"  mapa: catálogo ilegível: {e}")
    extras = {}
    try:
        extras = json.loads((RAIZ / "data/mapa_extras.json").read_text())
    except Exception:
        pass
    por_id = {}
    for pasta in sorted((RAIZ / "posts").glob("????-??-??")):
        pj = pasta / "post.json"
        if not pj.exists():
            continue
        try:
            p = json.loads(pj.read_text())
        except Exception:
            continue
        if p.get("tipo") != "milagre" or not p.get("id_milagre"):
            continue
        meta = json.loads((pasta / "meta.json").read_text()) if (pasta / "meta.json").exists() else {}
        if not meta.get("feed_id"):
            continue  # só o que já saiu no feed
        por_id[p["id_milagre"]] = {"id": p["id_milagre"], "dia": pasta.name, "post": p, "meta": meta,
                                    "cat": cat.get(p["id_milagre"], {}), "extra": extras.get(p["id_milagre"], {})}
    return list(por_id.values())


def preparar(m, cache):
    p, cat, ex, dia = m["post"], m["cat"], m["extra"], m["dia"]
    pasta = RAIZ / "posts" / dia
    # coordenadas
    cc = cache.setdefault("coordenadas", {})
    co = p.get("coordenadas") or ex.get("coordenadas") or cc.get(m["id"])
    if not co:
        artigos = [p.get("imagem_wikipedia")] + list((p.get("imagens_reel") or {}).get("artigos") or [])
        co = coord_wikidata([a for a in artigos if a])
        if not co:
            onde = (ex.get("visitar") or {}).get("lugar", "") + ", " + (cat.get("local") or p.get("subtitulo", "").split("·")[0])
            co = coord_nominatim(f"{onde}, {cat.get('pais', '')}".strip(", ")) or coord_nominatim(
                f"{cat.get('local', '')}, {cat.get('pais', '')}") or ex.get("coordenadas_aprox")
        if co:
            cc[m["id"]] = co
    m["coord"] = co
    # fotos (só fotografias e obras reais; ilustração de IA não entra na galeria)
    fotos = []
    if p.get("imagem") and (pasta / p["imagem"]).exists():
        fotos.append({"src": f"../{dia}/{p['imagem']}", "credito": p.get("imagem_credito", ""), "pagina": ""})
    try:
        for e in json.loads((pasta / "reel_imagens.json").read_text()):
            if e.get("origem") == "commons" and (pasta / e["arquivo"]).exists():
                fotos.append({"src": f"../{dia}/{e['arquivo']}", "credito": e.get("credito", ""), "pagina": e.get("pagina", "")})
    except Exception:
        pass
    m["fotos"] = fotos
    m["capa"] = fotos[0]["src"] if fotos else (f"../{dia}/card_01.jpg" if (pasta / "card_01.jpg").exists() else "")
    # vídeos
    vc = cache.setdefault("videos", {})
    vids = []
    for v in list(p.get("videos") or []) + list(ex.get("videos") or []):
        vid = video_id(v if isinstance(v, str) else (v or {}).get("url", ""))
        if vid and vid not in [x["id"] for x in vids]:
            info = video_info(vid, vc)
            if info:
                vids.append({"id": vid, **info})
    m["videos"] = vids[:3]
    m["visitar"] = p.get("visitar") or ex.get("visitar") or {"lugar": "", "cidade": cat.get("local", "")}
    m["permalink"] = m["meta"].get("feed_permalink") or PERFIL
    return m


# ------------------------------------------------------------------ páginas
def topo(raiz_rel, direita=""):
    return (f'<div class="top"><a href="{raiz_rel}index.html"><img src="{raiz_rel}brand/logo_avatar_claro_1080.png" alt=""></a>'
            f'<div><b>ACTA DEI</b><br><span>Mapa dos milagres</span></div>{direita}</div>')


def pagina_milagre(m, todos):
    p, cat = m["post"], m["cat"]
    st = p.get("status")
    badge = f'<span class="badge{" inv" if st == "investigacao" else ""}">{esc(STATUS[st])}</span>' if st in STATUS else ""
    if p.get("relato_completo"):
        relato = "".join(f"<p>{esc(x.strip())}</p>" for x in p["relato_completo"].split("\n\n") if x.strip())
    else:
        relato = ""
        for c in p.get("cards", []):
            k = (c.get("kicker") or "").split(" · ")[0]
            relato += f'<h3 class="cz">{esc(k)}</h3>' + "".join(f"<p>{esc(x.strip())}</p>" for x in c.get("texto", "").split("\n\n") if x.strip())
    tem_inv = any("INVESTIGA" in (c.get("kicker") or "").upper() for c in p.get("cards", []))
    inv = cat.get("investigacao") if not p.get("relato_completo") and not tem_inv else ""
    decisao = "".join(f"<p>{esc(x.strip())}</p>" for x in p.get("decisao", "").split("\n\n") if x.strip())
    fotos = "".join(f'<figure><a href="{esc(f["src"])}"><img src="{esc(f["src"])}" alt="" loading="lazy"></a><figcaption>'
                    + (f'<a href="{esc(f["pagina"])}">{esc(f["credito"])}</a>' if f["pagina"] else esc(f["credito"]))
                    + "</figcaption></figure>" for f in m["fotos"])
    videos = "".join(f'<a class="vid" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener">'
                     f'<img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" alt="" loading="lazy"><span class="play">▶</span>'
                     f'<b>{esc(v["titulo"])}</b><i>{esc(v["canal"])} · YouTube</i></a>' for v in m["videos"])
    links = p.get("fontes_links") or []
    fontes = "".join(f'<li>{f"<a href={chr(34)}{esc(links[i])}{chr(34)}>{esc(f)}</a>" if i < len(links) and links[i] else esc(f)}</li>'
                     for i, f in enumerate(p.get("fontes", [])))
    vis = m["visitar"]
    q = urllib.parse.quote_plus(f"{vis.get('lugar', '')} {vis.get('cidade', '')}".strip())
    lat, lon = (m["coord"] or [None, None])
    mini = (f'<div id="mini"></div><script>var mm=L.map("mini",{{scrollWheelZoom:false,zoomControl:true}}).setView([{lat},{lon}],15);'
            f'L.tileLayer("https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png",{{attribution:"&copy; OpenStreetMap",maxZoom:19}}).addTo(mm);'
            f'L.marker([{lat},{lon}],{{icon:CRUZ}}).addTo(mm);</script>') if lat is not None else ""
    outros = "".join(f'<a href="{o["id"]}.html">{esc(o["post"]["titulo"])}</a>' for o in todos if o["id"] != m["id"])
    css = BASE_CSS + """
main{max-width:860px;margin:0 auto;padding:0 18px}
.hero{position:relative;margin:0 -18px}.hero img{width:100%;max-height:520px;object-fit:cover;display:block}
.hero small{position:absolute;right:10px;bottom:8px;background:rgba(38,34,30,.7);color:#E6DFD2;font-size:13px;padding:2px 8px;border-radius:3px;max-width:80%}
h1{font-family:Cinzel,serif;font-size:34px;line-height:1.2;margin:26px 0 6px}.sub{color:var(--grey);font-style:italic;font-size:21px;margin:6px 0 4px}
h2{font-family:Cinzel,serif;font-size:19px;letter-spacing:3px;color:var(--red);border-top:2px solid var(--red);padding-top:18px;margin:44px 0 12px}
h3{font-size:14px;letter-spacing:3px;color:var(--red);margin:26px 0 6px}
.dec{background:#EFE6D6;border-left:4px solid var(--red);padding:6px 20px;font-weight:600}
.fotos{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px}.fotos figure{margin:0}
.fotos img{width:100%;height:200px;object-fit:cover;display:block;border:1px solid var(--line)}.fotos figcaption{font-size:14px;color:var(--grey);line-height:1.3;margin-top:4px}
.vids{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}
.vid{position:relative;display:block;text-decoration:none;color:var(--char)}.vid img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}
.vid .play{position:absolute;left:50%;top:28%;transform:translate(-50%,-50%);background:rgba(166,25,46,.92);color:#fff;width:54px;height:54px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px}
.vid b{display:block;font-size:18px;line-height:1.25;margin-top:6px}.vid i{font-size:15px;color:var(--grey)}
.nota{font-size:15px;color:var(--grey);font-style:italic}
#mini{height:280px;border:1px solid var(--line);margin-top:10px}
.btn{display:inline-block;background:var(--red);color:var(--cream);text-decoration:none;font-family:Cinzel,serif;font-size:14px;letter-spacing:2px;padding:12px 18px;border-radius:5px;margin:6px 8px 0 0}
.btn.sec{background:none;color:var(--red);border:2px solid var(--red)}
.outros a{display:inline-block;margin:4px 14px 4px 0}
ul.fontes{padding-left:20px}ul.fontes li{margin:4px 0}
@media(max-width:600px){h1{font-size:27px}body{font-size:19px}}
"""
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(p['titulo'])} · Acta Dei</title><meta name="description" content="{esc(cat.get('resumo', p.get('subtitulo', '')))}">
<meta property="og:title" content="{esc(p['titulo'])}"><meta property="og:image" content="{esc(m['capa'])}">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>{FONTES_CSS}{css}</style></head><body>
{topo("../../", '<a class="dir" href="index.html">← VOLTAR AO MAPA</a>')}
<main>
{f'<div class="hero"><img src="{esc(m["capa"])}" alt=""><small>{esc(m["fotos"][0]["credito"])}</small></div>' if m["fotos"] else ''}
<h1>{esc(p['titulo'])}</h1>{badge}<div class="sub">{esc(p.get('subtitulo', ''))}</div>
<h2>O RELATO</h2>{relato}
{f'<h3 class="cz">A INVESTIGAÇÃO</h3><p>{esc(inv)}</p>' if inv and inv not in relato else ''}
<h2>O QUE A SANTA IGREJA CATÓLICA DECIDIU</h2><div class="dec">{decisao}</div>
{f'<h2>FOTOS</h2><div class="fotos">{fotos}</div><p class="nota">Imagens do Wikimedia Commons, em domínio público ou Creative Commons, com crédito ao autor.</p>' if fotos else ''}
{f'<h2>VÍDEOS</h2><div class="vids">{videos}</div><p class="nota">Vídeos públicos do YouTube, de canais de terceiros. Abrem no YouTube.</p>' if videos else ''}
<h2>COMO VISITAR</h2><p><b>{esc(vis.get('lugar', ''))}</b><br>{esc(vis.get('cidade', ''))}</p>
<a class="btn sec" href="https://www.google.com/maps/search/?api=1&query={q}" target="_blank" rel="noopener">ABRIR NO GOOGLE MAPS</a>
{mini}
<h2>FONTES</h2><ul class="fontes">{fontes}</ul>
<p style="margin-top:34px"><a class="btn" href="{esc(m['permalink'])}" target="_blank" rel="noopener">VER O POST NO INSTAGRAM</a><a class="btn sec" href="index.html">TODOS OS MILAGRES NO MAPA</a></p>
{f'<h2>OUTROS MILAGRES</h2><div class="outros">{outros}</div>' if outros else ''}
</main><footer>Acta Dei · Mysterium Fidei · @actadei.oficial<br>Publicado no perfil em {m['dia'][8:10]}/{m['dia'][5:7]}/{m['dia'][:4]}</footer>
</body></html>"""


CRUZ_JS = """var CRUZ=L.divIcon({className:'cruz',iconSize:[26,34],iconAnchor:[13,30],popupAnchor:[0,-28],
html:'<svg viewBox="0 0 26 34" width="26" height="34"><path d="M10 2h6v8h8v6h-8v16h-6V16H2v-6h8z" fill="#A6192E" stroke="#F7F2E8" stroke-width="2"/></svg>'});"""


def pagina_mapa(ms):
    pontos = [{"id": m["id"], "t": m["post"]["titulo"], "s": m["post"].get("subtitulo", ""), "c": m["coord"],
               "f": m["capa"], "st": m["post"].get("status") or ""} for m in ms if m["coord"]]
    lista = "".join(f'<a class="item" href="{m["id"]}.html"><img src="{esc(m["capa"])}" alt="" loading="lazy"><div><b>{esc(m["post"]["titulo"])}</b>'
                    f'<i>{esc(m["post"].get("subtitulo", ""))}</i></div></a>' for m in sorted(ms, key=lambda x: x["dia"], reverse=True))
    css = BASE_CSS + """
#mapa{height:calc(100vh - 72px);min-height:420px;background:#EDE7DB}
.leaflet-popup-content-wrapper{border-radius:8px;padding:0;overflow:hidden;background:var(--cream)}.leaflet-popup-content{margin:0;width:260px!important}
.card img{width:100%;height:140px;object-fit:cover;display:block}.card div{padding:10px 14px 12px;font-family:'Cormorant Garamond',serif}
.card b{display:block;font-family:Cinzel,serif;font-size:14px;line-height:1.3;color:var(--char)}.card i{display:block;color:var(--grey);font-size:15px;margin:3px 0 6px}
.card .badge{font-size:9px}.card .ver{display:block;margin-top:8px;font-family:Cinzel,serif;font-size:12px;letter-spacing:2px;color:var(--red)}
.leaflet-container a.card{color:var(--char)}
.cruz{background:none;border:0}.cruz svg{filter:drop-shadow(0 2px 3px rgba(0,0,0,.35));transition:transform .15s}.cruz:hover svg{transform:scale(1.25)}
.lista{max-width:900px;margin:0 auto;padding:30px 18px}.lista h2{font-family:Cinzel,serif;letter-spacing:3px;font-size:18px;color:var(--red)}
.item{display:flex;gap:14px;align-items:center;padding:10px 0;border-top:1px solid var(--line);text-decoration:none;color:var(--char)}
.item img{width:84px;height:64px;object-fit:cover;flex:none}.item b{display:block;font-family:Cinzel,serif;font-size:15px}.item i{color:var(--grey);font-size:16px}
.leg{position:absolute;z-index:500;left:12px;bottom:22px;background:rgba(247,242,232,.94);padding:8px 12px;border-radius:6px;font-size:15px;box-shadow:0 2px 8px rgba(0,0,0,.2)}
"""
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mapa dos milagres · Acta Dei</title><meta name="description" content="Os milagres reconhecidos pela Santa Igreja Católica publicados pelo Acta Dei, no mapa.">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>{FONTES_CSS}{css}</style></head><body>
{topo("../../", f'<span class="dir">{len(pontos)} MILAGRES</span>')}
<div style="position:relative"><div id="mapa"></div><div class="leg">✚ Passe o mouse (ou toque) numa cruz · clique para abrir</div></div>
<section class="lista"><h2>TODOS OS MILAGRES DO MAPA</h2>{lista}</section>
<footer>Acta Dei · Mysterium Fidei · @actadei.oficial · Mapa: © colaboradores do OpenStreetMap</footer>
<script>
{CRUZ_JS}
var P={json.dumps(pontos, ensure_ascii=False)};
var mapa=L.map('mapa',{{worldCopyJump:true}});
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{attribution:'&copy; OpenStreetMap',maxZoom:19}}).addTo(mapa);
var hover=window.matchMedia('(hover: hover)').matches, b=[];
function e(s){{return (s||'').replace(/[&<>"]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]}})}}
P.forEach(function(p){{
  var st=p.st==='reconhecido'?'<span class="badge">Reconhecido</span>':(p.st==='investigacao'?'<span class="badge inv">Em investigação</span>':'');
  var html='<a class="card" href="'+p.id+'.html" style="text-decoration:none">'+(p.f?'<img src="'+e(p.f)+'" alt="">':'')+'<div><b>'+e(p.t)+'</b><i>'+e(p.s)+'</i>'+st+'<span class="ver">VER DETALHES →</span></div></a>';
  var mk=L.marker(p.c,{{icon:CRUZ,title:p.t}}).addTo(mapa).bindPopup(html,{{closeButton:!hover,autoPan:true}});
  if(hover){{mk.on('mouseover',function(){{mk.openPopup()}});mk.on('click',function(){{location.href=p.id+'.html'}});}}
  b.push(p.c);
}});
if(b.length>1){{mapa.fitBounds(b,{{padding:[60,60],maxZoom:6}})}}else if(b.length){{mapa.setView(b[0],6)}}else{{mapa.setView([42,12],4)}}
</script></body></html>"""


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    cp = SAIDA / "cache.json"
    try:
        cache = json.loads(cp.read_text())
    except Exception:
        cache = {}
    ms = [preparar(m, cache) for m in coletar()]
    cp.write_text(json.dumps(cache, ensure_ascii=False, indent=1))
    for m in ms:
        (SAIDA / f"{m['id']}.html").write_text(pagina_milagre(m, ms).replace("<script>var mm", "<script>" + CRUZ_JS + "var mm"))
    (SAIDA / "index.html").write_text(pagina_mapa(ms))
    sem = [m["id"] for m in ms if not m["coord"]]
    print(f"mapa: {len(ms)} milagres, {len(ms) - len(sem)} no mapa" + (f" (sem coordenadas: {', '.join(sem)})" if sem else ""))


if __name__ == "__main__":
    main()
