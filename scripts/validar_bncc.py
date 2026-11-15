#!/usr/bin/env python3
"""Valida os arquivos Markdown gerados contra a contagem oficial da BNCC.

Uso:
    python3 validar_bncc.py ../references

Confere, para cada arquivo: formato das linhas, codigos validos, ausencia de duplicados, numeracao
continua e total esperado. Confere tambem os totais por etapa. Sai com codigo 1 se algo falhar.
"""
import os
import re
import sys
from collections import defaultdict

# Contagem de referencia, feita de forma independente sobre os PDFs oficiais (codigos unicos entre
# parenteses). Veja docs/contagem-oficial.md.
TOTAL_ETAPA = {"EI": 93, "EF": 1304, "EM": 179}
ESPERADO_ARQUIVO = {
    "educacao-infantil.md": 93,
    "ensino-fundamental/anos-iniciais/lingua-portuguesa-1o-ao-5o.md": 19,
    "ensino-fundamental/anos-iniciais/lingua-portuguesa-1o-e-2o.md": 74,
    "ensino-fundamental/anos-iniciais/lingua-portuguesa-3o-ao-5o.md": 113,
    "ensino-fundamental/anos-iniciais/arte.md": 26,
    "ensino-fundamental/anos-iniciais/educacao-fisica.md": 27,
    "ensino-fundamental/anos-iniciais/matematica.md": 126,
    "ensino-fundamental/anos-iniciais/ciencias.md": 48,
    "ensino-fundamental/anos-iniciais/geografia.md": 56,
    "ensino-fundamental/anos-iniciais/historia.md": 52,
    "ensino-fundamental/anos-iniciais/ensino-religioso.md": 33,
    "ensino-fundamental/anos-finais/lingua-portuguesa-6o-ao-9o.md": 56,
    "ensino-fundamental/anos-finais/lingua-portuguesa-6o-e-7o.md": 64,
    "ensino-fundamental/anos-finais/lingua-portuguesa-8o-e-9o.md": 65,
    "ensino-fundamental/anos-finais/arte.md": 35,
    "ensino-fundamental/anos-finais/educacao-fisica.md": 42,
    "ensino-fundamental/anos-finais/lingua-inglesa.md": 88,
    "ensino-fundamental/anos-finais/matematica.md": 121,
    "ensino-fundamental/anos-finais/ciencias.md": 63,
    "ensino-fundamental/anos-finais/geografia.md": 67,
    "ensino-fundamental/anos-finais/historia.md": 99,
    "ensino-fundamental/anos-finais/ensino-religioso.md": 30,
    "ensino-medio/linguagens.md": 27,
    "ensino-medio/lingua-portuguesa.md": 53,
    "ensino-medio/matematica.md": 45,
    "ensino-medio/ciencias-da-natureza.md": 23,
    "ensino-medio/ciencias-humanas.md": 31,
}
# Intervalos de paginas impressas de cada secao. EI e EF seguem o sumario do PDF oficial de EI/EF;
# o Ensino Medio segue a numeracao propria do PDF oficial separado do EM (versao final, 179 habilidades).
PAGINAS_SUMARIO = {
    "educacao-infantil.md": (44, 52),
    "ensino-fundamental/anos-iniciais/lingua-portuguesa-1o-ao-5o.md": (89, 135),
    "ensino-fundamental/anos-iniciais/lingua-portuguesa-1o-e-2o.md": (89, 135),
    "ensino-fundamental/anos-iniciais/lingua-portuguesa-3o-ao-5o.md": (89, 135),
    "ensino-fundamental/anos-finais/lingua-portuguesa-6o-ao-9o.md": (136, 192),
    "ensino-fundamental/anos-finais/lingua-portuguesa-6o-e-7o.md": (136, 192),
    "ensino-fundamental/anos-finais/lingua-portuguesa-8o-e-9o.md": (136, 192),
    "ensino-fundamental/anos-iniciais/arte.md": (199, 204),
    "ensino-fundamental/anos-finais/arte.md": (205, 212),
    "ensino-fundamental/anos-iniciais/educacao-fisica.md": (224, 230),
    "ensino-fundamental/anos-finais/educacao-fisica.md": (231, 240),
    "ensino-fundamental/anos-finais/lingua-inglesa.md": (247, 264),
    "ensino-fundamental/anos-iniciais/matematica.md": (276, 297),
    "ensino-fundamental/anos-finais/matematica.md": (298, 320),
    "ensino-fundamental/anos-iniciais/ciencias.md": (331, 342),
    "ensino-fundamental/anos-finais/ciencias.md": (343, 352),
    "ensino-fundamental/anos-iniciais/geografia.md": (367, 380),
    "ensino-fundamental/anos-finais/geografia.md": (381, 396),
    "ensino-fundamental/anos-iniciais/historia.md": (403, 415),
    "ensino-fundamental/anos-finais/historia.md": (416, 434),
    "ensino-fundamental/anos-iniciais/ensino-religioso.md": (442, 451),
    "ensino-fundamental/anos-finais/ensino-religioso.md": (452, 460),
    "ensino-medio/linguagens.md": (483, 490),
    "ensino-medio/lingua-portuguesa.md": (497, 518),
    "ensino-medio/matematica.md": (523, 535),
    "ensino-medio/ciencias-da-natureza.md": (539, 547),
    "ensino-medio/ciencias-humanas.md": (558, 567),
}
# Competencias especificas do Ensino Medio que devem constar no topo de cada arquivo de area.
COMPETENCIAS_EM = {"linguagens.md": 7, "matematica.md": 5, "ciencias-da-natureza.md": 3, "ciencias-humanas.md": 6}
PADRAO = {
    "EI": re.compile(r"^EI0[123](?:EO|CG|TS|EF|ET)\d{2}$"),
    "EF": re.compile(r"^EF\d{2}[A-Z]{2}\d{2}$"),
    "EM": re.compile(r"^EM13(?:LGG\d{3}|LP\d{2}|MAT\d{3}|CNT\d{3}|CHS\d{3})$"),
}


