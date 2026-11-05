#!/usr/bin/env python3
"""Gera data/milagres.json: banco inicial de 60 casos com status oficial.

status: 'reconhecido' (decreto da Santa Sé, bispo diocesano, Bureau Médico de Lourdes) | 'investigacao' (processo aberto e público).
Casos sem posição oficial (San Gennaro, Sudário, Zeitoun, Medjugorje antes do nihil obstat) ficam em 'reserva' e NÃO entram na fila.
Os textos aqui são o ponto de partida; a tarefa diária confere duas fontes antes de publicar e escreve o post completo.
"""
import json
from pathlib import Path

M = []
def m(id, tipo, titulo, titulo_en, local, pais, data, status, autoridade, resumo, investigacao, decisao, fontes, wiki, busca, data_sugerida=None, tags=()):
    M.append(dict(id=id, tipo=tipo, titulo=titulo, titulo_en=titulo_en, local=local, pais=pais, data=data, status=status,
                  autoridade=autoridade, resumo=resumo, investigacao=investigacao, decisao=decisao, fontes=fontes,
                  imagem_wikipedia=wiki, imagem_busca=busca, data_sugerida=data_sugerida, tags=list(tags)))

VAT = "vatican.va"
# ======================= MILAGRES EUCARÍSTICOS
m("lanciano","eucaristico","O Milagre Eucarístico de Lanciano","The Eucharistic Miracle of Lanciano","Lanciano, Abruzos","Itália","século VIII (c. 730–750)","reconhecido","Arquidiocese de Lanciano-Ortona; culto público secular; carta de João Paulo II (2004)",
  "Durante a missa, um monge duvidou da presença real; a hóstia tornou-se carne e o vinho sangue, em cinco coágulos. Relíquias custodiadas desde 1252 pelos franciscanos.",
  "Verificações eclesiásticas em 1574, 1637, 1770 e 1886. Em 1970–71 o anatomopatologista Odoardo Linoli (Arezzo) descreveu tecido miocárdico humano e sangue do grupo AB; críticos apontam a ausência de painel multidisciplinar.",
  "Culto público autorizado; João Paulo II, em carta de 4/10/2004 ao arcebispo Carlo Ghidelli, recordou ter venerado as relíquias como cardeal.",
  ["Vatican.va — carta de João Paulo II a D. Carlo Ghidelli, 4/10/2004","Linoli, O. Quaderni Sclavo di Diagnostica, 1971","Santuário de Lanciano — miracoloeucaristico.eu"],
  "en:Eucharistic miracle of Lanciano","Lanciano eucharistic miracle reliquary", tags=("eucaristia","italia"))
m("bolsena","eucaristico","O Milagre de Bolsena e o Corporal de Orvieto","The Miracle of Bolsena and the Corporal of Orvieto","Bolsena e Orvieto","Itália","1263","reconhecido","Papa Urbano IV; bula Transiturus (1264) instituiu Corpus Christi",
  "O sacerdote Pedro de Praga, em dúvida sobre a transubstanciação, viu a hóstia sangrar sobre o corporal durante a missa em Santa Cristina, Bolsena.",
  "Urbano IV, então em Orvieto, mandou o bispo examinar o corporal e o levou em procissão; a catedral de Orvieto foi construída para guardá-lo.",
  "Um ano depois, em 1264, Urbano IV instituiu a festa de Corpus Christi para toda a Igreja (bula Transiturus de hoc mundo).",
  ["Catedral de Orvieto — Cappella del Corporale","Bula Transiturus de hoc mundo (1264)","Catholic Encyclopedia — Orvieto"],
  "en:Corporal of Bolsena","Orvieto corporal Bolsena miracle", tags=("eucaristia","italia","corpus christi"))
m("santarem","eucaristico","O Milagre Eucarístico de Santarém","The Eucharistic Miracle of Santarém","Santarém","Portugal","c. 1247","reconhecido","Autoridade diocesana; culto ininterrupto; igreja do Santíssimo Milagre",
  "Uma mulher levou uma hóstia consagrada para casa; a hóstia sangrou e foi devolvida à igreja de Santo Estêvão, onde permanece em um relicário.",
  "Reconhecimento episcopal medieval e visitas canônicas; o relicário de cristal foi feito em 1782; a hóstia conserva marcas de sangue ressecado.",
  "Culto público mantido há mais de sete séculos; a igreja recebeu o título de Santuário do Santíssimo Milagre.",
  ["Patriarcado de Lisboa / Diocese de Santarém","Santuário do Santíssimo Milagre — Santarém","Catálogo Carlo Acutis — miracolieucaristici.org"],
  "en:Miracle of Santarém","Santarem eucharistic miracle church", tags=("eucaristia","portugal"))
m("siena","eucaristico","As Hóstias de Siena","The Hosts of Siena","Siena, Toscana","Itália","1730","reconhecido","Arcebispado de Siena; exames de 1780, 1914 (comissão com Siro Grimaldi) e 1922",
  "Hóstias roubadas da Basílica de São Francisco em 1730 foram recuperadas; desde então permanecem sem decomposição.",
  "Exames científicos em 1914 (bacteriologista Siro Grimaldi) e 1922 constataram hóstias intactas e sem microrganismos; João Paulo II visitou-as em 1980.",
  "Culto autorizado pela arquidiocese; expostas na Basílica de São Francisco.",
  ["Arquidiocese de Siena — Basilica di San Francesco","Relatório Grimaldi, 1914","Discurso de João Paulo II em Siena, 14/9/1980 (vatican.va)"],
  "en:Hosts of Siena","Siena hosts miracle basilica San Francesco", tags=("eucaristia","italia"))
m("amsterdam","eucaristico","O Milagre de Amsterdã","The Miracle of Amsterdam","Amsterdã","Países Baixos","1345","reconhecido","Bispo de Utrecht (1346); Stille Omgang anual",
  "Uma hóstia dada a um moribundo foi vomitada e lançada ao fogo, mas não queimou; a cidade tornou-se local de peregrinação.",
  "Reconhecido pelo bispo de Utrecht em 1346; a Capela Santa foi erguida no local; a procissão silenciosa (Stille Omgang) persiste desde 1881.",
  "Culto aprovado desde 1346; a procissão anual reúne milhares de católicos.",
  ["Stille Omgang — gezelschap","Diocese de Haarlem-Amsterdam","Catálogo Carlo Acutis"],
  "en:Miracle of Amsterdam","Amsterdam miracle 1345 Stille Omgang", tags=("eucaristia","holanda"))
m("faverney","eucaristico","O Milagre de Faverney","The Miracle of Faverney","Faverney, Franche-Comté","França","1608","reconhecido","Arcebispo de Besançon (1608); Paulo V",
  "Durante a adoração, o altar pegou fogo; o ostensório ficou suspenso no ar por 33 horas, diante de testemunhas, sem que a hóstia queimasse.",
  "Inquérito do arcebispado de Besançon em 1608 com 54 testemunhas; o papa Paulo V concedeu indulgências.",
  "Reconhecido pelo arcebispo de Besançon em 1608; a hóstia é conservada na basílica de Faverney.",
  ["Arquidiocese de Besançon","Basílica de Faverney","Catálogo Carlo Acutis"],
  "en:Miracle of Faverney","Faverney eucharistic miracle", tags=("eucaristia","franca"))
m("buenos_aires","eucaristico","Buenos Aires, 1996: a hóstia analisada","Buenos Aires, 1996: the host under analysis","Paróquia Santa Maria, Buenos Aires","Argentina","15 de agosto de 1996","reconhecido","Arquidiocese de Buenos Aires (então arcebispo Jorge Bergoglio) — culto autorizado",
  "Uma hóstia encontrada no chão foi guardada em água; dias depois apresentava tecido avermelhado. O caso foi acompanhado pela arquidiocese.",
  "Amostras analisadas entre 1999 e 2005 (incluindo o patologista Frederick Zugibe, Nova York) descreveram tecido cardíaco humano inflamado; a investigação foi conduzida por iniciativa da arquidiocese e divulgada pelo médico Ricardo Castañón.",
  "A arquidiocese autorizou a veneração; não houve decreto pontifício. A hóstia permanece na paróquia Santa Maria.",
  ["Arquidiocese de Buenos Aires","Castañón, R. — relatório das análises","Catálogo Carlo Acutis"],
  "en:Eucharistic miracle of Buenos Aires","Buenos Aires eucharistic miracle 1996", tags=("eucaristia","argentina","seculo xx"))
