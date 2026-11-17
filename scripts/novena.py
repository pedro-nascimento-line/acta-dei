#!/usr/bin/env python3
"""Novenas: carrossel de 4 cards publicado às 20h (junto com o story da noite) nos 9 dias antes de uma festa.

Cada novena é um arquivo data/novenas/<ano>-<id>.json com: id, titulo, periodo, inicio (AAAA-MM-DD do 1º dia),
jaculatoria (+ _fonte), oracao {titulo, texto [parágrafos], fonte}, hashtags e dias [9 x {intencao, titulo,
meditacao, fontes}]. Duas novenas podem correr em paralelo (ex.: São Miguel e Santa Teresinha): cada uma gera
os seus arquivos.

Gera, na pasta do post do dia: novena_<id>_01.jpg … _04.jpg, legenda_novena_<id>.txt, hashtags_novena_<id>.txt.
Cards (estilo carvão, moldura dupla): 1 capa (dia, 9 contas, intenção, jaculatória) · 2 como rezar (fixo) ·
3 meditação do dia (fato histórico/documental, com fontes) · 4 oração da novena (fixa).
Textos: só orações tradicionais de domínio público ou oficiais com a fonte; nunca o texto integral das leituras.

Teste: python3 scripts/novena.py posts/2026-12-01
"""
import datetime as dt, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import render as R  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
A, BG, FG, SUB = R.RED_VIVO, R.CHAR, R.CREAM, "#CFC7B8"
ORDINAL = ["1º", "2º", "3º", "4º", "5º", "6º", "7º", "8º", "9º"]

CSS_N = f"""
.nv {{ height:1350px; position:relative; background:{BG}; color:{FG}; }}
.nv .m1 {{ position:absolute; inset:40px; border:2px solid {A}; }}
.nv .m2 {{ position:absolute; inset:54px; border:1px solid {A}; opacity:.55; }}
.nv .in {{ position:absolute; inset:0; padding:120px 118px 150px; display:flex; flex-direction:column; }}
.nv .k {{ font-family:'Cinzel'; font-weight:700; font-size:24px; letter-spacing:6px; color:{A}; text-align:center; }}
.nv .t {{ font-family:'Cinzel'; font-weight:700; font-size:54px; line-height:1.15; text-align:center; margin-top:18px; }}
.nv .reg {{ width:110px; height:3px; background:{A}; margin:34px auto; flex:none; }}
.nv .p {{ font-size:44px; line-height:1.36; }}
.nv .p p + p {{ margin-top:.55em; }}
.nv .ft {{ font-family:'Cinzel'; font-size:20px; letter-spacing:3px; line-height:1.5; color:{SUB}; text-align:center; }}
.nv .rod {{ position:absolute; left:0; right:0; bottom:82px; display:flex; justify-content:center; gap:40px;
           font-family:'Cinzel'; font-size:20px; letter-spacing:4px; color:{A}; }}
.passos li {{ list-style:none; display:flex; gap:26px; align-items:flex-start; margin-top:26px; font-size:39px; line-height:1.3; }}
.passos li b {{ flex:none; width:58px; height:58px; border-radius:50%; border:2px solid {A}; color:{A}; font-family:'Cinzel';
               font-size:28px; display:flex; align-items:center; justify-content:center; margin-top:-2px; }}
.passos li span em {{ color:{SUB}; }}
.contas span {{ display:inline-block; width:24px; height:24px; border-radius:50%; margin:0 8px; border:2px solid {A}; }}
"""
# encolhe o texto do miolo se passar da moldura
AJUSTE = """() => { const box = document.querySelector('.in'), alvo = document.querySelector('.p, .passos, .capa');
  if (!box || !alvo) return; let fs = parseFloat(getComputedStyle(alvo).fontSize) || 40;
  while (box.scrollHeight > box.clientHeight + 2 && fs > 26) { fs -= 1; alvo.style.fontSize = fs + 'px'; } }"""


def ativas(dia):
    """[(novena, n_do_dia 1..9)] das novenas que têm o dia `dia` (date) entre os seus 9 dias."""
    out = []
    for f in sorted((RAIZ / "data/novenas").glob("*.json")):
        try:
            nv = json.loads(f.read_text())
            n = (dia - dt.date.fromisoformat(nv["inicio"])).days + 1
            if 1 <= n <= len(nv["dias"]):
                out.append((nv, n))
        except Exception as e:
            print(f"  novena {f.name} ignorada: {e}")
    return out


def _pagina(miolo, n, t):
    rod = f'<div class="rod"><span>ACTA DEI · MYSTERIUM FIDEI</span><span>{n:02d} / {t:02d}</span></div>'
    return f'<div class="page nv"><div class="m1"></div><div class="m2"></div><div class="in">{miolo}</div>{rod}</div>'


