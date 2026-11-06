#!/usr/bin/env python3
"""Publica o conteúdo do dia no Instagram pela API oficial (Instagram API with Instagram Login).

Uso (no GitHub Actions):
  python3 scripts/publish.py --slot manha   # 7h BRT: carrossel + story da manhã + comentário com hashtags
  python3 scripts/publish.py --slot tarde   # 13h BRT: story da tarde
  python3 scripts/publish.py --slot noite   # 20h BRT: story da noite
  python3 scripts/publish.py --slot auto    # decide pelo horário UTC
  python3 scripts/publish.py --refresh-token

Variáveis de ambiente (Secrets do repositório):
  IG_ACCESS_TOKEN  token: de usuário do Instagram (60 dias, host graph.instagram.com) OU de usuário do sistema
                   do portfólio empresarial (não expira, host graph.facebook.com)
  IG_USER_ID       ID numérico da conta profissional do Instagram
  IG_API_HOST      opcional: "graph.instagram.com" (padrão) ou "graph.facebook.com" (token de usuário do sistema)
  PAGES_BASE       ex.: https://actadei.github.io/acta-dei   (URL pública do GitHub Pages)
  HASHTAGS_COMENTARIO  opcional: "true" publica as hashtags no primeiro comentário (exige a permissão
                   instagram_manage_comments no token). Padrão: hashtags no fim da legenda.

Regras: nunca publica duas vezes a mesma peça do mesmo dia (confere meta.json); cada execução publica o slot
pedido e o que ficou pendente dos slots anteriores do dia; espera as imagens estarem acessíveis no Pages;
tenta até 3 vezes com 5 min de intervalo; grava tudo em log/publicacoes.csv.
"""
import argparse, csv, datetime as dt, json, os, sys, time
from pathlib import Path
from zoneinfo import ZoneInfo
import requests

HOST = os.environ.get("IG_API_HOST", "graph.instagram.com").strip()
API = f"https://{HOST}/v21.0"
RAIZ = Path(__file__).resolve().parent.parent
BRT = ZoneInfo("America/Sao_Paulo")
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
USER = os.environ.get("IG_USER_ID", "")
BASE = os.environ.get("PAGES_BASE", "").rstrip("/")


def log(slot, tipo, ig_id, status, erro=""):
    agora = dt.datetime.now(BRT)
    with open(RAIZ / "log/publicacoes.csv", "a", newline="") as f:
        csv.writer(f).writerow([agora.date().isoformat(), agora.strftime("%H:%M"), slot, tipo, ig_id, status, erro[:200]])


def api(method, path, **params):
    params["access_token"] = TOKEN
    r = requests.request(method, f"{API}/{path}", params=params, timeout=60)
    try:
        data = r.json()
    except ValueError:
        data = {"raw": r.text}
    if r.status_code >= 400 or "error" in data:
        raise RuntimeError(f"{path}: {data.get('error', data)}")
    return data