m("tixtla","eucaristico","Tixtla, 2006","Tixtla, 2006","Tixtla, Guerrero","México","21 de outubro de 2006","reconhecido","Dom Alejo Zavala Castro, bispo de Chilpancingo-Chilapa (decreto de 12/10/2013)",
  "Durante um retiro, uma hóstia começou a exsudar uma substância avermelhada diante dos fiéis.",
  "Comissão diocesana (2009–2012) com análises em laboratórios do México e dos EUA (coordenação de Ricardo Castañón): sangue humano AB e tecido com sinais de vitalidade.",
  "Em 12 de outubro de 2013 o bispo declarou o fato 'sinal divino' e autorizou o culto.",
  ["Diocese de Chilpancingo-Chilapa — decreto de 2013","ACI Prensa, outubro de 2013","Catálogo Carlo Acutis"],
  "en:Eucharistic miracle of Tixtla","Tixtla eucharistic miracle 2006", tags=("eucaristia","mexico","seculo xxi"))
m("sokolka","eucaristico","Sokółka, 2008","Sokółka, 2008","Sokółka, Podláquia","Polônia","12 de outubro de 2008","reconhecido","Arcebispo metropolita de Białystok, Edward Ozorowski (comunicado de 2011)",
  "Uma hóstia caída foi colocada em água; dias depois apresentava uma mancha vermelha. A cúria mandou analisar.",
  "Dois patologistas da Universidade Médica de Białystok (Maria Sobaniec-Łotowska e Stanisław Sulkowski) descreveram tecido miocárdico humano em agonia, entrelaçado com a hóstia de modo que não puderam explicar.",
  "A arquidiocese reconheceu o fenômeno como não explicável pela ciência e expôs a hóstia à veneração em 2011.",
  ["Arquidiocese de Białystok — comunicado 2011","Universidade Médica de Białystok — laudos","Catholic News Agency, 2011"],
  "en:Eucharistic miracle of Sokółka","Sokolka eucharistic miracle", tags=("eucaristia","polonia","seculo xxi"))
m("legnica","eucaristico","Legnica, 2013","Legnica, 2013","Legnica, Baixa Silésia","Polônia","25 de dezembro de 2013","reconhecido","Dom Zbigniew Kiernikowski, bispo de Legnica (comunicado de 10/4/2016), após consulta à Congregação para a Doutrina da Fé",
  "Uma hóstia caída foi colocada em água e passou a mostrar manchas vermelhas.",
  "Análises do Departamento de Medicina Forense de Szczecin (2014–2015): fragmentos de tecido semelhante a músculo cardíaco humano com alterações de agonia; DNA humano detectado.",
  "O bispo comunicou o reconhecimento em abril de 2016 e autorizou a exposição da hóstia na paróquia de São Jacinto.",
  ["Diocese de Legnica — comunicado de 10/4/2016","Vatican Radio / Catholic News Agency, abril 2016","Catálogo Carlo Acutis"],
  "en:Eucharistic miracle of Legnica","Legnica eucharistic miracle", tags=("eucaristia","polonia","seculo xxi"))
m("cascia","eucaristico","A Hóstia de Cascia","The Host of Cascia","Cascia, Úmbria","Itália","1330","reconhecido","Autoridade diocesana; relíquia na Basílica de Santa Rita",
  "Um sacerdote guardou uma hóstia entre as páginas do breviário ao visitar um doente; ao abri-lo, encontrou a hóstia sangrando sobre as páginas.",
  "Verificações de 1687 e 1930; as páginas manchadas são conservadas na Basílica de Santa Rita de Cássia.",
  "Culto público secular, com exposição anual na festa de Corpus Christi.",
  ["Basílica de Santa Rita de Cássia","Catálogo Carlo Acutis","Diocese de Spoleto-Norcia"],
  "en:Cascia","Cascia eucharistic miracle basilica Santa Rita", tags=("eucaristia","italia"))

# ======================= APARIÇÕES APROVADAS
m("guadalupe","aparicao","Nossa Senhora de Guadalupe e a tilma de Juan Diego","Our Lady of Guadalupe and Juan Diego's tilma","Tepeyac, Cidade do México","México","9 a 12 de dezembro de 1531","reconhecido","Culto aprovado desde o século XVI; Bento XIV (1754) declarou padroeira; Juan Diego canonizado em 2002",
  "A Virgem apareceu ao indígena Juan Diego Cuauhtlatoatzin e, como sinal ao bispo Zumárraga, fez surgir sua imagem no manto (tilma) de fibra de agave.",
  "A tilma de 1531 permanece íntegra apesar da fibra que normalmente dura poucas décadas; estudos de 1936 (Richard Kuhn) e 1979 (Callahan e Smith, infravermelho) não identificaram esboço nem pinceladas na imagem original; o episódio foi estudado pelo processo de canonização de Juan Diego.",
  "Padroeira do México (1754) e da América (1946); Juan Diego canonizado por João Paulo II em 31/7/2002.",
  ["Vatican.va — homilia de canonização de Juan Diego, 31/7/2002","Basílica de Guadalupe — estudos sobre a tilma","Callahan, P. S. — The Tilma under Infra-red Radiation (CARA, 1981)"],
  "en:Our Lady of Guadalupe","Our Lady of Guadalupe tilma", "12-12", tags=("mariana","mexico"))
m("rue_du_bac","aparicao","Rue du Bac e a Medalha Milagrosa","Rue du Bac and the Miraculous Medal","Capela das Filhas da Caridade, Paris","França","18 de julho e 27 de novembro de 1830","reconhecido","Arcebispo de Paris, Hyacinthe de Quélen (inquérito canônico de 1836)",
  "A noviça Catarina Labouré viu a Virgem, que pediu a cunhagem de uma medalha com a invocação 'Ó Maria concebida sem pecado'.",
  "Inquérito canônico de 1836 ouviu testemunhas e examinou os fatos; a medalha, cunhada em 1832, espalhou-se com relatos de conversões e curas, entre elas a de Alphonse Ratisbonne (1842).",
  "Aprovação do arcebispo em 1836; Catarina Labouré canonizada em 1947, corpo encontrado incorrupto em 1933.",
  ["Chapelle Notre-Dame de la Médaille Miraculeuse — Paris","Vatican.va — canonização de Catarina Labouré (1947)","Laurentin, R. — Vie de Catherine Labouré"],
  "en:Miraculous Medal","Rue du Bac chapel Miraculous Medal", "11-27", tags=("mariana","franca"))
m("la_salette","aparicao","Nossa Senhora de La Salette","Our Lady of La Salette","La Salette, Alpes franceses","França","19 de setembro de 1846","reconhecido","Dom Philibert de Bruillard, bispo de Grenoble (19/9/1851)",
  "Dois pastores, Maximin Giraud e Mélanie Calvat, viram uma senhora em pranto que falou de conversão e penitência.",
  "Cinco anos de inquérito diocesano com comissão de teólogos; curas atribuídas à fonte de La Salette examinadas.",
  "Decreto de 1851 declarou a aparição digna de fé; basílica consagrada em 1879.",
  ["Diocese de Grenoble-Vienne — decreto de 1851","Santuário de La Salette","Catholic Encyclopedia — La Salette"],
  "en:Our Lady of La Salette","La Salette apparition statue", "09-19", tags=("mariana","franca"))