def cards(nv, n):
    d, esc, tot = nv["dias"][n - 1], R.esc, len(nv["dias"])
    contas = '<div class="contas" style="text-align:center">' + "".join(
        f'<span style="background:{A if i < n else "transparent"}"></span>' for i in range(tot)) + "</div>"
    capa = _pagina(f"""<div class="capa" style="flex:1;display:flex;flex-direction:column;justify-content:center;text-align:center">
      <img src="{R.AVATAR_DARK}" style="width:96px;display:block;margin:0 auto">
      <div class="k" style="margin-top:26px">{esc(nv['titulo'])}</div>
      <div style="font-size:30px;font-style:italic;color:{SUB};margin-top:10px">{esc(nv['periodo'])}</div>
      <div style="font-family:Cinzel;font-weight:700;font-size:120px;line-height:1;margin-top:64px">{ORDINAL[n-1]} DIA</div>
      <div style="margin-top:30px">{contas}</div>
      <div style="font-size:40px;font-style:italic;color:{SUB};margin-top:54px">Intenção: {esc(d['intencao'][0].lower() + d['intencao'][1:])}</div>
      <div class="reg"></div>
      <div style="font-size:70px;line-height:1.22;font-style:italic;font-weight:500">“{esc(nv['jaculatoria'])}”</div>
      <div class="ft" style="margin-top:40px">{esc(nv['jaculatoria_fonte']).upper()}</div>
      <div style="font-size:30px;font-style:italic;color:{SUB};margin-top:46px">Deslize para rezar o dia de hoje →</div></div>""", 1, 4)
    como = _pagina(f"""<div class="k">PRIMEIRA VEZ? É ASSIM</div><div class="t">Como rezar a novena</div><div class="reg"></div>
      <div style="font-size:34px;font-style:italic;color:{SUB};text-align:center;margin-top:-6px">Novena: a mesma oração por nove dias seguidos, pedindo uma graça. Leva uns 5 minutos.</div>
      <ul class="passos" style="margin-top:24px">
       <li><b>1</b><span>Faça o sinal da cruz <em>(em nome do Pai, do Filho e do Espírito Santo)</em>.</span></li>
       <li><b>2</b><span>Leia a meditação do dia <em>(card 3)</em>.</span></li>
       <li><b>3</b><span>Reze a oração da novena <em>(card 4)</em>.</span></li>
       <li><b>4</b><span>Reze um Pai-Nosso, uma Ave-Maria e um Glória.</span></li>
       <li><b>5</b><span>Peça em silêncio a sua intenção.</span></li>
       <li><b>6</b><span>Termine com a jaculatória da capa e o sinal da cruz.</span></li></ul>
      <div style="font-size:31px;font-style:italic;color:{SUB};text-align:center;margin-top:auto">Perdeu um dia? Continue de onde parou.</div>""", 2, 4)
    med = _pagina(f"""<div class="k">MEDITAÇÃO DO {ORDINAL[n-1]} DIA</div><div class="t">{esc(d['titulo'])}</div><div class="reg"></div>
      <div class="p">{R.paras(d['meditacao'])}</div>
      <div class="ft" style="margin-top:auto;padding-top:30px">FONTES: {esc(d['fontes']).upper()}</div>""", 3, 4)
    ora = nv["oracao"]
    orac = _pagina(f"""<div class="k">ORAÇÃO DA NOVENA · TODOS OS DIAS</div><div class="t">{esc(ora['titulo'])}</div><div class="reg"></div>
      <div class="p" style="font-style:italic;font-size:42px;text-align:center">{''.join(f'<p>{esc(x)}</p>' for x in ora['texto'])}</div>
      <div class="ft" style="margin-top:auto;padding-top:30px">{esc(ora['fonte']).upper()}</div>""", 4, 4)
    return [capa, como, med, orac]


def legenda(nv, n):
    d = nv["dias"][n - 1]
    nome = nv["titulo"].title().replace(" Da ", " da ").replace(" De ", " de ").replace(" Do ", " do ")
    linhas = [f"{nv['titulo']} · {ORDINAL[n-1]} DIA DE {len(nv['dias'])}", f"Intenção de hoje: {d['intencao'].lower()[0] + d['intencao'][1:]}", ""]
    if n == 1:
        linhas += [f"Hoje começa a {nome}, que vai até a véspera da festa ({nv['periodo']}).", ""]
    linhas += ["Primeira vez? Uma novena é a mesma oração rezada por nove dias seguidos, pedindo uma graça. Leva uns 5 minutos, "
               "e o passo a passo está no segundo card. Perdeu um dia? Continue de onde parou.", "",
               f"MEDITAÇÃO · {d['titulo']}", d["meditacao"].strip(), "",
               f"ORAÇÃO DA NOVENA · {nv['oracao']['titulo']}", " ".join(nv["oracao"]["texto"]), "",
               f"“{nv['jaculatoria']}”", "",
               f"Fontes: {d['fontes']} · Oração: {nv['oracao']['fonte']} · {nv['jaculatoria_fonte']}"]
    if n < len(nv["dias"]):
        linhas.append("Salve este post para rezar com ele até o fim da novena.")
    return "\n".join(linhas).strip()


def gerar(pasta, br=None):
    """Gera os cards e a legenda das novenas ativas no dia da pasta. Devolve a lista de arquivos gerados."""
    pasta = Path(pasta)
    try:
        dia = dt.date.fromisoformat(pasta.name)
    except ValueError:
        return []
    feitos = []
    for nv, n in ativas(dia):
        htmls = [(f"novena_{nv['id']}_{i:02d}.jpg", body) for i, body in enumerate(cards(nv, n), 1)]
        (pasta / f"legenda_novena_{nv['id']}.txt").write_text(legenda(nv, n)[:2100] + "\n")
        (pasta / f"hashtags_novena_{nv['id']}.txt").write_text(nv.get("hashtags", "#novena #actadei") + "\n")
        dono = br is None
        if dono:
            from playwright.sync_api import sync_playwright
            pw = sync_playwright().start(); br = pw.chromium.launch()
        for nome, body in htmls:
            pg = br.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            pg.set_content(f"<html><head><style>{R.CSS}{CSS_N}</style></head><body>{body}</body></html>")
            pg.wait_for_timeout(250); pg.evaluate(AJUSTE); pg.wait_for_timeout(50)
            pg.screenshot(path=str(pasta / nome), type="jpeg", quality=92); pg.close()
            feitos.append(nome)
        if dono:
            br.close(); pw.stop(); br = None
        print(f"  novena {nv['id']}: dia {n} de {len(nv['dias'])}")
    return feitos


if __name__ == "__main__":
    print(gerar(sys.argv[1]))
