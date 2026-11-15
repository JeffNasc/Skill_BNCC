#!/usr/bin/env python3
"""Testes de regressão da base (sem IA). Uso: python3 -I tests/regressao.py [pasta_references]

Verificam fatos que os 17 casos do MANUAL-DE-TESTE.md esperam da base: texto literal de códigos
conhecidos, códigos inexistentes, ausência de Computação, filtro por ano e limites de etapa.
Sai com código 1 se algum teste falhar.
"""
import re, sys, glob
from pathlib import Path

PASTA = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "references")


def linhas():
    for f in glob.glob(f"{PASTA}/**/*.md", recursive=True):
        if f.endswith("indice.md"):
            continue
        for l in open(f, encoding="utf-8"):
            if l.startswith("| ") and not l.startswith("| Código") and not l.startswith("| ---"):
                yield f, [x.replace("\\|", "|") for x in re.split(r"(?<!\\) \| ", l.rstrip("\n")[2:-2])]


TODAS = list(linhas())
POR_CODIGO = {c[0]: (f, c) for f, c in TODAS}
falhas = []


def confere(nome, ok):
    print(("ok    " if ok else "FALHA ") + nome)
    if not ok:
        falhas.append(nome)


# B1, B2, B4: texto literal e página
confere("B1 EF07CI01 texto e pág. 347", POR_CODIGO["EF07CI01"][1][-2].startswith("Discutir a aplicação, ao longo da história, das máquinas simples") and POR_CODIGO["EF07CI01"][1][-1] == "347")
confere("B2 EI03ET07 texto e pág. 52", POR_CODIGO["EI03ET07"][1][3] == "Relacionar números às suas respectivas quantidades e identificar o antes, o depois e o entre em uma sequência." and POR_CODIGO["EI03ET07"][1][-1] == "52")
confere("B4 EM13LP01 pág. 498", "condições de produção" in POR_CODIGO["EM13LP01"][1][-2] and POR_CODIGO["EM13LP01"][1][-1] == "498")
confere("A1 EF06MA07 frações pág. 301", POR_CODIGO["EF06MA07"][1][-1] == "301" and "frações" in POR_CODIGO["EF06MA07"][1][-2])
# B3: código inexistente
confere("B3 EF06MA99 não existe", "EF06MA99" not in POR_CODIGO)
# Totais
confere("totais 93/1304/179", (sum(c.startswith("EI") for c in POR_CODIGO), sum(c.startswith("EF") for c in POR_CODIGO), sum(c.startswith("EM") for c in POR_CODIGO)) == (93, 1304, 179))
# C1: nenhuma habilidade de Computação
confere("C1 sem habilidades de Computação", not any(re.match(r"(EF\d{2}CO|EI\d{2}CO|EM13CO)", c) for c in POR_CODIGO))
# C3: Inglês só nos anos finais
confere("C3 Inglês só do 6º ao 9º", all(re.match(r"EF(06|07|08|09|67|89)LI", c) for c in POR_CODIGO if re.match(r"EF\d{2}LI", c)))
# D1: 2º ano de LP deve reunir blocos EF12, EF15 e EF02, com 67 habilidades
lp2 = [c for f, c in TODAS if re.match(r"EF\d{2}LP", c[0]) and "2" in [x.strip() for x in c[2].split(",")]]
blocos = {c[0][:4] for c in lp2}
confere("D1 LP 2º ano: 67 habilidades (EF02, EF12, EF15)", len(lp2) == 67 and {"EF02", "EF12", "EF15"} <= blocos)
leit = sorted(c[0] for c in lp2 if c[0].startswith("EF02") and c[4].startswith("Leitura"))
confere("D1 EF02 de leitura presentes (EF02LP12, 20, 21, 26)", {"EF02LP12", "EF02LP20", "EF02LP21", "EF02LP26"} <= set(leit))
# Ensino Médio: LP com 2 dígitos, demais com 3
confere("formato EM13LP 2 dígitos", all(re.fullmatch(r"EM13LP\d{2}", c) for c in POR_CODIGO if c.startswith("EM13LP")))
# Hifenização: nenhum composto conhecido sem hífen
confere("sem 'gráficovisuais'", not any("gráficovisuais" in " ".join(c) for f, c in TODAS))
# Sem caracteres de controle
confere("sem caracteres de controle", not any(re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f­]", " ".join(c)) for f, c in TODAS))

print(f"\n{len(falhas)} falha(s)")
sys.exit(1 if falhas else 0)