m("lourdes","aparicao","Lourdes, 1858: as dezoito aparições","Lourdes, 1858: the eighteen apparitions","Gruta de Massabielle, Lourdes","França","11 de fevereiro a 16 de julho de 1858","reconhecido","Dom Bertrand-Sévère Laurence, bispo de Tarbes (18/1/1862)",
  "Bernadette Soubirous, 14 anos, viu dezoito vezes uma senhora que se identificou como 'a Imaculada Conceição', quatro anos após a proclamação do dogma.",
  "Comissão episcopal de 1858–1862 interrogou Bernadette e examinou curas na fonte; a Igreja reconheceu sete delas no mesmo decreto.",
  "Decreto de 1862: 'a Imaculada Mãe de Deus apareceu realmente a Bernadette'. Bernadette canonizada em 1933.",
  ["Diocese de Tarbes e Lourdes — decreto de 18/1/1862","Sanctuaire Notre-Dame de Lourdes — lourdes-france.org","Laurentin, R. — Lourdes, documents authentiques"],
  "en:Our Lady of Lourdes","Lourdes grotto Massabielle", "02-11", tags=("mariana","franca","lourdes"))
m("pontmain","aparicao","Nossa Senhora de Pontmain","Our Lady of Pontmain","Pontmain, Mayenne","França","17 de janeiro de 1871","reconhecido","Dom Casimir Wicart, bispo de Laval (2/2/1872)",
  "Durante a guerra franco-prussiana, crianças viram a Virgem no céu com a mensagem 'Rezai, meus filhos; Deus vos atenderá em pouco tempo'. O avanço prussiano parou naquela noite.",
  "Inquérito diocesano ouviu as crianças separadamente e os adultos presentes; o armistício veio onze dias depois.",
  "Aprovada em 1872; basílica consagrada em 1900.",
  ["Diocese de Laval","Sanctuaire de Pontmain","Catholic Encyclopedia"],
  "en:Our Lady of Pontmain","Pontmain apparition basilica", "01-17", tags=("mariana","franca"))
m("knock","aparicao","Knock, 1879","Knock, 1879","Knock, Condado de Mayo","Irlanda","21 de agosto de 1879","reconhecido","Comissões diocesanas de 1879 e 1936; visita de João Paulo II (1979) e Francisco (2018)",
  "Quinze pessoas viram, durante duas horas, Nossa Senhora, São José, São João Evangelista e um cordeiro sobre um altar na parede da igreja paroquial.",
  "A comissão de 1879 ouviu as quinze testemunhas e julgou os depoimentos dignos de confiança; a de 1936 reinterrogou os sobreviventes.",
  "Santuário nacional da Irlanda; João Paulo II celebrou o centenário em 1979; basílica elevada a santuário internacional em 2021.",
  ["Knock Shrine — knockshrine.ie","Arquidiocese de Tuam — comissões de 1879 e 1936","Vatican.va — homilia de João Paulo II em Knock, 30/9/1979"],
  "en:Our Lady of Knock","Knock apparition gable", "08-21", tags=("mariana","irlanda"))
m("fatima","aparicao","Fátima, 1917, e o Milagre do Sol","Fátima, 1917, and the Miracle of the Sun","Cova da Iria, Fátima","Portugal","13 de maio a 13 de outubro de 1917","reconhecido","Dom José Alves Correia da Silva, bispo de Leiria (13/10/1930)",
  "Lúcia, Francisco e Jacinta viram a Virgem seis vezes; na última, em 13 de outubro, uma multidão estimada em dezenas de milhares viu o sol 'dançar', fato noticiado pela imprensa laica (O Século).",
  "Inquérito canônico aberto em 1922 ouviu as testemunhas e examinou os relatos de jornais; concluiu em 1930.",
  "Carta pastoral de 1930 declarou as visões dignas de crédito e permitiu o culto; Francisco e Jacinta canonizados em 2017.",
  ["Santuário de Fátima — fatima.pt","Carta pastoral de D. José Alves Correia da Silva, 13/10/1930","Vatican.va — homilia de canonização, 13/5/2017"],
  "en:Our Lady of Fátima","Fatima miracle of the sun crowd 1917", "05-13", tags=("mariana","portugal"))
m("beauraing","aparicao","Beauraing, 1932–1933","Beauraing, 1932–1933","Beauraing","Bélgica","29 de novembro de 1932 a 3 de janeiro de 1933","reconhecido","Dom André-Marie Charue, bispo de Namur (2/7/1949)",
  "Cinco crianças viram a Virgem 33 vezes junto a um espinheiro no jardim de um colégio; ela mostrou um coração de ouro.",
  "Inquérito diocesano de 1935 em diante; a Santa Sé autorizou o culto em 1943 antes da aprovação definitiva.",
  "Reconhecimento do caráter sobrenatural em 1949; duas curas foram declaradas milagrosas no mesmo ato.",
  ["Diocese de Namur","Sanctuaire de Beauraing","Catholic Encyclopedia (suplemento)"],
  "en:Our Lady of Beauraing","Beauraing apparition shrine", "11-29", tags=("mariana","belgica"))
m("banneux","aparicao","Banneux, 1933: a Virgem dos Pobres","Banneux, 1933: the Virgin of the Poor","Banneux, Lieja","Bélgica","15 de janeiro a 2 de março de 1933","reconhecido","Dom Louis-Joseph Kerkhofs, bispo de Lieja (22/8/1949)",
  "Mariette Beco, 11 anos, viu oito vezes a Virgem, que se chamou 'Virgem dos Pobres' e indicou uma fonte 'para todas as nações'.",
  "Comissão diocesana (1935–1937) e exame de curas; o culto foi autorizado em 1942.",
  "Aprovada em 1949; o santuário recebe peregrinos de toda a Europa.",
  ["Diocese de Lieja","Sanctuaire de Banneux","Catholic Encyclopedia (suplemento)"],
  "en:Our Lady of Banneux","Banneux Virgin of the Poor shrine", "01-15", tags=("mariana","belgica"))
m("kibeho","aparicao","Kibeho, 1981: a única aparição aprovada na África","Kibeho, 1981: Africa's only approved apparition","Kibeho","Ruanda","28 de novembro de 1981 a 1989","reconhecido","Dom Augustin Misago, bispo de Gikongoro (29/6/2001)",
  "Três estudantes de um colégio — Alphonsine Mumureke, Nathalie Mukamazimpaka e Marie-Claire Mukangango — viram Nossa Senhora, 'Mãe do Verbo', que pediu conversão e previu sofrimentos, lidos depois à luz do genocídio de 1994.",
  "Comissões teológica e médica desde 1982; estudo de vinte anos sobre as videntes e as mensagens.",
  "Declaração de 2001 reconheceu as aparições às três primeiras videntes; santuário de Nossa Senhora das Dores.",
  ["Diocese de Gikongoro — declaração de 29/6/2001","Santuário de Kibeho","Vatican News"],
  "en:Our Lady of Kibeho","Kibeho shrine Our Lady of Sorrows", "11-28", tags=("mariana","africa","seculo xx"))
m("laus","aparicao","Nossa Senhora do Laus","Our Lady of Laus","Saint-Étienne-le-Laus, Altos Alpes","França","1664 a 1718","reconhecido","Dom Jean-Michel di Falco, bispo de Gap (4/5/2008)",
  "Benoîte Rencurel, pastora de 17 anos, viu a Virgem por 54 anos e recebeu a missão de acolher penitentes no santuário.",
  "Primeira aparição reconhecida pelo vigário-geral em 1665; o processo moderno foi concluído em 2008, o primeiro reconhecimento na França em mais de um século.",
  "Reconhecido em 2008 pelo bispo de Gap, com autorização da Santa Sé.",
  ["Diocese de Gap e Embrun — decreto de 2008","Sanctuaire Notre-Dame du Laus","Catholic News Agency, maio 2008"],
  "en:Our Lady of Laus","Notre-Dame du Laus sanctuary", "05-04", tags=("mariana","franca"))
m("akita","aparicao","Akita, 1973: as lágrimas da imagem","Akita, 1973: the weeping statue","Convento de Yuzawadai, Akita","Japão","1973 a 1981","reconhecido","Dom John Shojiro Ito, bispo de Niigata (carta pastoral de 22/4/1984)",
  "A irmã Agnes Sasagawa recebeu mensagens e estigma; a imagem de madeira de Nossa Senhora chorou 101 vezes, diante de testemunhas e da televisão japonesa.",
  "Análises de laboratório (Universidade de Akita e Gifu) identificaram lágrimas, sangue e suor humanos; o bispo consultou a Congregação para a Doutrina da Fé.",
  "O bispo declarou os eventos sobrenaturais e autorizou a veneração em 1984.",
  ["Carta pastoral de D. John Ito, 22/4/1984","Diocese de Niigata","EWTN — Akita"],
  "en:Our Lady of Akita","Our Lady of Akita statue", tags=("mariana","japao","seculo xx"))
