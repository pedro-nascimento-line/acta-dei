#!/usr/bin/env python3
"""Monta data/fila.json: os próximos 40 milagres a publicar, na rotação de pilares, sem repetir os já publicados.

Rotação semanal (dias pares do mês = milagre no feed; dias ímpares = santo do dia no feed):
  eucaristico → canonizacao → aparicao → canonizacao → brasil (tag) → incorrupto/lourdes (alternando) → canonizacao …
Um caso com 'data_sugerida' dentro dos próximos 45 dias pula para perto daquela data.
Uso: python3 scripts/build_fila.py  (a tarefa diária consome o primeiro item e roda este script de novo).
"""
import datetime as dt, json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
dados = json.loads((RAIZ / "data/milagres.json").read_text())["milagres"]
publicados = {json.loads(p.read_text()).get("id_milagre") for p in (RAIZ / "posts").glob("*/post.json")}
cand = [x for x in dados if x["id"] not in publicados]

hoje = dt.date.today()
def dias_ate(md):
    if not md:
        return 999
    m, d = map(int, md.split("-"))
    for ano in (hoje.year, hoje.year + 1):
        try:
            alvo = dt.date(ano, m, d)
        except ValueError:
            continue
        if alvo >= hoje:
            return (alvo - hoje).days
    return 999

ROTACAO = ["eucaristico", "canonizacao", "aparicao", "canonizacao", "brasil", "incorrupto", "canonizacao", "lourdes"]
fila, usados, i = [], set(), 0
while len(fila) < 40 and len(usados) < len(cand):
    tipo = ROTACAO[i % len(ROTACAO)]; i += 1
    pool = [x for x in cand if x["id"] not in usados and (("brasil" in x["tags"]) if tipo == "brasil" else x["tipo"] == tipo)]
    if not pool:
        pool = [x for x in cand if x["id"] not in usados]
    # prioriza data sugerida próxima; depois ordem do banco
    pool.sort(key=lambda x: (dias_ate(x.get("data_sugerida")) > 45, dias_ate(x.get("data_sugerida"))))
    esc = pool[0]; usados.add(esc["id"])
    fila.append({"id": esc["id"], "tipo": esc["tipo"], "titulo": esc["titulo"], "data_sugerida": esc.get("data_sugerida")})

(RAIZ / "data/fila.json").write_text(json.dumps({"gerada_em": hoje.isoformat(), "fila": fila}, ensure_ascii=False, indent=1))
print(f"fila com {len(fila)} itens; primeiros:", [f["id"] for f in fila[:8]])

# projeção dos próximos 30 dias (posts/_cronograma.json), usada na agenda do Pedro
try:
    import build_cronograma
    build_cronograma.main(30)
except Exception as e:  # nunca derruba o build por causa da previsão
    print(f"cronograma falhou: {e}")