def esperar_container(cid, timeout=300):
    """Espera o container ficar FINISHED (a Meta baixa e processa a imagem)."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        st = api("GET", cid, fields="status_code,status")
        if st.get("status_code") == "FINISHED":
            return True
        if st.get("status_code") == "ERROR":
            raise RuntimeError(f"container {cid} com erro: {st.get('status')}")
        time.sleep(8)
    raise RuntimeError(f"container {cid} não finalizou em {timeout}s")


def url_ok(url, tentativas=30, intervalo=30):
    """Confere se o Pages já está servindo o arquivo (até 15 min)."""
    for _ in range(tentativas):
        try:
            if requests.head(url, timeout=20).status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(intervalo)
    return False


def publicar_carrossel(dia, pasta, meta):
    cards = sorted(p.name for p in pasta.glob("card_*.jpg"))
    if not cards:
        raise RuntimeError("nenhum card_*.jpg na pasta do post")
    legenda = (pasta / "legenda.txt").read_text().strip()
    hashtags_p = pasta / "hashtags.txt"
    hashtags = hashtags_p.read_text().strip() if hashtags_p.exists() else ""
    no_comentario = os.environ.get("HASHTAGS_COMENTARIO", "").lower() == "true"
    if hashtags and not no_comentario:
        # hashtags no fim da legenda; se estourar 2.200, corta as últimas
        tags = hashtags.split()
        while tags and len(legenda) + 4 + len(" ".join(tags)) > 2200:
            tags.pop()
        if tags:
            legenda = legenda + "\n\n·\n" + " ".join(tags)
    if len(legenda) > 2200:
        raise RuntimeError(f"legenda com {len(legenda)} caracteres (limite 2200)")
    urls = [f"{BASE}/posts/{dia}/{c}" for c in cards]
    for u in urls:
        if not url_ok(u):
            raise RuntimeError(f"imagem não acessível no Pages: {u}")
    filhos = []
    for u in urls:
        c = api("POST", f"{USER}/media", image_url=u, is_carousel_item="true")
        esperar_container(c["id"]); filhos.append(c["id"])
    if len(filhos) == 1:
        cont = api("POST", f"{USER}/media", image_url=urls[0], caption=legenda)
    else:
        cont = api("POST", f"{USER}/media", media_type="CAROUSEL", children=",".join(filhos), caption=legenda)
    esperar_container(cont["id"])
    pub = api("POST", f"{USER}/media_publish", creation_id=cont["id"])
    meta["feed_id"] = pub["id"]
    log("manha", "carrossel", pub["id"], "ok")
    if hashtags and no_comentario:
        try:
            com = api("POST", f"{pub['id']}/comments", message=hashtags)
            meta["comentario_id"] = com["id"]; log("manha", "comentario", com["id"], "ok")
        except Exception as e:  # o post já saiu; o comentário não é crítico
            log("manha", "comentario", "", "falha", str(e))
    return pub["id"]


def publicar_story(dia, pasta, meta, slot):
    arq = pasta / f"story_{slot}.jpg"
    if not arq.exists():
        raise RuntimeError(f"{arq.name} não existe")
    u = f"{BASE}/posts/{dia}/{arq.name}"
    if not url_ok(u):
        raise RuntimeError(f"story não acessível no Pages: {u}")
    c = api("POST", f"{USER}/media", image_url=u, media_type="STORIES")
    esperar_container(c["id"])
    pub = api("POST", f"{USER}/media_publish", creation_id=c["id"])
    meta[f"story_{slot}_id"] = pub["id"]
    log(slot, "story", pub["id"], "ok")
    return pub["id"]


def publicar_slot(s, dia, pasta, meta):
    """Publica as peças de um slot que ainda não têm id no meta.json (nada sai duas vezes)."""
    if s == "manha":
        if not meta.get("feed_id"):
            publicar_carrossel(dia, pasta, meta)
        if not meta.get("story_manha_id"):
            try:
                publicar_story(dia, pasta, meta, "manha")
            except Exception as e:  # o carrossel já saiu; o story não derruba a execução
                log("manha", "story", "", "falha", str(e))
    elif not meta.get(f"story_{s}_id"):
        publicar_story(dia, pasta, meta, s)


def slot_auto():
    h = dt.datetime.now(BRT).hour
    return "manha" if h < 11 else "tarde" if h < 17 else "noite"


def refresh_token():
    if HOST != "graph.instagram.com":
        print(TOKEN); return  # token de usuário do sistema não expira: devolve o mesmo
    d = requests.get("https://graph.instagram.com/refresh_access_token",
                     params={"grant_type": "ig_refresh_token", "access_token": TOKEN}, timeout=60).json()
    if "access_token" not in d:
        raise RuntimeError(f"refresh falhou: {d}")
    print(d["access_token"])  # o workflow grava no secret via gh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", default="auto")
    ap.add_argument("--dia", default=dt.datetime.now(BRT).date().isoformat())
    ap.add_argument("--refresh-token", action="store_true")
    a = ap.parse_args()
    if a.refresh_token:
        return refresh_token()
    if not (TOKEN and USER and BASE):
        sys.exit("faltam IG_ACCESS_TOKEN, IG_USER_ID ou PAGES_BASE")
    slot = slot_auto() if a.slot == "auto" else a.slot
    pasta = RAIZ / "posts" / a.dia
    if not pasta.exists():
        log(slot, "-", "", "sem_post", f"pasta posts/{a.dia} não existe"); sys.exit("sem post para hoje")
    meta_p = pasta / "meta.json"
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
    # cada execução publica o slot pedido E o que ficou pendente dos slots anteriores do dia
    # (se o cron das 7h atrasar ou falhar, o das 13h publica o carrossel antes do story da tarde)
    ordem = ["manha", "tarde", "noite"]
    alvo = ordem[: ordem.index(slot) + 1]
    pecas = {"manha": ["feed_id", "story_manha_id"], "tarde": ["story_tarde_id"], "noite": ["story_noite_id"]}
    pendentes = [k for s_ in alvo for k in pecas[s_] if not meta.get(k)]
    if not pendentes:
        print(f"{slot}: tudo já publicado"); return
    print(f"{slot}: pendente -> {', '.join(pendentes)}")
    erro = ""
    for tentativa in range(1, 4):
        try:
            for s_ in alvo:
                publicar_slot(s_, a.dia, pasta, meta)
            erro = ""; break
        except Exception as e:
            erro = str(e); log(slot, "-", "", f"tentativa_{tentativa}", erro)
            time.sleep(300)
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    if erro:
        sys.exit(f"falhou após 3 tentativas: {erro}")


if __name__ == "__main__":
    main()