m("cuapa","aparicao","Cuapa, 1980","Cuapa, 1980","Cuapa, Chontales","Nicarágua","8 de maio a 13 de outubro de 1980","reconhecido","Dom Pablo Antonio Vega, bispo de Juigalpa (13/11/1982)",
  "O sacristão Bernardo Martínez viu a Virgem cinco vezes, com pedido de oração do rosário e paz para o país.",
  "Inquérito diocesano de 1980–1982, em plena guerra civil; o vidente tornou-se sacerdote em 1995.",
  "Aprovada pelo bispo em 1982; santuário diocesano em Cuapa.",
  ["Diocese de Juigalpa — declaração de 1982","Conferência Episcopal da Nicarágua","Catholic News Agency"],
  "en:Our Lady of Cuapa","Cuapa apparition Nicaragua", tags=("mariana","america latina","seculo xx"))
m("san_nicolas","aparicao","San Nicolás de los Arroyos, 1983","San Nicolás de los Arroyos, 1983","San Nicolás, Buenos Aires","Argentina","25 de setembro de 1983 a 1990","reconhecido","Dom Héctor Cardelli, bispo de San Nicolás (22/5/2016)",
  "Gladys Quiroga de Motta recebeu cerca de 1.800 mensagens da Virgem do Rosário; o culto cresceu com a construção do santuário.",
  "Comissão diocesana de 1990 autorizou o culto; estudo final concluído em 2016.",
  "Decreto de 2016 reconheceu o caráter sobrenatural dos eventos.",
  ["Diocese de San Nicolás de los Arroyos — decreto de 2016","Santuário de Nossa Senhora do Rosário de San Nicolás","AICA, maio 2016"],
  "en:Our Lady of the Rosary of San Nicolás","San Nicolas de los Arroyos sanctuary", tags=("mariana","argentina","seculo xx"))
m("champion","aparicao","Our Lady of Good Help: a única aparição aprovada nos EUA","Our Lady of Good Help: the only approved apparition in the U.S.","Champion, Wisconsin","Estados Unidos","9 de outubro de 1859","reconhecido","Dom David Ricken, bispo de Green Bay (8/12/2010)",
  "A imigrante belga Adele Brise viu a Virgem três vezes, com a missão de catequizar crianças; em 1871 a capela foi poupada pelo incêndio de Peshtigo.",
  "Comissão de teólogos e historiadores (2009–2010) revisou documentos e tradição oral.",
  "Decreto de 2010 aprovou a aparição; santuário nacional desde 2016.",
  ["Diocese de Green Bay — decreto de 8/12/2010","National Shrine of Our Lady of Champion","Catholic News Agency, dezembro 2010"],
  "en:Our Lady of Good Help","Our Lady of Good Help shrine Champion", "10-09", tags=("mariana","eua"))

# ======================= MILAGRES DE CANONIZAÇÃO E BEATIFICAÇÃO
m("jp2_floribeth","canonizacao","A cura de Floribeth Mora e a canonização de João Paulo II","Floribeth Mora's healing and the canonization of John Paul II","Tres Ríos, Cartago","Costa Rica","1º de maio de 2011","reconhecido","Decreto da Congregação das Causas dos Santos (5/7/2013); canonização em 27/4/2014",
  "Floribeth Mora Díaz, com aneurisma cerebral inoperável, viu o aneurisma desaparecer na noite da beatificação de João Paulo II, enquanto rezava diante de sua foto.",
  "Consulta Médica do Dicastério examinou os exames de imagem antes e depois; teólogos e cardeais aprovaram em 2013.",
  "Milagre reconhecido por Francisco em 5/7/2013; João Paulo II canonizado em 27/4/2014.",
  ["Vatican.va — decreto de 5/7/2013 e homilia de 27/4/2014","Dicastério das Causas dos Santos","Catholic News Agency — entrevista com Floribeth Mora"],
  "en:Pope John Paul II","Floribeth Mora John Paul II canonization", "10-22", tags=("canonizacao","papa","seculo xxi"))
m("jp2_simon_pierre","canonizacao","Irmã Marie Simon-Pierre: Parkinson e a beatificação de João Paulo II","Sister Marie Simon-Pierre: Parkinson's and John Paul II's beatification","Aix-en-Provence","França","2 de junho de 2005","reconhecido","Decreto de 14/1/2011; beatificação em 1/5/2011",
  "Religiosa francesa com doença de Parkinson — a mesma doença do papa — recuperou-se repentinamente dois meses após a morte de João Paulo II, depois de a comunidade rezar por sua intercessão.",
  "Exames neurológicos repetidos e dois painéis médicos do Dicastério; o caso foi reexaminado antes da aprovação.",
  "Milagre reconhecido por Bento XVI em 14/1/2011; beatificação em 1/5/2011.",
  ["Vatican.va — decreto de 14/1/2011","Dicastério das Causas dos Santos","Conferência Episcopal da França"],
  "en:Marie Simon-Pierre","Marie Simon-Pierre John Paul II beatification", tags=("beatificacao","papa"))
m("madre_teresa_brasil","canonizacao","Marcilio Andrino: o milagre brasileiro de Madre Teresa","Marcilio Andrino: Mother Teresa's Brazilian miracle","Santos, São Paulo","Brasil","9 de dezembro de 2008","reconhecido","Decreto de 17/12/2015; canonização em 4/9/2016",
  "O engenheiro Marcilio Haddad Andrino, em coma por abscessos cerebrais, acordou sem sequelas minutos antes da cirurgia, enquanto a esposa Fernanda rezava a Madre Teresa.",
  "Consulta Médica concluiu que a cura foi instantânea, completa e sem explicação médica; teólogos aprovaram a ligação com a intercessão.",
  "Francisco reconheceu o milagre em 17/12/2015; Madre Teresa canonizada em 4/9/2016 na Praça de São Pedro.",
  ["Vatican.va — decreto de 17/12/2015","Diocese de Santos","Vatican News — entrevista com o casal Andrino"],
  "en:Mother Teresa","Mother Teresa canonization 2016", "09-05", tags=("canonizacao","brasil","seculo xxi"))
m("madre_teresa_besra","canonizacao","Monica Besra e a beatificação de Madre Teresa","Monica Besra and Mother Teresa's beatification","Dangram, Bengala Ocidental","Índia","5 de setembro de 1998","reconhecido","Decreto de 20/12/2002; beatificação em 19/10/2003",
  "Monica Besra tinha um tumor abdominal; após as irmãs colocarem sobre ela uma medalha tocada no corpo de Madre Teresa, o tumor desapareceu.",
  "Comissão da arquidiocese de Calcutá e painel médico do Vaticano; o caso gerou debate público na Índia sobre tratamento prévio.",
  "Reconhecido por João Paulo II em 20/12/2002; beatificação em 19/10/2003.",
  ["Vatican.va — decreto de 20/12/2002","Arquidiocese de Calcutá","Postulação das Missionárias da Caridade"],
  "en:Mother Teresa","Mother Teresa beatification 2003", tags=("beatificacao","india"))
m("acutis_mattheus","canonizacao","Mattheus, de Campo Grande: o milagre de Carlo Acutis","Mattheus of Campo Grande: Carlo Acutis' miracle","Campo Grande, Mato Grosso do Sul","Brasil","12 de outubro de 2013","reconhecido","Decreto de 21/2/2020; beatificação em 10/10/2020",
  "O menino Mattheus Lins Vianna, com pâncreas anular congênito, tocou uma relíquia de Carlo Acutis na paróquia São Sebastião e, a partir daquele dia, passou a comer normalmente; exames mostraram a anatomia normalizada.",
  "Inquérito diocesano em Campo Grande (2016) e Consulta Médica romana; o pároco Marcelo Tenório documentou o caso desde o início.",
  "Francisco aprovou o milagre em 21/2/2020; Carlo Acutis beatificado em Assis em 10/10/2020.",
  ["Vatican.va — decreto de 21/2/2020","Arquidiocese de Campo Grande","Vatican News, outubro 2020"],
  "en:Carlo Acutis","Carlo Acutis beatification Assisi", "10-12", tags=("beatificacao","brasil","seculo xxi"))
