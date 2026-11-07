#!/usr/bin/env python3
"""Projeta o cronograma dos próximos dias (posts/_cronograma.json): o que vai ao feed em cada data
(santo do dia, milagre da fila ou celebração), o santo do story da manhã e os "também hoje".

É uma previsão: segue as mesmas regras da tarefa diária (dia ímpar = santo; par = milagre da fila;
datas fortes e domingos = celebração; caso com data_sugerida vai para o dia par mais próximo dela).
A tarefa diária pode trocar um caso se as fontes não confirmarem. Reescrito a cada build.
Uso: python3 scripts/build_cronograma.py [dias=30]
"""
import datetime as dt, json, sys
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent
ORDEM = {"S": 0, "F": 1, "M": 2, "BR": 3, "m": 4, "MR": 5}
EXCECOES = {"01-01", "01-06", "02-02", "03-19", "03-25", "06-24", "06-29", "08-15", "10-12", "11-01", "11-02", "12-08", "12-12", "12-25"}


def main(dias=30):
    santos = json.loads((RAIZ / "data/santos.json").read_text())["dias"]
    fila = json.loads((RAIZ / "data/fila.json").read_text())["fila"]
    hoje = dt.datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    datas = [hoje + dt.timedelta(days=i) for i in range(dias)]

    def tipo_dia(d):
        if d.strftime("%m-%d") in EXCECOES or d.weekday() == 6:
            return "celebracao"
        return "santo" if d.day % 2 == 1 else "milagre"

    dias_milagre = [d for d in datas if tipo_dia(d) == "milagre"]
    # 1) casos com data sugerida dentro da janela ocupam o dia de milagre mais próximo da data
    alocado, livres = {}, list(dias_milagre)
    for item in fila:
        ds = item.get("data_sugerida")
        if not ds or not livres:
            continue
        alvo = dt.date(hoje.year, int(ds[:2]), int(ds[3:]))
        if alvo < hoje - dt.timedelta(days=3):
            alvo = dt.date(hoje.year + 1, alvo.month, alvo.day)
        if alvo > datas[-1] + dt.timedelta(days=3):
            continue
        melhor = min(livres, key=lambda d: abs((d - alvo).days))
        if abs((melhor - alvo).days) <= 3:
            alocado[melhor] = item; livres.remove(melhor)
    # 2) os demais, na ordem da fila
    resto = [i for i in fila if i not in alocado.values()]
    for d in livres:
        if resto:
            alocado[d] = resto.pop(0)

    out = []
    for d in datas:
        ents = sorted(santos.get(d.strftime("%m-%d")) or [], key=lambda e: ORDEM.get(e.get("grau", "MR"), 9))
        santo = ents[0]["nome"] if ents else ""
        tambem = [e["nome"] for e in ents[1:3]]
        t = tipo_dia(d)
        if t == "milagre":
            m = alocado.get(d)
            feed = m["titulo"] if m else "(fila vazia: santo do dia)"
            feed_id = m["id"] if m else None
        else:
            feed, feed_id = santo, None
        out.append({"data": d.isoformat(), "dia_semana": ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"][d.weekday()],
                    "tipo": t, "feed": feed, "id_milagre": feed_id, "santo_story": santo, "tambem_hoje": tambem})
    (RAIZ / "posts/_cronograma.json").write_text(json.dumps({"gerado_em": hoje.isoformat(), "dias": out}, ensure_ascii=False, indent=2))
    print(f"cronograma: {len(out)} dias a partir de {hoje}")
    return out


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
