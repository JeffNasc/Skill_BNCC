#!/usr/bin/env python3
"""Extrai as competencias especificas do Ensino Medio (texto literal) do texto do PDF oficial.

Uso: python3 -I extrair_competencias_em.py <em_raw.txt> <saida.json>
Entrada: texto gerado por `pdftotext` (modo padrao) do PDF do Ensino Medio.
Saida: {"LGG": {"1": "...", ...}, "MAT": {...}, "CNT": {...}, "CHS": {...}}
"""
import json
import re
import sys

AREAS = {
    "LGG": "COMPETÊNCIAS ESPECÍFICAS DE LINGUAGENS E SUAS",
    "MAT": "COMPETÊNCIAS ESPECÍFICAS DE MATEMÁTICA E SUAS",
    "CNT": "COMPETÊNCIAS ESPECÍFICAS DE CIÊNCIAS DA NATUREZA E",
    "CHS": "COMPETÊNCIAS ESPECÍFICAS DE CIÊNCIAS HUMANAS E",
}
ESPERADO = {"LGG": 7, "MAT": 5, "CNT": 3, "CHS": 6}
RUIDO = re.compile(r"^(\d{1,3}|BASE NACIONAL|COMUM CURRICULAR|[A-ZÀ-Ú0-9 ,.\-–:]{6,})$")


def juntar(linhas):
    t = ""
    for p in linhas:
        if not t:
            t = p
        elif t.endswith("-") and p[:1].islower():
            t += p
        else:
            t += " " + p
    t = re.sub(r"[\u00ad\u0002\u0007]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    # remove o titulo da secao seguinte (ex.: "5.3.1. CIENCIAS DA NATUREZA E SUAS ..."), se colado ao texto
    return re.sub(r"\s+\d\.\d\.\d\.\s.*$", "", t)


def extrair(texto):
    res = {}
    for area, cab in AREAS.items():
        i = texto.index(cab)
        fim = texto.index("COMPETÊNCIA ESPECÍFICA 1", i)
        linhas = [l.strip() for l in texto[i:fim].splitlines()]
        # remove o titulo da secao (que e todo em maiusculas) e rodapes
        linhas = [l for l in linhas[1:] if l and not RUIDO.match(l) or re.match(r"^\d\.", l)]
        itens, atual = {}, None
        for l in linhas:
            m = re.match(r"^(\d)\.\s*(.*)$", l)
            if m and int(m.group(1)) == (int(atual) + 1 if atual else 1):
                atual = m.group(1)
                itens[atual] = [m.group(2)] if m.group(2) else []
            elif atual:
                itens[atual].append(l)
        res[area] = {k: juntar(v) for k, v in itens.items()}
        if len(res[area]) != ESPERADO[area] or any(not v for v in res[area].values()):
            sys.exit(f"{area}: {len(res[area])} competencias, esperado {ESPERADO[area]}")
    return res


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    r = extrair(open(sys.argv[1], encoding="utf-8").read())
    json.dump(r, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print({a: len(v) for a, v in r.items()})