m("acutis_valeria","canonizacao","Valeria Valverde e a canonização de Carlo Acutis","Valeria Valverde and Carlo Acutis' canonization","Florença","Itália","2 de julho de 2022","reconhecido","Decreto de 23/5/2024; canonização em 7/9/2025",
  "A costarriquenha Valeria Valverde, 21 anos, sofreu traumatismo craniano grave em acidente de bicicleta; a mãe peregrinou a Assis ao túmulo de Carlo; no mesmo dia ela voltou a respirar sozinha e recuperou-se em semanas.",
  "Consulta Médica e Congresso de Teólogos do Dicastério (2023–2024).",
  "Milagre reconhecido por Francisco em 23/5/2024; canonizado por Leão XIV em 7/9/2025, ao lado de Pier Giorgio Frassati.",
  ["Vatican.va — decreto de 23/5/2024","Vatican News — canonização de 7/9/2025","Diocese de Assis"],
  "en:Carlo Acutis","Carlo Acutis canonization 2025", tags=("canonizacao","seculo xxi"))
m("dulce_claudia","canonizacao","Cláudia Cristiane: a hemorragia que parou","Cláudia Cristiane: the hemorrhage that stopped","Malhador, Sergipe","Brasil","janeiro de 2001","reconhecido","Decreto de 27/10/2010; beatificação em 22/5/2011",
  "Cláudia Cristiane dos Santos sofreu hemorragia incontrolável após o parto; o padre Fernando Negromonte rezou pedindo a intercessão de Irmã Dulce e o sangramento cessou.",
  "Processo na Arquidiocese de Aracaju e painel médico do Vaticano concluíram que não havia explicação médica.",
  "Bento XVI reconheceu o milagre em 2010; Irmã Dulce beatificada em Salvador em 22/5/2011.",
  ["Vatican.va — decreto de 27/10/2010","Obras Sociais Irmã Dulce — OSID","Arquidiocese de Aracaju"],
  "pt:Irmã Dulce","Irma Dulce dos Pobres", "08-13", tags=("beatificacao","brasil"))
m("dulce_mauricio","canonizacao","Maurício Bruno: a visão recuperada e a primeira santa brasileira","Maurício Bruno: sight regained and Brazil's first female saint","Salvador, Bahia","Brasil","dezembro de 2014","reconhecido","Decreto de 13/5/2019; canonização em 13/10/2019",
  "O maestro Maurício Bruno Ribeiro, cego havia 14 anos por glaucoma, recuperou a visão depois de rezar a Irmã Dulce em sua igreja em Salvador.",
  "Exames oftalmológicos antes e depois foram avaliados pela Consulta Médica do Dicastério; teólogos confirmaram o nexo com a oração.",
  "Reconhecido por Francisco em 13/5/2019; canonização em 13/10/2019, Praça de São Pedro.",
  ["Vatican.va — decreto de 13/5/2019 e homilia de 13/10/2019","Arquidiocese de Salvador","OSID"],
  "pt:Irmã Dulce","Santa Dulce dos Pobres canonization", "10-13", tags=("canonizacao","brasil","seculo xxi"))
m("galvao_sandra","canonizacao","As pílulas de Frei Galvão e a gestação de Sandra Grossi","Frei Galvão's paper pills and Sandra Grossi's pregnancy","São Paulo","Brasil","1999","reconhecido","Decreto de 16/12/2006; canonização em 11/5/2007 em São Paulo",
  "Sandra Grossi de Almeida, com útero bicorno e histórico de abortos, levou a gestação a termo após tomar as 'pílulas' de papel com oração de Frei Galvão; o filho Enzo nasceu saudável.",
  "Processo na Arquidiocese de São Paulo com laudos obstétricos; Consulta Médica romana aprovou em 2006.",
  "Bento XVI canonizou Frei Galvão no Campo de Marte, em 11/5/2007, diante de cerca de um milhão de pessoas.",
  ["Vatican.va — homilia de Bento XVI, 11/5/2007","Mosteiro da Luz — São Paulo","Arquidiocese de São Paulo"],
  "pt:Frei Galvão","Frei Galvao canonization 2007", "05-11", tags=("canonizacao","brasil"))
m("faustina_pytel","canonizacao","Ronald Pytel: o coração que se refez","Ronald Pytel: the heart made whole","Baltimore, Maryland","Estados Unidos","5 de outubro de 1995","reconhecido","Decreto de 20/12/1999; canonização em 30/4/2000",
  "O padre Ronald Pytel, com válvula aórtica gravemente danificada, recuperou-se completamente durante uma oração de cura na festa de Santa Faustina.",
  "O cardiologista Nicholas Fortuin (Johns Hopkins) documentou a normalização inexplicável; a Consulta Médica aprovou em 1999.",
  "Reconhecido por João Paulo II em 1999; Faustina canonizada em 30/4/2000, primeira santa do novo milênio.",
  ["Vatican.va — homilia de 30/4/2000","Arquidiocese de Baltimore","Santuário da Divina Misericórdia, Cracóvia"],
  "en:Faustina Kowalska","Faustina Kowalska canonization", "10-05", tags=("canonizacao","eua"))
m("padre_pio_colella","canonizacao","Matteo Pio Colella e a canonização de Padre Pio","Matteo Pio Colella and the canonization of Padre Pio","San Giovanni Rotondo","Itália","janeiro de 2000","reconhecido","Decreto de 20/12/2001; canonização em 16/6/2002",
  "Matteo, 7 anos, com meningite fulminante e falência de órgãos, recuperou-se sem sequelas após orações a Padre Pio no hospital Casa Sollievo della Sofferenza.",
  "Laudos do hospital e Consulta Médica do Vaticano; o menino relatou ter visto um frade de barba branca.",
  "João Paulo II canonizou Padre Pio em 16/6/2002, diante de cerca de 300 mil pessoas.",
  ["Vatican.va — homilia de 16/6/2002","Casa Sollievo della Sofferenza","Frades Capuchinhos de San Giovanni Rotondo"],
  "en:Padre Pio","Padre Pio canonization 2002", "09-23", tags=("canonizacao","italia"))
m("escriva_nevado","canonizacao","Manuel Nevado: a radiodermatite e a canonização de São Josemaria","Manuel Nevado: radiodermatitis and St. Josemaría's canonization","Almendralejo, Badajoz","Espanha","novembro de 1992","reconhecido","Decreto de 20/12/2001; canonização em 6/10/2002",
  "O médico Manuel Nevado Rey, com radiodermatite crônica cancerizável nas mãos após anos de raios X, curou-se por completo após pedir a intercessão de Josemaria Escrivá.",
  "A Consulta Médica classificou a cura como instantânea, completa e irreversível, sem explicação científica.",
  "João Paulo II canonizou Josemaria Escrivá em 6/10/2002.",
  ["Vatican.va — homilia de 6/10/2002","Opus Dei — opusdei.org (processo de canonização)","Dicastério das Causas dos Santos"],
  "en:Josemaría Escrivá","Josemaria Escriva canonization 2002", "06-26", tags=("canonizacao","espanha"))
m("portillo_ureta","canonizacao","José Ignacio Ureta: o bebê chileno e o Beato Álvaro del Portillo","José Ignacio Ureta: the Chilean baby and Blessed Álvaro del Portillo","Santiago","Chile","agosto de 2003","reconhecido","Decreto de 5/7/2013; beatificação em 27/9/2014 em Madri",
  "O recém-nascido José Ignacio Ureta Wilson sofreu parada cardíaca de mais de meia hora e hemorragia; os pais rezaram a Álvaro del Portillo e ele voltou a viver sem sequelas.",
  "Processo diocesano em Santiago e Consulta Médica romana.",
  "Francisco aprovou o milagre em 2013; beatificação em Madri, 27/9/2014.",
  ["Vatican.va — decreto de 5/7/2013","Opus Dei — beatificação de Álvaro del Portillo","Arquidiocese de Santiago"],
  "en:Álvaro del Portillo","Alvaro del Portillo beatification Madrid", tags=("beatificacao","chile"))
