# Acta Dei · Mysterium Fidei

Arquivo diário, bilíngue (PT-BR + EN) e documentado dos milagres reconhecidos pela Igreja Católica e dos santos de cada dia. Operação 100% autônoma: pesquisa, redação, arte e publicação no Instagram (@actadei) sem aprovação humana.

## Como funciona

1. **Tarefa agendada (Cowork, 5h30 BRT)** lê `data/santos.json` e `data/fila.json`, pesquisa nas fontes aceitas, escreve o `post.json` (texto dos cards, stories, legenda PT/EN, hashtags, fontes, pistas de imagem) e faz o commit em `posts/AAAA-MM-DD/`. Ela só escreve texto: não precisa de acesso a imagens nem à API da Meta.
2. **GitHub Actions `build.yml`** dispara nesse commit: baixa a imagem de domínio público no Wikimedia Commons (`scripts/fetch_image.py`, com conferência de licença), renderiza cards e stories (`scripts/render.py`), regenera o índice e faz o commit das artes.
3. **GitHub Pages** serve as imagens em URL pública (a Meta baixa o JPEG na hora de publicar) e o índice de fontes (`index.html`) que vai no link da bio.
4. **GitHub Actions `publish.yml`** roda `scripts/publish.py` às 7h, 13h e 20h BRT: publica o carrossel e os stories pela API do Instagram (Instagram Login) e grava o resultado em `log/publicacoes.csv`. O token fica em *Secrets*, nunca no código; `refresh-token.yml` renova o token toda semana.

## Estrutura

| Pasta ou arquivo | Conteúdo |
| --- | --- |
| `brand/` | Selo, avatar, lockups (SVG/PNG) e fontes (Cinzel, Cormorant Garamond) |
| `data/santos.json` | Calendário litúrgico: santo(s) de cada dia, grau, padroado, imagem, fontes |
| `data/milagres.json` | Banco de milagres verificados: tipo, local, data, status, investigação, decisão, fontes |
| `data/fila.json` | Ordem dos próximos milagres a publicar, respeitando a rotação de pilares |
| `posts/AAAA-MM-DD/` | `post.json`, cards JPEG, stories JPEG, `legenda.txt`, `hashtags.txt`, `meta.json` |
| `log/publicacoes.csv` | Data, hora, slot, tipo, ID do Instagram, status, erro |
| `index.html` | Site do GitHub Pages (raiz do repositório): índice de todos os posts com fontes clicáveis, link da bio |
| `scripts/render.py` | Gera os cards e stories a partir de `post.json` |
| `scripts/commons.py` | Busca imagem de domínio público no Wikimedia Commons e confere a licença |
| `scripts/publish.py` | Cliente da API do Instagram: containers, carrossel, story, comentário, log |
| `scripts/build_index.py` | Regenera `index.html` a partir de `posts/` e `log/` |
| `scripts/PROMPT_TAREFA_DIARIA.md` | Roteiro completo que a tarefa agendada segue todos os dias |

## Regras editoriais (resumo)

- Só publica milagres com status oficial: **Reconhecido pela Igreja** (decreto da Santa Sé, bispo diocesano ou Bureau Médico de Lourdes) ou **Em investigação** (processo aberto e público, sempre sinalizado).
- Duas fontes independentes precisam concordar em data, lugar e status antes de publicar.
- Imagens só de domínio público ou Creative Commons verificada no Wikimedia Commons, com crédito no `post.json`.
- Sem enquetes, caixas de perguntas ou respostas a comentários nas fases 1 e 2.
- Nunca: curas atuais sem decreto, videntes não aprovados, profecias, política, crítica a outras religiões, pedidos de dinheiro, imagens geradas por IA apresentadas como fotografia, marcas ou produtos.

## Identidade

Vermelho-selo `#A6192E` (degradê até `#7A1020`), creme `#F7F2E8`, carvão quente `#26221E`, cinza quente `#6B655E`. Cinzel para nomes e títulos; Cormorant Garamond para corpo, datas e citações. O vermelho nunca ocupa áreas grandes.
