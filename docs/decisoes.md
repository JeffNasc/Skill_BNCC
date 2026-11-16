# Decisões do projeto

Autor: Jefferson Nascimento, com o Claude como assistente de desenvolvimento. Este documento registra o caminho da Skill BNCC, do problema à versão publicada, e o motivo de cada escolha.

## 1. O problema

IAs generativas citam habilidades da BNCC com códigos que não existem e textos que não são os oficiais. Para planejamento de aula e produção editorial, isso não serve. A pergunta que me guiou foi: como entregar à IA a base oficial, de um jeito que ela consulte sem inventar?

## 2. Contar no documento oficial

Antes de montar qualquer coisa, mandei contar as habilidades nos PDFs do MEC e conferi o resultado, pelos códigos únicos entre parênteses. Cheguei a 1.576: 93 na Educação Infantil, 1.304 no Ensino Fundamental e 179 no Ensino Médio.

Sites citam 183 habilidades no Ensino Médio. O PDF específico do Ensino Médio traz 179, e o PDF de Educação Infantil e Fundamental guarda, nas páginas finais, uma versão anterior do Ensino Médio com 183 códigos. Decidi seguir o documento do Ensino Médio e registrar a diferença.

## 3. Texto literal, em arquivos pequenos

Escolhi não reescrever nada. Uma skill que parafraseia a BNCC deixa de ser fonte. Quebrei a base por etapa, componente e bloco de anos e criei um índice que diz qual arquivo abrir, para a IA carregar só o necessário. Língua Portuguesa, o maior componente, foi dividida por bloco de anos, e o maior arquivo caiu de 96 KB para 41 KB.

## 4. Organização curricular

Acrescentei a unidade temática e o objeto de conhecimento de cada habilidade do Ensino Fundamental, lendo a geometria das tabelas do PDF. No Ensino Médio, incluí o texto das competências específicas no topo de cada área. Em todas as linhas, mantive a página do PDF de origem, para quem precisa conferir.

## 5. Os testes que me fizeram mudar de ideia

Conduzi, com o Claude como assistente, baterias de teste que simulam professores de cada ciclo, além de uma bateria automática contra os PDFs. Elas encontraram falhas reais, e eu decidi como corrigir cada uma:

- O filtro por ano perdia mais da metade das habilidades de Língua Portuguesa. Criei a coluna "Aplica-se aos anos".
- Subitens de objeto saíam com marcador duplicado.
- O validador conferia páginas por faixas amplas. Passei a conferir a página exata pelo rodapé do PDF.
- A EF03LP11 saiu com "gráficovisuais" em vez de "gráfico-visuais". Corrigi o texto e o extrator.
- O índice do pacote para GPT e Copilot apontava para arquivos que não existiam.

Também validei a ligação entre objeto e habilidade por dois algoritmos independentes e conferi páginas de seis componentes visualmente. Descobri que a BNCC agrupa vários objetos em uma célula sem indicar qual vale para qual habilidade, e decidi que a skill não afirma ligação um a um.

## 6. O público

Professores, educadores e editores nem sempre têm intimidade com tecnologia. Defini regras de conversa: português simples, nenhuma exigência de código, uma pergunta curta por vez e resposta pronta para copiar no plano de aula, com a página para conferência.

## 7. Computação (2022) fica de fora

O complemento de Computação depende do anexo oficial do Parecer CNE/CEB 2/2022, e não consegui acessá-lo no site do MEC. Existem fontes secundárias, mas usá-las quebraria a garantia de texto literal. Decidi publicar sem Computação e avisar isso na skill, no README e no post. Ela entra na versão 1.1.

## 8. Publicação e verificação aberta

Publiquei o repositório com guia de teste, manual, prompt de teste que funciona em qualquer IA e scripts de verificação. Uma GitHub Action roda a contagem e os testes de regressão a cada envio. Uma avaliação independente apontou fragilidades (recuperação de habilidades de vários blocos, conferência de página, código inexistente), e eu as corrigi nas versões 1.0.1 e 1.0.2.

## O que ainda falta

- Módulo de Computação (2022), a partir do anexo oficial.
- Testes com professores reais, em conversas independentes e em mais de uma IA.