m("paulo6_pironato","canonizacao","Vanna Pironato e a canonização de Paulo VI","Vanna Pironato and the canonization of Paul VI","Verona","Itália","2014","reconhecido","Decreto de 6/3/2018; canonização em 14/10/2018",
  "Gestante com rompimento de bolsa na 13ª semana, Vanna Pironato rezou a Paulo VI em Brescia; a gravidez prosseguiu e a filha Amanda nasceu saudável.",
  "Consulta Médica e teólogos examinaram o caso entre 2017 e 2018.",
  "Francisco canonizou Paulo VI em 14/10/2018, junto com Oscar Romero.",
  ["Vatican.va — decreto de 6/3/2018 e homilia de 14/10/2018","Diocese de Brescia","Vatican News"],
  "en:Pope Paul VI","Paul VI canonization 2018", "05-29", tags=("canonizacao","papa"))
m("jp1_candela","canonizacao","Candela Giarda e a beatificação de João Paulo I","Candela Giarda and the beatification of John Paul I","Buenos Aires","Argentina","julho de 2011","reconhecido","Decreto de 13/10/2021; beatificação em 4/9/2022",
  "A menina Candela Giarda, 11 anos, com encefalite grave e falência múltipla, recuperou-se após o padre José Dabusti rezar a João Paulo I na UTI.",
  "Processo na Arquidiocese de Buenos Aires e Consulta Médica romana.",
  "Francisco reconheceu o milagre em 2021 e beatificou Albino Luciani em 4/9/2022.",
  ["Vatican.va — decreto de 13/10/2021","Fundação Vaticana João Paulo I","Vatican News"],
  "en:Pope John Paul I","John Paul I beatification 2022", tags=("beatificacao","papa","argentina"))
m("stein_mccarthy","canonizacao","Benedicta McCarthy e a canonização de Edith Stein","Benedicta McCarthy and the canonization of Edith Stein","Boston, Massachusetts","Estados Unidos","1987","reconhecido","Decreto de 1997; canonização em 11/10/1998",
  "Teresa Benedicta McCarthy, 2 anos, ingeriu dose maciça de paracetamol e teve falência hepática; a família rezou a Edith Stein e a criança recuperou-se por completo.",
  "Consulta Médica do Vaticano considerou a recuperação inexplicável; o médico Ronald Kleinman testemunhou.",
  "Canonizada por João Paulo II em 11/10/1998, copadroeira da Europa.",
  ["Vatican.va — homilia de 11/10/1998","Carmelo de Colônia","Arquidiocese de Boston"],
  "en:Edith Stein","Edith Stein canonization", "08-09", tags=("canonizacao","eua"))
m("frassati_gutierrez","canonizacao","Juan Manuel Gutiérrez e a canonização de Pier Giorgio Frassati","Juan Manuel Gutiérrez and the canonization of Pier Giorgio Frassati","Los Angeles, Califórnia","Estados Unidos","2017","reconhecido","Decreto de 25/11/2024; canonização em 7/9/2025",
  "O seminarista Juan Manuel Gutiérrez rompeu o tendão de Aquiles dias antes de uma peregrinação; rezou uma novena a Frassati e amanheceu curado.",
  "Consulta Médica e teólogos do Dicastério em 2024.",
  "Francisco aprovou o milagre em 2024; Leão XIV canonizou Frassati em 7/9/2025.",
  ["Vatican.va — decreto de 25/11/2024","Vatican News — canonização de 7/9/2025","Arquidiocese de Los Angeles"],
  "en:Pier Giorgio Frassati","Pier Giorgio Frassati canonization", "07-04", tags=("canonizacao","seculo xxi"))
m("nha_chica","canonizacao","Nhá Chica: a beata mineira","Nhá Chica: the blessed of Minas Gerais","Baependi, Minas Gerais","Brasil","1995","reconhecido","Decreto de 2011; beatificação em 4/5/2013",
  "Ana Lúcia Meirelles, com cirrose em estágio terminal, recuperou-se após pedir a intercessão de Francisca de Paula de Jesus, a Nhá Chica.",
  "Processo na Diocese da Campanha e Consulta Médica romana.",
  "Beatificada em Baependi em 4/5/2013, pelo cardeal Angelo Amato.",
  ["Vatican.va — decreto de 2011","Diocese da Campanha","Santuário de Nhá Chica, Baependi"],
  "pt:Nhá Chica","Nha Chica Baependi", "11-28", tags=("beatificacao","brasil"))
m("martin_carmen","canonizacao","Carmen, de Valência: o milagre dos pais de Santa Teresinha","Carmen of Valencia: the miracle of St. Thérèse's parents","Valência","Espanha","outubro de 2008","reconhecido","Decreto de 18/3/2015; canonização em 18/10/2015",
  "A menina Carmen, nascida prematura com hemorragia cerebral, sobreviveu sem sequelas depois de os pais pedirem a intercessão de Luís e Zélia Martin.",
  "Processo na Arquidiocese de Valência e Consulta Médica romana.",
  "Francisco canonizou o casal Martin durante o Sínodo da Família, em 18/10/2015 — primeiro casal canonizado junto.",
  ["Vatican.va — homilia de 18/10/2015","Santuário de Lisieux","Arquidiocese de Valência"],
  "en:Louis and Zélie Martin","Louis Zelie Martin canonization", "07-12", tags=("canonizacao","espanha","familia"))
m("sheen_engstrom","canonizacao","James Fulton Engstrom: 61 minutos sem batimentos","James Fulton Engstrom: 61 minutes without a heartbeat","Peoria, Illinois","Estados Unidos","16 de setembro de 2010","reconhecido","Decreto de 6/7/2019 (milagre aprovado); beatificação ainda não realizada",
  "O recém-nascido James Fulton Engstrom ficou 61 minutos sem pulso; a mãe, Bonnie, invocou Fulton Sheen; o menino viveu sem sequelas neurológicas.",
  "Processo na Diocese de Peoria; Consulta Médica aprovou em 2019.",
  "Milagre reconhecido por Francisco em 2019; a beatificação foi adiada por questões ligadas a outra diocese e segue pendente (verificar status antes de publicar).",
  ["Vatican.va — decreto de 6/7/2019","Diocese de Peoria — Fulton Sheen Foundation","Catholic News Agency"],
  "en:Fulton J. Sheen","Fulton Sheen", tags=("beatificacao","eua"))

# ======================= LOURDES — CURAS RECONHECIDAS PELO BUREAU MÉDICO
m("lourdes_70","lourdes","Lourdes, cura nº 70: Irmã Bernadette Moriau","Lourdes, cure no. 70: Sister Bernadette Moriau","Lourdes","França","11 de julho de 2008","reconhecido","Dom Jacques Benoit-Gonnin, bispo de Beauvais (11/2/2018), após o Comitê Médico Internacional de Lourdes",
  "A religiosa Bernadette Moriau, 69 anos, com síndrome da cauda equina e paralisia parcial desde 1980, deixou os aparelhos ortopédicos e os analgésicos dias após voltar de Lourdes.",
  "Bureau Médico de Lourdes e Comitê Médico Internacional (2016) votaram que a cura é inexplicável no estado atual da ciência.",
  "O bispo de Beauvais declarou a cura milagrosa em 11/2/2018 — a 70ª reconhecida em Lourdes.",
  ["Sanctuaire de Lourdes — Bureau des Constatations Médicales","Diocese de Beauvais — declaração de 11/2/2018","Moriau, B. — Ma vie est un miracle (2018)"],
  "en:Our Lady of Lourdes","Lourdes sanctuary basilica", "02-11", tags=("lourdes","cura","seculo xxi"))
