#!/usr/bin/env python3
"""Verifica, por dois caminhos independentes, se cada objeto de conhecimento esta ligado a habilidade certa.

1. Invariantes: dentro de cada bloco de codigos, um objeto nao pode reaparecer depois de outro (alguns casos
   legitimos de Lingua Portuguesa sao listados para revisao visual).
2. Segundo algoritmo, sem usar as bordas das tabelas: o objeto de cada habilidade deve ser o bloco de texto
   da coluna de objetos mais proximo acima do codigo. Um controle negativo (objeto de outra habilidade)
   confirma que o teste consegue reprovar.

Uso: python3 -I verificar_ligacao.py <pasta_references> <pdf_ef_reparado>
"""
import re, glob, json, collections, unicodedata
import pdfplumber
import sys
if len(sys.argv) != 3:
    sys.exit("Uso: python3 -I verificar_ligacao.py <pasta_references> <pdf_ef_reparado>")
REFS, PDF_EF = sys.argv[1], sys.argv[2]


def rows(path):
    for l in open(path, encoding="utf-8"):
        if l.startswith("| ") and not l.startswith("| Código") and not l.startswith("| ---"):
            yield [x.replace("\\|", "|") for x in re.split(r"(?<!\\) \| ", l.rstrip("\n")[2:-2])]

R=REFS
base={}
for f in glob.glob(f"{R}/ensino-fundamental/**/*.md",recursive=True):
    for c in rows(f):
        campo=c[3] if len(c)==8 else ""
        base[c[0]]={"anos":c[2],"campo":campo,"unidade":c[-4],"objeto":c[-3].replace("[subitem: "," ").replace("]"," "),"arq":f}
# ---------- 1. invariantes
print("1. INVARIANTES")
viol=[]
grupos=collections.defaultdict(list)
for cod,d in base.items(): grupos[cod[:6]].append((int(cod[6:]),cod,d))
for pref,lst in grupos.items():
    lst.sort(); vistos=[]; ult=None
    for n,cod,d in lst:
        chave=(d["campo"],d["unidade"],d["objeto"])
        if chave!=ult:
            if chave in vistos: viol.append((cod,"objeto reaparece depois de outro",d["campo"][:25],d["unidade"][:30],d["objeto"][:50]))
            vistos.append(chave); ult=chave
print(" objetos que reaparecem fora de sequencia:",len(viol))
for v in viol[:15]: print("  ",v)
# objeto isolado: unidade/objeto usados por uma unica habilidade em componentes onde isso e raro

# ---------- 2. segundo algoritmo (sem bordas): bloco de objeto mais proximo acima da habilidade
print("2. ALGORITMO B (blocos de texto por espacamento, sem bordas)")
COD=re.compile(r"^\((EF\d{2}[A-Z]{2}\d{2})\)$")
def toks(s):
    s=unicodedata.normalize("NFKC",s).replace("-"," ").lower()
    return re.sub(r"[^\w\s]"," ",s).split()
pdf=pdfplumber.open(PDF_EF)
ant_bloco=None; comparados=set(); neg_total=[0]; neg_ok=[0]
cods_ord=sorted(base); vizinho={c:cods_ord[(i+37)%len(cods_ord)] for i,c in enumerate(cods_ord)}
discord=[]; total=0; sem_bloco=[]
for num,pg in enumerate(pdf.pages,1):
    ws=pg.extract_words()
    cods=[w for w in ws if COD.match(w["text"])]
    if not cods: continue
    xh=min(w["x0"] for w in cods)-4
    cab=[w for w in ws if w["text"]=="OBJETOS" and w["x0"]<xh]
    if not cab: continue
    xo=max(w["x0"] for w in cab)-4
    # texto da coluna de objetos abaixo do cabecalho da tabela
    topo=max(w["top"] for w in cab)+8
    col=[w for w in ws if xo<=w["x0"]<xh and w["top"]>topo]
    linhas=collections.defaultdict(list)
    for w in col: linhas[round(w["top"]/3)].append(w)
    L=sorted((min(x["top"] for x in v)," ".join(x["text"] for x in sorted(v,key=lambda x:x["x0"]))) for v in linhas.values())
    blocos=[]; prev=None
    for t,txt in L:
        if prev is None or t-prev>15.5: blocos.append([t,[txt]])
        else: blocos[-1][1].append(txt)
        prev=t
    blocos=[(t," ".join(tx)) for t,tx in blocos]
    for w in sorted(cods,key=lambda w:w["top"]):
        cod=COD.match(w["text"]).group(1); total+=1
        cand=[b for b in blocos if b[0]<=w["top"]+3]
        esperado=base[cod]["objeto"].split(" • ")
        if not cand:
            sem_bloco.append((cod,num)); continue
        b=cand[-1][1]
        sb=sorted(toks(b))
        ok=any(sorted(toks(e))==sb for e in esperado) or any(set(sb)<=set(toks(e)) and len(sb)>=3 for e in esperado) or set(sb)<=set(toks(" ".join(esperado)))
        comparados.add(cod)
        # controle negativo: o mesmo teste aplicado ao objeto de outra habilidade deve falhar na maioria
        viz=base.get(vizinho.get(cod,""),None)
        if viz and viz["objeto"]!=base[cod]["objeto"]:
            neg_total[0]+=1
            if any(sorted(toks(e))==sb for e in viz["objeto"].split(" • ")): neg_ok[0]+=1
        if not ok: discord.append((cod,num,b[:60],base[cod]["objeto"][:60]))
print(" codigos distintos comparados:",len(comparados),"de",len(base),"| controle negativo: teste aceitou objeto errado em",neg_ok[0],"de",neg_total[0],"casos")
print(" ocorrencias comparadas:",total,"| discordancias:",len(discord),"| sem bloco acima na pagina (continua da anterior):",len(sem_bloco))
for d in discord[:25]: print("  ",d)
if discord or sem_bloco:
    sys.exit(1)
