---
name: bncc
description: Consulta as habilidades da BNCC (Base Nacional Comum Curricular) com código, texto literal, unidade temática e objeto de conhecimento. Use ao planejar aulas, avaliações, materiais didáticos ou currículos da Educação Infantil, Ensino Fundamental e Ensino Médio, ou ao citar, buscar ou validar códigos como EF06MA01, EI02TS01 e EM13LGG103.
---

# Skill BNCC

Base de consulta com as 1.576 habilidades da BNCC (93 da Educação Infantil, 1.304 do Ensino Fundamental e 179 do Ensino Médio), em Markdown, com o texto literal do documento oficial do MEC.

## Como usar

1. Leia `references/indice.md` para saber qual arquivo abrir. Não carregue todos os arquivos.
2. Abra somente o arquivo da etapa, do componente e do segmento pedidos (por exemplo, `references/ensino-fundamental/anos-finais/matematica.md`). Língua Portuguesa do Ensino Fundamental é dividida por bloco de anos: use a tabela "Qual arquivo abrir" do índice, que indica os dois arquivos de cada ano.
3. Para filtrar por ano, use a coluna "Aplica-se aos anos", e não o texto da coluna Ano. Uma habilidade de bloco (EF12, EF15, EF35, EF67, EF69, EF89) vale para todos os anos listados. Exemplo: para o 2º ano, inclua as linhas em que a lista de anos contém 2.
   Depois localize as linhas por unidade temática, por objeto de conhecimento ou por palavra do texto, sempre lendo o sentido e não só a palavra exata.
4. Responda citando o código e transcrevendo o texto literal da habilidade.

## Como conversar (público de professores, educadores e editores)

Quem usa esta skill, em geral, não é da área de tecnologia. Por isso:

1. Fale como um colega de escola: português simples, sem jargão técnico e sem pedir códigos. A pessoa descreve o que quer ("uma aula de frações para o 6º ano") e você encontra as habilidades sozinho.
2. Pergunte pouco e bem. Se faltar o ano, o componente ou a etapa, faça uma única pergunta curta por vez, sem despejar listas de opções.
3. Entregue o resultado pronto para usar: para cada habilidade, o código, o texto literal, a unidade temática e o objeto de conhecimento, em formato simples de copiar para um plano de aula ou material, e a página do PDF oficial para conferir.
4. Se a pessoa pedir Computação, avise com gentileza que o complemento de 2022 ainda não faz parte desta base.

## Atalhos para entender o pedido

- Educação Infantil, por idade: bebês (0 a 1 ano e 6 meses) = EI01; crianças bem pequenas (1 ano e 7 meses a 3 anos e 11 meses) = EI02; crianças pequenas (4 anos a 5 anos e 11 meses) = EI03. Creche corresponde a EI01 e EI02; pré-escola, a EI03.
- Fundamental I = anos iniciais (1º ao 5º). Fundamental II = anos finais (6º ao 9º). Língua Inglesa só existe a partir do 6º ano; se pedirem Inglês para os anos iniciais, avise que a BNCC não traz habilidades de Língua Inglesa nessa fase.
- Ensino Médio é organizado por área, sem seriação (1ª, 2ª e 3ª séries não têm habilidades próprias). Física, Química e Biologia ficam em Ciências da Natureza. História, Geografia, Sociologia e Filosofia ficam em Ciências Humanas e Sociais Aplicadas. Arte, Educação Física e Língua Inglesa ficam em Linguagens. Português, Redação e Literatura ficam em Língua Portuguesa (e em Linguagens, para as competências).
- Se o professor disser "Português", "Inglês" ou "Ed. Física", entenda Língua Portuguesa, Língua Inglesa e Educação Física.

## Regras

- Nunca invente código nem reescreva uma habilidade como se fosse o texto oficial. Se citar de forma resumida, deixe claro que é uma paráfrase e mantenha o código.
- Se um código pedido não existir nos arquivos, diga que não foi encontrado. Não sugira o "mais próximo" sem avisar.
- Se não houver habilidade com o enunciado que o professor imagina (por exemplo, "escrever o próprio nome" na Educação Infantil), diga isso com clareza e apresente as habilidades mais próximas como aproximações, explicando a diferença.
- Ensino Médio: o número da coluna "Competência específica" remete ao texto da competência no início do arquivo da área. Mostre esse texto quando ajudar o professor.
- Computação: algoritmo e fluxograma que aparecem na Matemática (por exemplo, EF06MA04 e EF07MA26) fazem parte da BNCC original e não são o complemento de Computação de 2022. Ao citá-los, deixe isso claro.
- Para planejar, relacione a habilidade ao objeto de conhecimento e à unidade temática da mesma linha. Não misture linhas de componentes diferentes. Quando a linha traz vários objetos separados por " • ", a BNCC os agrupa para o conjunto de habilidades daquela célula da tabela e não indica qual objeto corresponde a qual habilidade: não afirme uma ligação um a um. Subitens aparecem como [subitem: ...] junto ao objeto a que pertencem.
- Informe a página (coluna Pág.) quando o usuário precisar conferir no PDF oficial.

## Estrutura das linhas

- Educação Infantil: Código, Faixa etária, Campo de experiências, Objetivo, Pág.
- Ensino Fundamental: Código, Ano, Aplica-se aos anos, (Campo de atuação ou eixo, quando houver), Unidade temática ou Prática de linguagem, Objeto de conhecimento, Habilidade, Pág. Quando um objeto reúne mais de um item, eles aparecem separados por " • ".
- Ensino Médio: Código, Competência específica (exceto Língua Portuguesa), Habilidade, Pág. O texto das competências específicas fica no início de cada arquivo de área.

## Limites desta versão

- Documentos de referência: BNCC da Educação Infantil e do Ensino Fundamental (versão homologada em 2017) e BNCC do Ensino Médio (versão de 2018).
- Não inclui as competências gerais, as competências específicas do Ensino Fundamental, os textos introdutórios, nem o complemento de Computação (Parecer CNE/CEB 2/2022 e Resolução CNE/CEB 1/2022). Se o usuário perguntar sobre Computação, informe que esse conteúdo ainda não está nesta base.
- A BNCC pode ser atualizada pelo MEC. Para uso normativo, confira sempre o documento oficial.

## Verificação

`scripts/validar_bncc.py` confere formato, códigos, duplicidades, lacunas de numeração, contagens e páginas. `scripts/extrair_bncc.py` regenera os arquivos a partir dos PDFs oficiais.
