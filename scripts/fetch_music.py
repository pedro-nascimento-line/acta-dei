#!/usr/bin/env python3
"""Monta e mantém a estante de música sacra dos Reels: gravações de domínio público / CC0 / CC BY(-SA)
do Wikimedia Commons, com a licença registrada. Fica em posts/_musica/ (versionada, baixada uma vez).

Uso: python3 scripts/fetch_music.py            # completa a estante até ALVO faixas
     python3 scripts/fetch_music.py --lista    # mostra o que há
Só aceita as mesmas licenças das imagens (commons.py). Rejeita NC, ND e 'fair use'.
"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import commons  # noqa: E402
from av import duracao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "posts" / "_musica"
INDICE = PASTA / "musica.json"
ALVO = 6
TERMOS = [
    "gregorian chant", "canto gregoriano", "Kyrie gregorian chant", "Salve Regina chant",
    "Ave Maria gregorian", "Veni Creator Spiritus chant", "Pange lingua chant", "Tantum ergo chant",
    "Te Deum chant", "Magnificat gregorian", "Ave Maris Stella chant", "Adoro te devote",
]
MIN_S, MAX_S = 40, 900


def buscar_audio(termo, n=20):
    d = commons._get({"action": "query", "list": "search", "srsearch": f"{termo} filetype:audio",
                      "srnamespace": 6, "srlimit": n})
    titulos = [h["title"] for h in d["query"]["search"]]
    return [i for i in commons.info_batch(titulos) if (i.get("mime") or "").startswith("audio/") and i["licenca_ok"]]


def main(listar=False):
    PASTA.mkdir(parents=True, exist_ok=True)
    estante = json.loads(INDICE.read_text()) if INDICE.exists() else []
    estante = [e for e in estante if (PASTA / e["arquivo"]).exists()]
    if listar or len(estante) >= ALVO:
        for e in estante:
            print(f"{e['arquivo']:28} {e['segundos']:6.0f}s  {e['licenca']:14} {e['title'][:60]}")
        print(f"{len(estante)} faixas")
        return
    ja = {e["title"] for e in estante}
    for termo in TERMOS:
        if len(estante) >= ALVO:
            break
        try:
            cands = buscar_audio(termo)
        except Exception as e:
            print(f"busca '{termo}' falhou: {e}"); continue
        print(f"busca '{termo}': {len(cands)} candidatos com licença aceita")
        for i in cands:
            if len(estante) >= ALVO or i["title"] in ja:
                continue
            ext = Path(i["title"]).suffix.lower() or ".ogg"
            destino = PASTA / f"faixa_{len(estante) + 1:02d}{ext}"
            try:
                destino.write_bytes(commons._req(i["url_original"]).content)
            except Exception as e:
                print(f"  download falhou: {i['title'][:60]}: {e}"); continue
            seg = duracao(destino)
            if not (MIN_S <= seg <= MAX_S) or destino.stat().st_size > 25_000_000:
                print(f"  descartada ({seg:.0f}s, {destino.stat().st_size // 1000} kB): {i['title'][:60]}")
                destino.unlink(); continue
            estante.append({"arquivo": destino.name, "segundos": round(seg, 1), "title": i["title"],
                            "licenca": i["licenca"], "autor": i["autor"], "pagina": i["pagina"]})
            ja.add(i["title"])
            print(f"  + {destino.name}: {i['title'][:60]} · {i['licenca']} · {seg:.0f}s")
            INDICE.write_text(json.dumps(estante, ensure_ascii=False, indent=2))
    INDICE.write_text(json.dumps(estante, ensure_ascii=False, indent=2))
    print(f"estante: {len(estante)} faixas")


if __name__ == "__main__":
    main(listar="--lista" in sys.argv)
