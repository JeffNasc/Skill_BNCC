#!/usr/bin/env python3
"""Reune os arquivos de references/ em 16 arquivos para subir como Conhecimento em um GPT.

O GPT personalizado aceita ate 20 arquivos de conhecimento. Este script junta anos iniciais e anos
finais de cada componente do Ensino Fundamental e copia os demais arquivos.

Uso: python3 empacotar_gpt.py <pasta_references> <pasta_saida>
"""
import os
import re
import shutil
import sys

SUFIXO_LP = r"-(?:1o-ao-5o|1o-e-2o|3o-ao-5o|6o-ao-9o|6o-e-7o|8o-e-9o)"


def indice_do_pacote(texto):
    """Reescreve o indice para os nomes de arquivo do pacote (ef-*.md e em-*.md)."""
    # a tabela "Qual arquivo abrir" nao se aplica ao pacote, onde Lingua Portuguesa e um so arquivo
    texto = re.sub(r"## Qual arquivo abrir.*?(?=## Totais)",
                   "## Como filtrar por ano\n\nAbra o arquivo do componente e use a coluna \"Aplica-se aos anos\" "
                   "para filtrar o ano. No pacote, Língua Portuguesa reúne os anos iniciais e finais em um só arquivo.\n\n",
                   texto, flags=re.S)
    linhas, vistos = [], set()
    for l in texto.splitlines():
        m = re.search(r"`(ensino-fundamental/anos-(?:iniciais|finais)/([a-z\-]+?)(?:" + SUFIXO_LP + r")?\.md)`", l)
        if m:
            novo = f"`ef-{m.group(2)}.md`"
            if m.group(2) == "lingua-portuguesa":
                if "lingua-portuguesa" in vistos:
                    continue
                vistos.add("lingua-portuguesa")
                l = re.sub(r"^\| [^|]+ \| Língua Portuguesa \| [^|]+ \| `[^`]+` \| \d+ \|$",
                           "| Ensino Fundamental | Língua Portuguesa | 1º ao 9º ano | `ef-lingua-portuguesa.md` | 391 |", l)
            else:
                l = l.replace(m.group(0), novo)
        l = re.sub(r"`ensino-medio/([a-z\-]+)\.md`", r"`em-\1.md`", l)
        linhas.append(l)
    return "\n".join(linhas) + "\n"


def main(ref, saida):
    os.makedirs(saida, exist_ok=True)
    with open(os.path.join(ref, "indice.md"), encoding="utf-8") as f:
        indice = indice_do_pacote(f.read())
    with open(os.path.join(saida, "00-indice.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(indice)
    shutil.copy(os.path.join(ref, "educacao-infantil.md"), os.path.join(saida, "educacao-infantil.md"))
    ini = os.path.join(ref, "ensino-fundamental", "anos-iniciais")
    fin = os.path.join(ref, "ensino-fundamental", "anos-finais")
    # Lingua Portuguesa esta dividida em partes por bloco de anos; juntamos tudo num arquivo por componente.
    componentes = {}
    for pasta in (ini, fin):
        for nome in sorted(os.listdir(pasta)):
            base = nome[:-3]
            if base.startswith("lingua-portuguesa-"):
                base = "lingua-portuguesa"
            componentes.setdefault(base, []).append(os.path.join(pasta, nome))
    for base, caminhos in sorted(componentes.items()):
        partes = [re.sub(r"^Este arquivo traz .*\n", "", open(c, encoding="utf-8").read(), flags=re.M).rstrip() + "\n"
                  for c in caminhos]
        nome = base + ".md"
        with open(os.path.join(saida, f"ef-{nome}"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n\n".join(partes))
    em = os.path.join(ref, "ensino-medio")
    for nome in sorted(os.listdir(em)):
        shutil.copy(os.path.join(em, nome), os.path.join(saida, f"em-{nome}"))
    print(f"{len(os.listdir(saida))} arquivos em {saida}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