m("lourdes_69","lourdes","Lourdes, cura nº 69: Danila Castelli","Lourdes, cure no. 69: Danila Castelli","Lourdes","França","4 de maio de 1989","reconhecido","Dom Giovanni Giudici, bispo de Pavia (20/6/2013)",
  "Danila Castelli, com crises hipertensivas graves por feocromocitoma, sentiu-se curada ao sair das piscinas de Lourdes; os sintomas nunca voltaram.",
  "Cinco avaliações do Bureau Médico entre 1989 e 2010; o Comitê Médico Internacional confirmou em 2011.",
  "Declarada milagrosa pelo bispo de Pavia em 2013.",
  ["Sanctuaire de Lourdes — lista oficial das curas","Diocese de Pavia","Comitê Médico Internacional de Lourdes"],
  "en:Our Lady of Lourdes","Lourdes baths piscines", tags=("lourdes","cura"))
m("lourdes_67","lourdes","Lourdes, cura nº 67: Anna Santaniello","Lourdes, cure no. 67: Anna Santaniello","Lourdes","França","19 de agosto de 1952","reconhecido","Dom Gerardo Pierro, arcebispo de Salerno (21/9/2005)",
  "Anna Santaniello, com doença cardíaca reumática grave (doença de Bouillaud), entrou nas piscinas em maca e saiu andando.",
  "Bureau Médico (1952 e 1953), Comitê Médico Internacional (1960–1964); reconhecimento canônico só em 2005, quando ela tinha 94 anos.",
  "Declarada milagrosa pela arquidiocese de Salerno em 2005.",
  ["Sanctuaire de Lourdes — lista oficial","Arquidiocese de Salerno-Campagna-Acerno","UNITALSI"],
  "en:Our Lady of Lourdes","Lourdes procession sick pilgrims", tags=("lourdes","cura"))
m("lourdes_66","lourdes","Lourdes, cura nº 66: Jean-Pierre Bély","Lourdes, cure no. 66: Jean-Pierre Bély","Lourdes","França","9 de outubro de 1987","reconhecido","Dom Claude Dagens, bispo de Angoulême (9/2/1999)",
  "Jean-Pierre Bély, com esclerose múltipla avançada e invalidez total, recuperou os movimentos após a unção dos enfermos em Lourdes.",
  "Comitê Médico Internacional concluiu em 1998 que a cura era inexplicável.",
  "Reconhecida como milagre em 1999.",
  ["Sanctuaire de Lourdes — lista oficial","Diocese de Angoulême","Comitê Médico Internacional de Lourdes"],
  "en:Our Lady of Lourdes","Lourdes grotto candles", tags=("lourdes","cura"))
m("lourdes_65","lourdes","Lourdes, cura nº 65: Delizia Cirolli","Lourdes, cure no. 65: Delizia Cirolli","Lourdes","França","24 de dezembro de 1976","reconhecido","Dom Salvatore Pappalardo, arcebispo de Catânia (28/6/1989)",
  "Delizia Cirolli, 12 anos, com sarcoma de Ewing no joelho e amputação recomendada, curou-se após a peregrinação a Lourdes.",
  "Bureau Médico e Comitê Internacional (1982) consideraram a cura inexplicável; ela se tornou enfermeira e voluntária em Lourdes.",
  "Reconhecida em 1989 pela arquidiocese de Catânia.",
  ["Sanctuaire de Lourdes — lista oficial","Arquidiocese de Catânia","UNITALSI"],
  "en:Our Lady of Lourdes","Lourdes basilica rosary", tags=("lourdes","cura"))
m("lourdes_01","lourdes","Lourdes, cura nº 1: Catherine Latapie","Lourdes, cure no. 1: Catherine Latapie","Lourdes","França","1º de março de 1858","reconhecido","Dom Bertrand-Sévère Laurence, bispo de Tarbes (18/1/1862)",
  "Catherine Latapie, com paralisia dos dedos após um acidente, mergulhou a mão na nascente recém-descoberta por Bernadette e recuperou o movimento.",
  "Examinada pela comissão episcopal de 1858–1862, foi uma das sete curas citadas no decreto de reconhecimento das aparições.",
  "Primeira cura oficial de Lourdes, reconhecida em 1862.",
  ["Sanctuaire de Lourdes — lista oficial","Decreto de 18/1/1862","Laurentin, R. — Lourdes, documents authentiques"],
  "en:Our Lady of Lourdes","Lourdes spring source grotto", tags=("lourdes","cura","seculo xix"))
m("rudder","lourdes","Pierre de Rudder: a perna fraturada em Oostakker","Pierre de Rudder: the fractured leg at Oostakker","Oostakker, Gante","Bélgica","7 de abril de 1875","reconhecido","Dom Antoine Stillemans, bispo de Gante (25/7/1908)",
  "Pierre de Rudder tinha fratura exposta da tíbia há oito anos, sem consolidação; ao rezar na réplica da gruta de Lourdes em Oostakker, a perna fechou instantaneamente.",
  "Após sua morte, em 1898, os ossos foram exumados e examinados: a fratura estava consolidada com calo ósseo; moldes foram feitos para estudo.",
  "Reconhecido como milagre pelo bispo de Gante em 1908.",
  ["Diocese de Gante — decreto de 1908","Santuário de Oostakker-Lourdes","Boissarie, G. — L'œuvre de Lourdes"],
  "en:Pierre de Rudder","Pierre de Rudder Oostakker", tags=("lourdes","cura","belgica"))

# ======================= CORPOS INCORRUPTOS
m("bernadette_corpo","incorrupto","O corpo de Santa Bernadette","The body of St. Bernadette","Nevers","França","exumações de 1909, 1919 e 1925","reconhecido","Processo de beatificação (atas das exumações); canonizada em 1933",
  "Bernadette Soubirous morreu em 1879; nas três exumações do processo, o corpo foi encontrado íntegro, com relato de médicos e testemunhas.",
  "Atas oficiais assinadas pelos médicos presentes (Jourdan, David; depois Talon e Comte); em 1925 foram retiradas relíquias e aplicada fina camada de cera no rosto e nas mãos.",
  "Beatificada em 1925 e canonizada em 1933; o corpo repousa em urna na capela do convento Saint-Gildard, em Nevers.",
  ["Espace Bernadette — Nevers","Atas das exumações (processo de beatificação)","Vatican.va — canonização de 8/12/1933"],
  "en:Bernadette Soubirous","Bernadette Soubirous body Nevers", "04-16", tags=("incorrupto","franca"))
m("vianney_corpo","incorrupto","O Cura d'Ars incorrupto","The incorrupt Curé of Ars","Ars-sur-Formans","França","exumação de 1904","reconhecido","Processo de beatificação; canonizado em 1925",
  "João Maria Vianney morreu em 1859; exumado em 1904, o corpo foi encontrado ressecado mas íntegro.",
  "Médicos do processo registraram o estado do corpo; o coração foi retirado como relíquia.",
  "Canonizado em 1925; padroeiro dos párocos; corpo exposto na basílica de Ars com máscara de cera.",
  ["Sanctuaire d'Ars","Vatican.va — canonização de 31/5/1925","Diocese de Belley-Ars"],
  "en:John Vianney","Cure d'Ars body basilica", "08-04", tags=("incorrupto","franca"))
m("laboure_corpo","incorrupto","Santa Catarina Labouré: 57 anos depois","St. Catherine Labouré: 57 years later","Paris","França","exumação de 21 de março de 1933","reconhecido","Processo de beatificação; canonizada em 1947",
  "A vidente da Medalha Milagrosa morreu em 1876; exumada em 1933, o corpo estava íntegro, com olhos e membros flexíveis, segundo o relatório médico.",
  "Exumação presidida pelo cardeal Verdier, com médicos e testemunhas; o relatório integra o processo.",
  "Beatificada em 1933 e canonizada em 1947; corpo na capela da Rue du Bac.",
  ["Chapelle de la Médaille Miraculeuse — Paris","Vatican.va — canonização de 27/7/1947","Laurentin, R."],
  "en:Catherine Labouré","Catherine Laboure body Rue du Bac", "11-28", tags=("incorrupto","franca"))
