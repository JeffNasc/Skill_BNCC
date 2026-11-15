#!/usr/bin/env python3
"""Associa cada habilidade do Ensino Fundamental a sua unidade tematica (ou pratica de linguagem)
e ao seu objeto de conhecimento, lendo a geometria das tabelas do PDF oficial.

Uso: python3 -I extrair_objetos.py <pdf_ef_reparado> <saida.json>

Em cada pagina de habilidades, as linhas horizontais da coluna de objetos delimitam as celulas.
Cada habilidade pertence a celula em que seu codigo aparece. Unidade e campo (faixas de titulo como
"CAMPO ARTISTICO-LITERARIO" ou "EIXO ORALIDADE") se propagam para as linhas seguintes e paginas
seguintes ate que outra faixa apareca.
"""
import json
import re
import sys

import pdfplumber

COD = re.compile(r"^\((EF\d{2}[A-Z]{2}\d{2})\)$")
CAB_UNIDADE = re.compile(r"^(UNIDADES|PRÁTICAS|CAMPOS)$")


# Distancia vertical (pt) entre linhas acima da qual comeca um novo objeto. Quebra de linha dentro de
# um mesmo objeto tem ~12,6 pt; objetos distintos na mesma celula tem ~18,5 pt.
SALTO_NOVO_OBJETO = 15.5


def linhas_texto(palavras):
    """Agrupa palavras em linhas (por proximidade vertical). Devolve [(topo, texto), ...]."""
    palavras = sorted(palavras, key=lambda w: (round(w["top"]), w["x0"]))
    linhas, atual, ref = [], [], None
    for w in palavras:
        if ref is None or abs(w["top"] - ref) <= 3:
            atual.append(w)
            ref = w["top"] if ref is None else ref
        else:
            linhas.append((ref, atual))
            atual, ref = [w], w["top"]
    if atual:
        linhas.append((ref, atual))
    return [(t, " ".join(x["text"] for x in sorted(l, key=lambda w: w["x0"]))) for t, l in linhas]


def separar_objetos(linhas):
    """Divide as linhas de uma celula em objetos de conhecimento.

    Devolve [(linhas_do_item, eh_subitem)]. Um objeto novo comeca quando o espacamento vertical passa de
    SALTO_NOVO_OBJETO. Uma linha que comeca com o marcador "•" abre um subitem do objeto anterior.
    """
    itens, anterior = [], None
    for topo, texto in linhas:
        if texto.startswith("•"):
            itens.append(([texto.lstrip("• ").strip()], True))
        elif not itens or (anterior is not None and topo - anterior > SALTO_NOVO_OBJETO):
            itens.append(([texto], False))
        else:
            itens[-1][0].append(texto)
        anterior = topo
    return itens


def montar_objeto(itens):
    """Junta os itens: objetos separados por " • "; subitens entre colchetes, junto ao objeto a que pertencem."""
    saida = []
    for linhas, sub in itens:
        texto = juntar(linhas)
        if not texto:
            continue
        if sub and saida:
            saida[-1] += f" [subitem: {texto}]"
        else:
            saida.append(texto)
    return " • ".join(saida)


def juntar(linhas):
    t = ""
    for p in linhas:
        if not t:
            t = p
        elif t.endswith("-") and p[:1].islower():
            t += p
        else:
            t += " " + p
    t = t.replace("­", "").replace("\u0002", "")
    return re.sub(r"\s+", " ", t).strip()


def processar(caminho):
    resultado, ordem = {}, []
    unidade = campo = objeto = prefixo = None
    faixa_nova = False
    with pdfplumber.open(caminho) as pdf:
        for num, pg in enumerate(pdf.pages, start=1):
            palavras = pg.extract_words(keep_blank_chars=False, use_text_flow=False)
            codigos = [w for w in palavras if COD.match(w["text"])]
            if not codigos:
                continue
            x_hab = min(w["x0"] for w in codigos) - 4
            # cabecalhos da pagina: a segunda coluna comeca em "OBJETOS"
            obj_cab = [w for w in palavras if w["text"] == "OBJETOS" and w["x0"] < x_hab]
            if not obj_cab:
                continue
            x_obj = max(w["x0"] for w in obj_cab) - 4
            # fronteiras de linha: bordas horizontais que cobrem a coluna de objetos
            tops = sorted({round(e["top"]) for e in pg.edges
                           if e["orientation"] == "h" and e["x0"] <= x_obj + 20 and e["x1"] >= x_obj + 150})
            if not tops:
                continue
            tops = tops + [pg.height + 1]
            for ini, fim in zip(tops, tops[1:]):
                celula = lambda a, b: [w for w in palavras
                                       if ini - 1 <= w["top"] < fim - 1 and a <= w["x0"] < b]
                txt_unid = juntar([t for _, t in linhas_texto(celula(0, x_obj))])
                txt_obj = montar_objeto(separar_objetos(linhas_texto(celula(x_obj, x_hab))))
                if txt_unid.isdigit():
                    txt_unid = ""  # numero de pagina
                cods = [w for w in celula(x_hab, 99999) if COD.match(w["text"])]
                if CAB_UNIDADE.match(txt_unid.split(" ")[0] if txt_unid else "") and "OBJETOS" in txt_obj:
                    continue  # linha de cabecalho
                if not cods and "OBJETOS DE CONHECIMENTO" in juntar([t for _, t in linhas_texto(celula(0, 99999))]):
                    continue  # cabecalho de tabela em linha unica
                if not cods:
                    # faixa de titulo (campo de atuacao, eixo etc.), que pode trazer uma descricao
                    # apos " – ". Guardamos so o titulo.
                    if txt_unid:
                        inteira = juntar([t for _, t in linhas_texto(celula(0, 99999))])
                        campo = inteira.split(" – ")[0].strip()
                        faixa_nova = True
                    continue
                if txt_unid:
                    unidade = txt_unid
                if txt_obj:
                    objeto = txt_obj
                for w in sorted(cods, key=lambda w: w["top"]):
                    c = COD.match(w["text"]).group(1)
                    # Ao mudar de bloco/componente, o campo anterior so vale se uma faixa nova apareceu.
                    if c[4:6] != prefixo and not faixa_nova:
                        campo = None
                    prefixo = c[4:6]
                    faixa_nova = False
                    resultado.setdefault(c, []).append(
                        {"unidade": unidade, "campo": campo, "objeto": objeto, "pdf_pag": num})
                    ordem.append(c)
    return resultado, ordem


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    res, ordem = processar(sys.argv[1])
    json.dump(res, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("habilidades com objeto:", len(res), "| ocorrencias:", len(ordem))
