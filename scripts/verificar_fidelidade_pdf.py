#!/usr/bin/env python3
"""Confere se o texto literal de cada habilidade da base aparece nos PDFs oficiais.

Uso:
  python3 -I verificar_fidelidade_pdf.py <pasta_references> <pdf_ei_ef_reparado> <pdf_ensino_medio>

O PDF de EI e EF costuma precisar de reparo antes (qpdf --qdf ou qpdf entrada.pdf saida.pdf).
Para EF, confere cada palavra (4+ letras) nas páginas onde o código aparece, só na coluna de habilidades (pdfplumber). Para EI e EM, usa o texto da página (pypdf).
Sai com código 1 se algum texto não for encontrado.
"""
import re, sys, glob, unicodedata
from pathlib import Path
import pdfplumber
from pypdf import PdfReader


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[­\u0002\u0007]", "", s)
    return re.sub(r"[\s\-‐‑–]+", "", s).lower()


def linhas(caminho):
    for l in open(caminho, encoding="utf-8"):
        if l.startswith("| ") and not l.startswith("| Código") and not l.startswith("| ---"):
            yield [x.replace("\\|", "|") for x in re.split(r"(?<!\\) \| ", l.rstrip("\n")[2:-2])]


def textos(pasta, prefixo):
    out = {}
    for f in glob.glob(f"{pasta}/**/*.md", recursive=True):
        if f.endswith("indice.md"):
            continue
        for c in linhas(f):
            if c[0].startswith(prefixo):
                out[c[0]] = c[3] if prefixo == "EI" else c[-2]
    return out


def paginas_ef(pdf):
    """Para cada código EF, junta o texto (sem espaços) das páginas onde ele aparece na coluna de habilidades."""
    blocos = {}
    for pg in pdfplumber.open(pdf).pages:
        ws = pg.extract_words()
        cods = [w for w in ws if re.fullmatch(r"\(EF\d{2}[A-Z]{2}\d{2}\)", w["text"])]
        if not cods:
            continue
        x = min(w["x0"] for w in cods) - 4
        blob = norm(" ".join(w["text"] for w in ws if w["x0"] >= x))
        for w in cods:
            blocos.setdefault(w["text"][1:-1], []).append(blob)
    return {c: "".join(v) for c, v in blocos.items()}


def palavras_ausentes_ef(base, pdf):
    """Cada palavra (4+ letras) do texto da habilidade precisa existir nas páginas onde o código aparece.
    A conferência por palavras evita falsos alarmes causados pela ordem das linhas em tabelas de várias colunas."""
    paginas = paginas_ef(pdf)
    ausentes = []
    for c, t in base.items():
        blob = paginas.get(c)
        if blob is None:
            ausentes.append(c)
            continue
        if any(norm(w) not in blob for w in re.findall(r"[^\W\d_]{4,}", t.replace("-", " "))):
            ausentes.append(c)
    return ausentes


def texto_pypdf(pdf):
    return norm(" ".join((p.extract_text() or "") for p in PdfReader(pdf).pages))


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    pasta, pdf_ef, pdf_em = sys.argv[1:4]
    falhou = False
    for nome, prefixo, fonte in (
        ("EF", "EF", None),
        ("EI", "EI", lambda: texto_pypdf(pdf_ef)),
        ("EM", "EM", lambda: texto_pypdf(pdf_em)),
    ):
        base = textos(pasta, prefixo)
        if fonte is None:
            ausentes = palavras_ausentes_ef(base, pdf_ef)
        else:
            pdf = fonte()
            ausentes = [c for c, t in base.items() if norm(t) not in pdf]
        print(f"{nome}: {len(base)} textos conferidos, {len(ausentes)} não encontrados no PDF", ausentes[:10])
        falhou = falhou or bool(ausentes)
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