def linhas_de_dados(caminho):
    """Linhas da tabela, sem cabecalho. Divide por ' | ' respeitando '\\|' escapado."""
    for l in open(caminho, encoding="utf-8"):
        l = l.rstrip("\n")
        if not l.startswith("| ") or l.startswith("| Código") or l.startswith("| ---"):
            continue
        celulas = re.split(r"(?<!\\) \| ", l[2:-2] if l.endswith(" |") else l[2:])
        yield celulas


def sequencia_ok(codigos, etapa):
    """Numeracao sem lacunas dentro de cada prefixo (bloco+componente no EF, area+competencia no EM)."""
    falhas = []
    grupos = defaultdict(list)
    for c in codigos:
        if etapa == "EF":
            grupos[c[:6]].append(int(c[6:]))
        elif etapa == "EI":
            grupos[c[:6]].append(int(c[6:]))
        else:
            m = re.match(r"EM13(LGG|MAT|CNT|CHS)(\d)(\d{2})$", c)
            if m:
                grupos[m.group(1) + m.group(2)].append(int(m.group(3)))
            else:
                grupos["LP"].append(int(c[6:]))
    for g, nums in grupos.items():
        faltam = [n for n in range(1, max(nums) + 1) if n not in set(nums)]
        # Educacao Infantil: EO06/EO07, ET07/ET08 existem so em algumas faixas, entao nao exigimos
        # sequencia completa por faixa nesses prefixos.
        if faltam and etapa != "EI":
            falhas.append((g, faltam))
    return falhas


def main(raiz):
    erros = []
    por_etapa = defaultdict(set)
    for rel, esperado in ESPERADO_ARQUIVO.items():
        caminho = os.path.join(raiz, rel)
        if not os.path.exists(caminho):
            erros.append(f"{rel}: arquivo ausente")
            continue
        conteudo = open(caminho, encoding="utf-8").read()
        if re.search(r"[\x00-\x08\x0b-\x1f\u00ad\ufffd]", conteudo):
            erros.append(f"{rel}: caractere de controle ou de substituicao no texto")
        if re.search(r"\d\.\d\.\d\. [A-ZÀ-Ú]{3,}", conteudo):
            erros.append(f"{rel}: titulo de secao do PDF colado ao texto")
        etapa = "EI" if rel.startswith("educacao") else "EF" if rel.startswith("ensino-fundamental") else "EM"
        codigos = []
        for cel in linhas_de_dados(caminho):
            if not cel or not PADRAO[etapa].match(cel[0]):
                erros.append(f"{rel}: linha com codigo invalido: {cel[:1]}")
                continue
            texto = cel[3] if etapa == "EI" else cel[-2]
            if len(texto.strip()) < 15:
                erros.append(f"{rel}: texto vazio ou curto em {cel[0]}")
            if etapa == "EF":
                anos = [a.strip() for a in cel[2].split(",")]
                if not all(a.isdigit() and 1 <= int(a) <= 9 for a in anos):
                    erros.append(f"{rel}: coluna 'Aplica-se aos anos' invalida em {cel[0]}: {cel[2]!r}")
            if etapa == "EF" and (len(cel) < 7 or not cel[-4].strip() or not cel[-3].strip()):
                erros.append(f"{rel}: unidade tematica ou objeto de conhecimento ausente em {cel[0]}")
            codigos.append(cel[0])
            ini, fim = PAGINAS_SUMARIO[rel]
            if not cel[-1].isdigit() or not (ini <= int(cel[-1]) <= fim):
                erros.append(f"{rel}: pagina {cel[-1]} fora do intervalo {ini}-{fim} em {cel[0]}")
        if etapa == "EM" and os.path.basename(rel) in COMPETENCIAS_EM:
            n_comp = sum(1 for l in open(caminho, encoding="utf-8") if l.startswith("- Competência "))
            if n_comp != COMPETENCIAS_EM[os.path.basename(rel)]:
                erros.append(f"{rel}: {n_comp} competencias especificas, esperado {COMPETENCIAS_EM[os.path.basename(rel)]}")
        if len(codigos) != esperado:
            erros.append(f"{rel}: {len(codigos)} habilidades, esperado {esperado}")
        if len(set(codigos)) != len(codigos):
            erros.append(f"{rel}: codigos duplicados")
        for g, faltam in sequencia_ok(codigos, etapa):
            erros.append(f"{rel}: lacuna na numeracao de {g}: {faltam}")
        repetidos = por_etapa[etapa] & set(codigos)
        if repetidos:
            erros.append(f"{rel}: codigos ja presentes em outro arquivo: {sorted(repetidos)[:5]}")
        por_etapa[etapa] |= set(codigos)
        print(f"ok  {len(codigos):4d}  {rel}")
    for etapa, esperado in TOTAL_ETAPA.items():
        if len(por_etapa[etapa]) != esperado:
            erros.append(f"total {etapa}: {len(por_etapa[etapa])}, esperado {esperado}")
    print(f"\nTotais: " + " | ".join(f"{e}={len(por_etapa[e])}" for e in TOTAL_ETAPA) +
          f" | geral={sum(len(v) for v in por_etapa.values())}")
    if erros:
        print("\nFALHAS:")
        for e in erros:
            print(" -", e)
        sys.exit(1)
    print("Validacao concluida sem falhas.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