m("zita_corpo","incorrupto","Santa Zita, 700 anos íntegra","St. Zita, intact for 700 years","Lucca, Toscana","Itália","exumação de 1580","reconhecido","Culto confirmado por Inocêncio XII (1696)",
  "A empregada doméstica Zita morreu em 1272; exumada em 1580, o corpo estava intacto e assim permanece exposto na basílica de San Frediano.",
  "Reconhecimentos canônicos em 1580 e 1652; estudos modernos descrevem mumificação natural sem embalsamamento.",
  "Culto confirmado em 1696; padroeira das empregadas domésticas.",
  ["Basilica di San Frediano — Lucca","Arquidiocese de Lucca","Catholic Encyclopedia — Zita"],
  "en:Zita","Santa Zita body Lucca", "04-27", tags=("incorrupto","italia"))
m("xavier_corpo","incorrupto","São Francisco Xavier em Goa","St. Francis Xavier in Goa","Velha Goa","Índia","desde 1553","reconhecido","Processo de canonização (1622); exposições públicas decenais",
  "Morto em 1552 na ilha de Sanchoão, o corpo foi sepultado em cal viva e encontrado íntegro meses depois; levado a Goa em 1554.",
  "Exames de 1554, 1614 (quando o braço direito foi enviado a Roma) e exposições periódicas documentadas pela arquidiocese.",
  "Canonizado em 1622; o corpo é exposto a cada dez anos na Basílica do Bom Jesus (última exposição: 2024–2025).",
  ["Arquidiocese de Goa e Damão — exposição 2024","Basílica do Bom Jesus","Catholic Encyclopedia — Francis Xavier"],
  "en:Francis Xavier","Francis Xavier body Bom Jesus Goa", "12-03", tags=("incorrupto","india"))
m("teresa_avila_corpo","incorrupto","Santa Teresa de Ávila em Alba de Tormes","St. Teresa of Ávila at Alba de Tormes","Alba de Tormes, Salamanca","Espanha","exumações de 1583, 1585, 1750, 1914 e 2024","reconhecido","Processo de canonização (1622); reconhecimento canônico de 2024",
  "Teresa morreu em 1582; exumada nove meses depois, o corpo estava íntegro e exalava perfume, segundo as atas carmelitas.",
  "Em agosto de 2024, a Ordem do Carmelo abriu o sepulcro com médicos e o postulador: o corpo estava no mesmo estado de 1914, conforme laudo divulgado em 2025.",
  "Canonizada em 1622 e doutora da Igreja em 1970.",
  ["Carmelitas Descalços — comunicado da exumação de 2024","Diocese de Salamanca","Vatican News, 2024–2025"],
  "en:Teresa of Ávila","Teresa of Avila tomb Alba de Tormes", "10-15", tags=("incorrupto","espanha"))
m("cecilia_corpo","incorrupto","Santa Cecília e a escultura de Maderno","St. Cecilia and Maderno's sculpture","Trastevere, Roma","Itália","exumação de 1599","reconhecido","Cardeal Paolo Emilio Sfondrati; Clemente VIII",
  "Ao restaurar a basílica em 1599, o cardeal Sfondrati abriu o sarcófago da mártir do século III e encontrou o corpo íntegro, deitado de lado, como o escultor Stefano Maderno o representou.",
  "Testemunhas incluíram o historiador Antonio Bosio; Clemente VIII mandou reinumar o corpo após 30 dias de exposição.",
  "Culto antiquíssimo; padroeira dos músicos.",
  ["Basilica di Santa Cecilia in Trastevere","Bosio, A. — Historia passionis S. Caeciliae (1600)","Catholic Encyclopedia"],
  "en:Saint Cecilia","Santa Cecilia Maderno sculpture Trastevere", "11-22", tags=("incorrupto","italia","roma"))
m("charbel_corpo","incorrupto","São Charbel: o corpo que exsudava","St. Charbel: the body that exuded liquid","Mosteiro de Annaya","Líbano","exumações de 1899, 1927, 1950 e 1965","reconhecido","Processo de beatificação (1965) e canonização (1977)",
  "O eremita maronita morreu em 1898; o corpo foi encontrado íntegro e exsudando um líquido avermelhado por décadas, com luzes relatadas sobre o túmulo.",
  "Comissões médicas de 1950 (com médicos de Beirute) documentaram o fenômeno; milhares de curas foram registradas no mosteiro.",
  "Beatificado em 1965 e canonizado em 1977.",
  ["Mosteiro de São Maron, Annaya","Vatican.va — canonização de 9/10/1977","Ordem Libanesa Maronita"],
  "en:Charbel Makhlouf","Saint Charbel Annaya monastery", "07-24", tags=("incorrupto","libano"))

# ======================= DEVOÇÕES E CASOS ESPECIAIS
m("aparecida","devocao","Aparecida: a imagem encontrada no rio Paraíba","Aparecida: the statue found in the Paraíba river","Guaratinguetá, São Paulo","Brasil","outubro de 1717","reconhecido","Coroação canônica (1904, Pio X); padroeira do Brasil (1930, Pio XI); basílica visitada por três papas",
  "Três pescadores retiraram do rio o corpo e depois a cabeça de uma imagem de terracota de Nossa Senhora da Conceição; a pesca, antes vazia, encheu as redes. A devoção cresceu com relatos de graças.",
  "A Igreja aprovou a devoção e, mais tarde, o título de padroeira; a imagem quebrada em 1978 foi restaurada e segue na basílica. Não há decreto sobre milagres individuais, e sim o reconhecimento da devoção.",
  "Padroeira do Brasil por decreto de Pio XI em 1930; 12 de outubro é feriado nacional desde 1980.",
  ["Santuário Nacional de Aparecida — a12.com","Decreto de Pio XI, 16/7/1930","CNBB"],
  "pt:Nossa Senhora Aparecida","Nossa Senhora Aparecida imagem", "10-12", tags=("brasil","mariana"))
m("ratisbonne","aparicao","A conversão de Alphonse Ratisbonne","The conversion of Alphonse Ratisbonne","Sant'Andrea delle Fratte, Roma","Itália","20 de janeiro de 1842","reconhecido","Inquérito canônico do Vicariato de Roma (1842)",
  "O judeu alsaciano Alphonse Ratisbonne, que usava por aposta uma Medalha Milagrosa, viu a Virgem na igreja de Sant'Andrea delle Fratte e converteu-se no ato; tornou-se sacerdote.",
  "Inquérito do Vicariato de Roma ouviu Ratisbonne e as testemunhas e concluiu em cinco meses.",
  "Decreto de 3/6/1842 reconheceu a conversão como milagre.",
  ["Vicariato de Roma — decreto de 3/6/1842","Sant'Andrea delle Fratte — capela do milagre","Chapelle de la Médaille Miraculeuse"],
  "en:Marie-Alphonse Ratisbonne","Ratisbonne Sant'Andrea delle Fratte", "01-20", tags=("mariana","conversao","roma"))

RESERVA = [
  {"id":"san_gennaro","titulo":"Liquefação do sangue de São Januário","motivo":"A Igreja autoriza o culto mas nunca declarou o fenômeno milagroso; publicar só como 'tradição com culto aprovado', nunca como milagre reconhecido."},
  {"id":"sudario","titulo":"Sudário de Turim","motivo":"A Igreja não se pronuncia sobre a autenticidade; publicar só em pauta sobre o que a Igreja diz e não diz."},
  {"id":"medjugorje","titulo":"Medjugorje","motivo":"Nihil obstat de 19/9/2024 autoriza a devoção sem declarar sobrenaturalidade; só publicar com o status exato."},
  {"id":"wilhelmina","titulo":"Irmã Wilhelmina Lancaster (Gower, 2023)","motivo":"Sem processo canônico aberto; não publicar."},
]

out = {"_nota": __doc__.strip(), "milagres": M, "reserva": RESERVA}
Path(__file__).resolve().parent.parent.joinpath("data/milagres.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
from collections import Counter
print(len(M), "milagres;", dict(Counter(x["tipo"] for x in M)))
