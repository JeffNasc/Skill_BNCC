# Skill BNCC

Base de consulta gratuita e de código aberto com as habilidades da Base Nacional Comum Curricular (BNCC), organizada em Markdown para uso com assistentes de IA. É uma alternativa sugerida para projetos de educação que usam inteligência artificial e precisam citar habilidades com código e texto fiéis ao documento oficial.

Funciona como skill nativa do Claude e pode ser reaproveitada em um GPT personalizado e em agentes do Microsoft Copilot.

## O que há na base

| Etapa | Habilidades |
| --- | --- |
| Educação Infantil (objetivos de aprendizagem e desenvolvimento) | 93 |
| Ensino Fundamental | 1.304 (574 nos anos iniciais e 730 nos anos finais) |
| Ensino Médio | 179 |
| **Total** | **1.576** |

Cada habilidade ocupa uma linha, com o texto literal, o código oficial e a página do PDF de origem. No Ensino Fundamental há uma coluna "Aplica-se aos anos" com a lista explícita de anos (por exemplo, "1, 2"), que facilita filtrar habilidades de bloco, e os arquivos de Língua Portuguesa são divididos por bloco de anos para economizar contexto. No Ensino Fundamental, a linha traz também a unidade temática (ou prática de linguagem), o objeto de conhecimento e, quando existem, o campo de atuação ou o eixo.

## Pensada para quem não é de tecnologia

A skill foi desenhada para professores, educadores e editores. Ela conversa em português simples, não pede códigos, faz uma pergunta curta por vez quando falta alguma informação e devolve o resultado pronto para copiar em um plano de aula ou material, com a página do PDF oficial para conferência.

Exemplos de pedidos:

- "Preciso de uma aula de frações para o 6º ano."
- "Quais habilidades de leitura posso trabalhar com crianças de 4 anos?"
- "Quero conferir se a habilidade EF07CI01 combina com minha atividade sobre máquinas simples."
- "Monte uma lista de habilidades de Geografia do 8º ano para o bimestre."
- "Que habilidades de Língua Portuguesa do Ensino Médio tratam de argumentação?"

## Estrutura

```
skill-bncc/
  SKILL.md                      instruções da skill (curtas)
  references/
    indice.md                   mapa dos arquivos e guia dos códigos
    educacao-infantil.md
    ensino-fundamental/
      anos-iniciais/            um arquivo por componente (Língua Portuguesa em 3 partes por bloco de anos)
      anos-finais/              um arquivo por componente (Língua Portuguesa em 3 partes por bloco de anos)
    ensino-medio/               um arquivo por área, com o texto das competências específicas no topo
  scripts/
    extrair_bncc.py             gera references/ a partir dos PDFs oficiais
    extrair_objetos.py          liga cada habilidade a unidade e objeto, pela geometria das tabelas
    extrair_competencias_em.py  extrai o texto das competências específicas do Ensino Médio
    validar_bncc.py             confere contagens, formato, numeração e páginas
    verificar_ligacao.py        verifica por dois caminhos independentes a ligação entre objeto e habilidade
    empacotar_gpt.py            junta os arquivos em 16 para GPT e Copilot
  adapters/
    gpt/instrucoes.md
    copilot/instrucoes.md
```

A skill carrega só o índice e o arquivo necessário a cada pergunta, o que mantém o consumo de contexto baixo.

## Como usar

**Claude:** copie a pasta `skill-bncc` como skill (arquivo `SKILL.md` na raiz) e peça, por exemplo: "Quais habilidades de Matemática do 7º ano tratam de proporcionalidade?"

**GPT personalizado:** siga `adapters/gpt/instrucoes.md`. O script `empacotar_gpt.py` gera 16 arquivos, dentro do limite de 20 do conhecimento de um GPT.

**Microsoft Copilot:** siga `adapters/copilot/instrucoes.md`.

## Como a base foi construída e validada

1. Os textos vêm dos PDFs oficiais do MEC (EI e EF, versão homologada em 2017; Ensino Médio, documento de 2018). Nada foi digitado ou reescrito.
2. A extração usa `pdftotext` e lê a posição das tabelas com `pdfplumber`. Quando o PDF está danificado, o `qpdf` o repara antes.
3. A contagem oficial foi feita de forma independente, sobre os códigos únicos entre parênteses nos PDFs, e é a referência do validador.
4. `validar_bncc.py` confere, em cada arquivo, o formato das linhas, os códigos válidos, a ausência de duplicidades, a numeração sem lacunas, a presença de unidade e objeto, as faixas de páginas e os totais por arquivo e por etapa.

Para regenerar e validar:

```
python3 scripts/extrair_bncc.py --ei-ef BNCC_EI_EF_110518_versaofinal_site.pdf --em BNCC_EnsinoMedio_embaixa_site_110518.pdf --saida references
python3 scripts/validar_bncc.py references
```

Requisitos: Python 3, `pdfplumber`, `pdftotext` (poppler-utils) e, se o PDF estiver danificado, `qpdf`.

## Limites desta versão

- **Computação (2022) fora desta versão.** Não incluímos o complemento de Computação à BNCC (Parecer CNE/CEB 2/2022), porque o anexo oficial não estava acessível no site do MEC e optamos por não usar fontes secundárias. Ele entrará depois como módulo separado.
- Não inclui as competências gerais, as competências específicas do Ensino Fundamental, os textos introdutórios nem o complemento de Computação (Parecer CNE/CEB 2/2022 e Resolução CNE/CEB 1/2022). O complemento entrará como um módulo separado, depois de conferido linha a linha no anexo oficial.
- O PDF de EI e EF traz, nas páginas finais, uma versão anterior do Ensino Médio (183 códigos). A base usa o PDF específico do Ensino Médio (179 habilidades).
- Nas tabelas do PDF, quando uma célula de objetos reúne vários itens, eles valem para o conjunto de habilidades da célula (por exemplo, em Ciências do 7º ano, quatro objetos para EF07CI01 a EF07CI06). A base reproduz o agrupamento, sem inventar ligação um a um.
- Em um caso (EF67LP27), o PDF oficial não traz ponto final. O texto foi mantido literal.
- A BNCC pode ser atualizada pelo MEC. Para uso normativo, confira sempre o documento oficial.

## Licença

Código, organização e documentação sob licença MIT. O texto da BNCC é de titularidade do Ministério da Educação e está reproduzido sem alterações. Veja `LICENSE`.

## Autoria

Jefferson Nascimento.

## Testar

Veja [COMO-TESTAR.md](COMO-TESTAR.md) e o [MANUAL-DE-TESTE.md](MANUAL-DE-TESTE.md) para instalar e testar. Versões: [CHANGELOG.md](CHANGELOG.md).

**Aviso:** o complemento de Computação (2022) ainda não está incluído nesta versão.

## Verificação independente

Qualquer pessoa pode conferir a base contra os PDFs oficiais do MEC:

```
python3 -I tests/regressao.py
python3 -I scripts/verificar_fidelidade_pdf.py references <pdf_ei_ef_reparado> <pdf_ensino_medio>
python3 -I scripts/validar_bncc.py
```

O segundo script confere o texto de todas as habilidades e a página (rodapé impresso) contra os PDFs. O primeiro roda a cada push no GitHub.
