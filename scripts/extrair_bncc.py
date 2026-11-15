#!/usr/bin/env python3
"""Extrai as habilidades da BNCC dos PDFs oficiais do MEC e gera os arquivos Markdown da skill.

Requisitos: Python 3.9+, `pdftotext` (poppler-utils) e, opcionalmente, `qpdf` para reparar PDFs com
estrutura danificada.

Uso:
    python3 extrair_bncc.py --ei-ef BNCC_EI_EF_110518_versaofinal_site.pdf \
                            --em BNCC_EnsinoMedio_embaixa_site_110518.pdf \
                            --saida ../references

O texto de cada habilidade e copiado literalmente do PDF. Nada e resumido, reescrito ou corrigido.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extrair_objetos import processar as processar_objetos  # noqa: E402
from extrair_competencias_em import extrair as extrair_competencias_em  # noqa: E402

# --------------------------------------------------------------------------------------
# Padroes de codigo e tabelas de apoio
# --------------------------------------------------------------------------------------
PADRAO = {
    "EI": r"EI0[123](?:EO|CG|TS|EF|ET)\d{2}",
    "EF": r"EF\d{2}[A-Z]{2}\d{2}",
    "EM": r"EM13(?:LGG\d{3}|LP\d{2}|MAT\d{3}|CNT\d{3}|CHS\d{3})",
}
INICIO = {etapa: re.compile(rf"^\(({p})\)\s*(.*)$") for etapa, p in PADRAO.items()}

FONTE_EI_EF = "BNCC, Educação Infantil e Ensino Fundamental, versão homologada (MEC, 2017)"
FONTE_EM = "BNCC, Ensino Médio, versão homologada (MEC, 2018)"

FAIXA_EI = {
    "01": "Bebês (0 a 1 ano e 6 meses)",
    "02": "Crianças bem pequenas (1 ano e 7 meses a 3 anos e 11 meses)",
    "03": "Crianças pequenas (4 anos a 5 anos e 11 meses)",
}
CAMPO_EI = {
    "EO": "O eu, o outro e o nós",
    "CG": "Corpo, gestos e movimentos",
    "TS": "Traços, sons, cores e formas",
    "EF": "Escuta, fala, pensamento e imaginação",
    "ET": "Espaços, tempos, quantidades, relações e transformações",
}

# bloco de anos do codigo EF -> (rotulo, ano inicial, ano final)
BLOCO_EF = {
    "01": ("1º ano", 1, 1), "02": ("2º ano", 2, 2), "03": ("3º ano", 3, 3),
    "04": ("4º ano", 4, 4), "05": ("5º ano", 5, 5), "06": ("6º ano", 6, 6),
    "07": ("7º ano", 7, 7), "08": ("8º ano", 8, 8), "09": ("9º ano", 9, 9),
    "12": ("1º e 2º anos", 1, 2), "15": ("1º ao 5º ano", 1, 5), "35": ("3º ao 5º ano", 3, 5),
    "67": ("6º e 7º anos", 6, 7), "69": ("6º ao 9º ano", 6, 9), "89": ("8º e 9º anos", 8, 9),
}
COMPONENTE_EF = {
    "LP": ("Língua Portuguesa", "lingua-portuguesa"),
    "AR": ("Arte", "arte"),
    "EF": ("Educação Física", "educacao-fisica"),
    "LI": ("Língua Inglesa", "lingua-inglesa"),
    "MA": ("Matemática", "matematica"),
    "CI": ("Ciências", "ciencias"),
    "GE": ("Geografia", "geografia"),
    "HI": ("História", "historia"),
    "ER": ("Ensino Religioso", "ensino-religioso"),
}
# Lingua Portuguesa e dividida por bloco de anos para que cada consulta carregue pouco texto.
# Para planejar um ano, abre-se o arquivo do bloco "ao 5o"/"ao 9o" (vale para todos os anos) e o do
# par de anos correspondente.
SUBARQUIVO_LP = {
    "anos-iniciais": {
        "15": "1o-ao-5o", "12": "1o-e-2o", "01": "1o-e-2o", "02": "1o-e-2o",
        "35": "3o-ao-5o", "03": "3o-ao-5o", "04": "3o-ao-5o", "05": "3o-ao-5o",
    },
    "anos-finais": {
        "69": "6o-ao-9o", "67": "6o-e-7o", "06": "6o-e-7o", "07": "6o-e-7o",
        "89": "8o-e-9o", "08": "8o-e-9o", "09": "8o-e-9o",
    },
}
ROTULO_SUBARQUIVO = {
    "1o-ao-5o": "habilidades que valem do 1º ao 5º ano",
    "1o-e-2o": "habilidades do 1º e do 2º anos (inclui as do bloco 1º e 2º anos)",
    "3o-ao-5o": "habilidades do 3º ao 5º ano (inclui as do bloco 3º ao 5º anos)",
    "6o-ao-9o": "habilidades que valem do 6º ao 9º ano",
    "6o-e-7o": "habilidades do 6º e do 7º anos (inclui as do bloco 6º e 7º anos)",
    "8o-e-9o": "habilidades do 8º e do 9º anos (inclui as do bloco 8º e 9º anos)",
}
SEGMENTO = {
    "anos-iniciais": "Anos Iniciais (1º ao 5º ano)",
    "anos-finais": "Anos Finais (6º ao 9º ano)",
}
AREA_EM = {
    "LGG": ("Linguagens e suas Tecnologias", "linguagens"),
    "LP": ("Língua Portuguesa", "lingua-portuguesa"),
    "MAT": ("Matemática e suas Tecnologias", "matematica"),
    "CNT": ("Ciências da Natureza e suas Tecnologias", "ciencias-da-natureza"),
    "CHS": ("Ciências Humanas e Sociais Aplicadas", "ciencias-humanas"),
}


# --------------------------------------------------------------------------------------
# PDF -> texto
# --------------------------------------------------------------------------------------
def pdf_para_texto(pdf, tmp):
    """Converte o PDF em texto no modo de leitura padrao (uma celula de tabela por bloco).

    Devolve (texto, caminho do PDF legivel), pois o PDF pode precisar de reparo pelo qpdf.
    """
    destino = os.path.join(tmp, os.path.basename(pdf) + ".txt")
    r = subprocess.run(["pdftotext", pdf, destino], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(destino) or os.path.getsize(destino) < 1000:
        if not shutil.which("qpdf"):
            sys.exit(f"Falha ao ler {pdf} e qpdf nao esta instalado para repara-lo.")
        reparado = os.path.join(tmp, "reparado.pdf")
        subprocess.run(["qpdf", pdf, reparado], capture_output=True, text=True)  # avisos sao normais
        r = subprocess.run(["pdftotext", reparado, destino], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"Falha ao ler {pdf}: {r.stderr.strip()}")
    legivel = reparado if "reparado" in locals() else pdf
    with open(destino, encoding="utf-8") as f:
        return f.read(), legivel


# --------------------------------------------------------------------------------------
# Extracao
# --------------------------------------------------------------------------------------
def mapa_paginas(paginas, janela=20):
    """Numero impresso de cada pagina do PDF.

    Linhas formadas so por digitos podem ser o numero do rodape, mas tambem numeros de competencia
    dentro das tabelas. Como a numeracao impressa avanca no mesmo passo que as paginas do PDF, o
    deslocamento (impresso - pagina do PDF) e constante num trecho do documento. Para cada pagina,
    usa-se o deslocamento mais comum numa janela de paginas vizinhas."""
    deslocamentos = []
    for i, pg in enumerate(paginas, start=1):
        nums = {int(l.strip()) for l in pg.splitlines() if re.fullmatch(r"\d{1,3}", l.strip())}
        deslocamentos.append({n - i for n in nums})
    mapa = []
    total = len(paginas)
    for i in range(1, total + 1):
        contagem = Counter()
        for j in range(max(1, i - janela), min(total, i + janela) + 1):
            contagem.update(deslocamentos[j - 1])
        desloc = contagem.most_common(1)[0][0] if contagem else 0
        mapa.append(i + desloc)
    return mapa


def juntar(partes):
    """Une as linhas de uma habilidade. Preserva hifens, pois nenhuma palavra hifenizada por
    quebra de linha foi encontrada no material (conferido na validacao)."""
    t = ""
    for p in partes:
        if not t:
            t = p
        elif t.endswith("-") and p[:1].islower():
            t += p
        else:
            t += " " + p
    t = t.replace("­", "").replace("\u0002", "")
    return re.sub(r"\s+", " ", t).strip()


def extrair(texto, etapa):
    """Retorna {codigo: [ocorrencias]}. Cada habilidade comeca em uma linha '(CODIGO) ...' e vai ate
    a proxima linha em branco ou o proximo codigo."""
    achados = defaultdict(list)
    paginas = texto.split("\f")
    impressas = mapa_paginas(paginas)
    for num_pdf, pagina in enumerate(paginas, start=1):
        impressa = impressas[num_pdf - 1]
        linhas = pagina.splitlines()
        j = 0
        while j < len(linhas):
            m = INICIO[etapa].match(linhas[j].strip())
            if not m:
                j += 1
                continue
            codigo, resto = m.group(1), m.group(2)
            partes = [resto] if resto else []
            j += 1
            while j < len(linhas):
                l = linhas[j].strip()
                if l == "" or INICIO[etapa].match(l):
                    break
                partes.append(l)
                j += 1
            achados[codigo].append(
                {"codigo": codigo, "texto": juntar(partes), "pag": impressa or num_pdf, "pdf_pag": num_pdf}
            )
    return achados


def escolher(achados, preferir):
    """Resolve codigos que aparecem mais de uma vez. No EI e no EF, as repeticoes sao exemplos da
    secao de estrutura (paginas iniciais), entao vale a ultima ocorrencia. No EM, a repeticao e um
    quadro-resumo no fim, entao vale a primeira. Os textos repetidos precisam ser identicos."""
    final = {}
    for codigo, ocs in achados.items():
        textos = {o["texto"] for o in ocs}
        if len(textos) > 1:
            sys.exit(f"{codigo} aparece com textos diferentes: {textos}")
        final[codigo] = ocs[-1] if preferir == "ultima" else ocs[0]
    return final


# --------------------------------------------------------------------------------------
# Escrita dos arquivos
# --------------------------------------------------------------------------------------
def cel(s):
    return s.replace("|", "\\|")


def escrever(caminho, titulo, linhas_cabecalho, colunas, linhas):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {titulo}\n\n")
        for l in linhas_cabecalho:
            f.write(f"{l}\n")
        f.write("\n")
        f.write("| " + " | ".join(colunas) + " |\n")
        f.write("| " + " | ".join("---" for _ in colunas) + " |\n")
        for linha in linhas:
            f.write("| " + " | ".join(cel(str(c)) for c in linha) + " |\n")


def gerar_ei(dados, saida, indice):
    linhas = []
    for codigo in sorted(dados, key=lambda c: (c[4:6] and list(CAMPO_EI).index(c[4:6]), c[2:4], int(c[6:]))):
        d = dados[codigo]
        linhas.append([codigo, FAIXA_EI[codigo[2:4]], CAMPO_EI[codigo[4:6]], d["texto"], d["pag"]])
    caminho = os.path.join(saida, "educacao-infantil.md")
    escrever(
        caminho,
        "Educação Infantil: objetivos de aprendizagem e desenvolvimento",
        [f"Fonte: {FONTE_EI_EF}. Texto literal.", f"Total: {len(linhas)} objetivos."],
        ["Código", "Faixa etária", "Campo de experiências", "Objetivo", "Pág."],
        linhas,
    )
    indice.append(("Educação Infantil", "Todos os campos de experiências", "0 a 5 anos e 11 meses",
                   "educacao-infantil.md", len(linhas)))


def chave_ef(codigo):
    _, ini, fim = BLOCO_EF[codigo[2:4]]
    return (ini, -fim, int(codigo[6:]))


def gerar_ef(dados, saida, indice, objetos):
    grupos = defaultdict(list)
    for codigo, d in dados.items():
        rotulo, ini, fim = BLOCO_EF[codigo[2:4]]
        seg = "anos-iniciais" if ini <= 5 else "anos-finais"
        comp = codigo[4:6]
        parte = SUBARQUIVO_LP[seg][codigo[2:4]] if comp == "LP" else None
        grupos[(seg, comp, parte)].append((codigo, rotulo, ini, fim, d))
    for (seg, comp, parte), itens in sorted(grupos.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2] or "")):
        nome, slug = COMPONENTE_EF[comp]
        itens.sort(key=lambda x: chave_ef(x[0]))
        info = {c: objetos[c][0] for c, *_ in itens}
        # LP organiza por pratica de linguagem; as demais por unidade tematica.
        rotulo_unidade = "Prática de linguagem" if comp == "LP" else "Unidade temática"
        com_campo = any(i["campo"] for i in info.values())
        linhas = []
        for c, rot, ini, fim, d in itens:
            i = info[c]
            anos = ", ".join(str(a) for a in range(ini, fim + 1))
            linha = [c, rot, anos] + ([i["campo"] or ""] if com_campo else [])
            linhas.append(linha + [i["unidade"], i["objeto"], d["texto"], d["pag"]])
        colunas = (["Código", "Ano", "Aplica-se aos anos"] + (["Campo de atuação / eixo"] if com_campo else [])
                   + [rotulo_unidade, "Objeto de conhecimento", "Habilidade", "Pág."])
        nome_arq = f"{slug}-{parte}" if parte else slug
        rel = os.path.join("ensino-fundamental", seg, f"{nome_arq}.md")
        cab = [f"Fonte: {FONTE_EI_EF}. Texto literal.", f"Total: {len(linhas)} habilidades."]
        if parte:
            cab.append(f"Este arquivo traz as {ROTULO_SUBARQUIVO[parte]}. Para planejar um ano, abra também os "
                       f"outros arquivos de {nome} do mesmo segmento que incluam esse ano "
                       f"(veja a tabela \"Qual arquivo abrir\" em indice.md).")
        escrever(
            os.path.join(saida, rel),
            f"{nome}: Ensino Fundamental, {SEGMENTO[seg]}" + (f" ({parte.replace('o', 'º').replace('-', ' ')})" if parte else ""),
            cab,
            colunas,
            linhas,
        )
        indice.append((f"Ensino Fundamental, {SEGMENTO[seg]}", nome,
                       ROTULO_SUBARQUIVO[parte].replace("habilidades ", "") if parte else "ver colunas Ano e Aplica-se aos anos",
                       rel.replace(os.sep, "/"), len(linhas)))


def gerar_em(dados, saida, indice, competencias):
    grupos = defaultdict(list)
    for codigo, d in dados.items():
        area = re.match(r"EM13(LGG|LP|MAT|CNT|CHS)", codigo).group(1)
        grupos[area].append((codigo, d))
    for area in ("LGG", "LP", "MAT", "CNT", "CHS"):
        nome, slug = AREA_EM[area]
        itens = sorted(grupos[area], key=lambda x: x[0])
        if area == "LP":
            linhas = [[c, d["texto"], d["pag"]] for c, d in itens]
            colunas = ["Código", "Habilidade", "Pág."]
        else:
            linhas = [[c, c[7], d["texto"], d["pag"]] for c, d in itens]
            colunas = ["Código", "Competência específica", "Habilidade", "Pág."]
        rel = os.path.join("ensino-medio", f"{slug}.md")
        if area == "LP":
            comp_linhas = ["As habilidades de Língua Portuguesa não têm número de competência no código. "
                           "Elas se relacionam às competências específicas de Linguagens (ver linguagens.md)."]
        else:
            comp_linhas = ["", "Competências específicas da área (texto literal; o número é o primeiro dígito do código):", ""]
            comp_linhas += [f"- Competência {k}: {v}" for k, v in sorted(competencias[area].items())]
        escrever(
            os.path.join(saida, rel),
            f"{nome}: Ensino Médio",
            [f"Fonte: {FONTE_EM}. Texto literal.",
             f"Total: {len(linhas)} habilidades. As habilidades do Ensino Médio não têm seriação."] + comp_linhas,
            colunas,
            linhas,
        )
        indice.append(("Ensino Médio", nome, "sem seriação", rel.replace(os.sep, "/"), len(linhas)))


def gerar_indice(saida, indice):
    totais = defaultdict(int)
    for etapa, _, _, _, n in indice:
        totais[etapa.split(",")[0]] += n
    with open(os.path.join(saida, "indice.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# Índice da BNCC\n\n")
        f.write("Use este índice para abrir só o arquivo necessário. Cada arquivo tem uma habilidade por linha, "
                "com o texto literal do documento oficial do MEC.\n\n")
        f.write("## Como ler os códigos\n\n")
        f.write("- Educação Infantil: `EI` + faixa etária (01 bebês, 02 crianças bem pequenas, 03 crianças pequenas) "
                "+ campo (EO, CG, TS, EF, ET) + número. Exemplo: EI02TS01.\n")
        f.write("- Ensino Fundamental: `EF` + ano ou bloco de anos + componente + número. Exemplo: EF06MA01. "
                "Blocos: 12 = 1º e 2º anos, 15 = 1º ao 5º, 35 = 3º ao 5º, 67 = 6º e 7º, 69 = 6º ao 9º, 89 = 8º e 9º. "
                "Componentes: LP, AR, EF (Educação Física), LI, MA, CI, GE, HI, ER.\n")
        f.write("- Ensino Médio: `EM13` + área (LGG, LP, MAT, CNT, CHS) + número. Nas áreas LGG, MAT, CNT e CHS, "
                "o primeiro dígito do número é a competência específica, cujo texto está no início do arquivo da área. Exemplo: EM13LGG103.\n\n")
        f.write("## Arquivos\n\n")
        f.write("| Etapa | Componente ou área | Anos | Arquivo | Habilidades |\n| --- | --- | --- | --- | --- |\n")
        for etapa, comp, anos, rel, n in indice:
            f.write(f"| {etapa} | {comp} | {anos} | `{rel}` | {n} |\n")
        f.write("\n## Qual arquivo abrir para um ano do Ensino Fundamental\n\n")
        f.write("Todos os componentes, exceto Língua Portuguesa, têm um arquivo por segmento. Abra o do segmento e use "
                "a coluna \"Aplica-se aos anos\" para filtrar o ano (códigos de bloco, como EF12, EF15, EF35, EF67, "
                "EF69 e EF89, valem para vários anos).\n\n")
        f.write("Língua Portuguesa é dividida em arquivos por bloco de anos. Para planejar um ano, abra os dois arquivos indicados:\n\n")
        f.write("| Ano | Arquivos de Língua Portuguesa |\n| --- | --- |\n")
        prefixo = {"anos-iniciais": "ensino-fundamental/anos-iniciais/lingua-portuguesa-",
                   "anos-finais": "ensino-fundamental/anos-finais/lingua-portuguesa-"}
        pares = {1: "1o-e-2o", 2: "1o-e-2o", 3: "3o-ao-5o", 4: "3o-ao-5o", 5: "3o-ao-5o",
                 6: "6o-e-7o", 7: "6o-e-7o", 8: "8o-e-9o", 9: "8o-e-9o"}
        for ano in range(1, 10):
            seg = "anos-iniciais" if ano <= 5 else "anos-finais"
            comum = "1o-ao-5o" if ano <= 5 else "6o-ao-9o"
            f.write(f"| {ano}º ano | `{prefixo[seg]}{comum}.md` e `{prefixo[seg]}{pares[ano]}.md` |\n")
        total = sum(totais.values())
        f.write(f"\n## Totais\n\n| Etapa | Habilidades |\n| --- | --- |\n")
        for e, n in totais.items():
            f.write(f"| {e} | {n} |\n")
        f.write(f"| **Total** | **{total}** |\n\n")
        f.write("O complemento de Computação à BNCC (2022) não está incluído nesta versão.\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ei-ef", required=True, help="PDF oficial da BNCC (Educação Infantil e Ensino Fundamental)")
    ap.add_argument("--em", required=True, help="PDF oficial da BNCC do Ensino Médio")
    ap.add_argument("--saida", required=True, help="pasta onde os arquivos Markdown serão gravados")
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        texto_ef, pdf_ef = pdf_para_texto(a.ei_ef, tmp)
        texto_em, _ = pdf_para_texto(a.em, tmp)
        objetos, _ordem = processar_objetos(pdf_ef)
        competencias = extrair_competencias_em(texto_em)

    ei = escolher(extrair(texto_ef, "EI"), "ultima")
    ef = escolher(extrair(texto_ef, "EF"), "ultima")
    em = escolher(extrair(texto_em, "EM"), "primeira")
    print(f"Extraidos: EI={len(ei)} EF={len(ef)} EM={len(em)} total={len(ei) + len(ef) + len(em)}")

    indice = []
    gerar_ei(ei, a.saida, indice)
    gerar_ef(ef, a.saida, indice, objetos)
    gerar_em(em, a.saida, indice, competencias)
    gerar_indice(a.saida, indice)
    print(f"Arquivos gravados em {a.saida}")


if __name__ == "__main__":
    main()
