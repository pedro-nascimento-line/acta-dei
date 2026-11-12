#!/usr/bin/env python3
"""Mantém a estante de música de fundo dos Reels: 5 cantos gregorianos calmos, escolhidos a dedo no
Wikimedia Commons (coro ou schola, sem instrumentos, sem sinos), com a licença conferida na hora do download.
Fica em posts/_musica/ (versionada, baixada uma vez). Os Reels alternam entre elas, uma por dia.

Uso: python3 scripts/fetch_music.py            # baixa o que faltar da lista CURADAS e tira o resto
     python3 scripts/fetch_music.py --lista    # mostra o que há
Só aceita as mesmas licenças das imagens (commons.py): domínio público, CC0, CC BY, CC BY-SA.
Para trocar uma faixa, troque o título em CURADAS: na próxima geração de artes a estante se ajusta sozinha.
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import commons  # noqa: E402
from av import duracao, VETO_MUSICA  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "posts" / "_musica"
INDICE = PASTA / "musica.json"

# (título exato no Commons, nome curto para o crédito). Conferidas em 12/11/2026: licença, duração e intérprete.
CURADAS = [
    ("File:The Tudor Consort - 02 - Introit - Resurrexi et Adhuc Tecum Sum.ogg", "Introito Resurrexi · The Tudor Consort"),
    ("File:The Tudor Consort - 07 - Gradual - Haec Dies.ogg", "Gradual Haec dies · The Tudor Consort"),
    ("File:The Tudor Consort - 08 - Alleluia - Pascha Nostrum.ogg", "Aleluia Pascha nostrum · The Tudor Consort"),
    ("File:Schola Gregoriana-Antiphona et Magnificat.ogg", "Antífona e Magnificat · Schola Gregoriana (Ołtarzew)"),
    ("File:Pange Lingua Latin in Latin.ogg", "Pange lingua · Gareth Hughes"),
]
MIN_S, MAX_S = 60, 900


def nome_arquivo(i, title):
    ext = Path(title).suffix.lower() or ".ogg"
    return f"gregoriano_{i:02d}{ext}"


def main(listar=False):
    PASTA.mkdir(parents=True, exist_ok=True)
    antiga = json.loads(INDICE.read_text()) if INDICE.exists() else []
    por_titulo = {e["title"]: e for e in antiga if (PASTA / e["arquivo"]).exists()}
    estante = []
    for i, (title, curto) in enumerate(CURADAS, start=1):
        if VETO_MUSICA.search(title):
            print(f"  vetada pela regra de sinos: {title}"); continue
        e = por_titulo.get(title)
        if not e:
            if listar:
                print(f"  falta baixar: {title}"); continue
            try:
                info = commons.info(title)
            except Exception as ex:
                print(f"  consulta falhou: {title[:60]}: {ex}"); continue
            if not info or not info["licenca_ok"]:
                print(f"  licença não aceita ou arquivo sumiu: {title}"); continue
            destino = PASTA / nome_arquivo(i, title)
            try:
                destino.write_bytes(commons._req(info["url_original"]).content)
            except Exception as ex:
                print(f"  download falhou: {title[:60]}: {ex}"); continue
            seg = duracao(destino)
            if not (MIN_S <= seg <= MAX_S):
                print(f"  descartada ({seg:.0f}s): {title[:60]}"); destino.unlink(); continue
            e = {"arquivo": destino.name, "segundos": round(seg, 1), "title": title,
                 "licenca": info["licenca"], "autor": info["autor"], "pagina": info["pagina"]}
            print(f"  + {destino.name}: {curto} · {info['licenca']} · {seg:.0f}s")
        e["nome"] = curto
        estante.append(e)
    if not listar:
        # tira da pasta tudo o que não está mais na lista (faixas antigas, sinos, órgão)
        manter = {e["arquivo"] for e in estante} | {INDICE.name}
        for f in PASTA.iterdir():
            if f.is_file() and f.name not in manter:
                print(f"  - removida da estante: {f.name}"); f.unlink()
        INDICE.write_text(json.dumps(estante, ensure_ascii=False, indent=2))
    for e in estante:
        print(f"{e['arquivo']:20} {e['segundos']:6.0f}s  {e['licenca']:12} {e['nome']}")
    print(f"estante: {len(estante)} de {len(CURADAS)} faixas")


if __name__ == "__main__":
    main(listar="--lista" in sys.argv)
