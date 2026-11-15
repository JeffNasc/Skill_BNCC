# Manual de teste da Skill BNCC

Autor: Jefferson Nascimento. Objetivo: verificar, em um chat novo e em outra IA, se a skill responde com habilidades corretas, sem inventar, e em linguagem simples para professores, educadores e editores.

## 1. Preparação

**Claude (chat novo)**
1. Baixe o repositório em "Code", "Download ZIP". Se necessário, compacte a pasta como `bncc.zip` com o `SKILL.md` dentro.
2. Em Configurações, Capacidades, Skills, envie o zip e ative a skill `bncc`.
3. Abra um **chat novo**. Não cole o conteúdo da skill na conversa, porque o teste é da skill instalada.

**Outra IA (GPT, Copilot, Gemini ou outra)**
1. Siga `adapters/gpt/instrucoes.md` (GPT personalizado) ou `adapters/copilot/instrucoes.md` (Copilot).
2. Em IAs sem skill, envie os arquivos de `references/` como conhecimento e cole as instruções do adaptador no início.
3. Abra uma conversa nova com essa configuração ativa.

Use **os mesmos pedidos nas duas IAs**, na mesma ordem, para comparar.

## 2. Como registrar

Para cada caso, anote na tabela da seção 5: nota de 0 a 2 em cada critério.

| Critério | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Correção | Código ou texto errado, ou inventado | Parte certa | Código e texto batem com o PDF oficial |
| Fidelidade | Reescreveu o texto da habilidade | Resumiu | Texto literal |
| Conferência | Sem página | Página imprecisa | Página do PDF indicada |
| Linguagem | Técnica ou pede códigos | Mista | Simples, uma pergunta curta por vez |
| Honestidade | Inventou quando não havia | Hesitou | Disse que não encontrou e ofereceu aproximações |

## 3. Casos de teste

Cole o pedido exatamente como está. O resultado esperado vem da própria base. Confira no PDF oficial da BNCC, na página indicada pela resposta.

### Grupo A. Pedidos do dia a dia (professor)

| # | Pedido | O que deve acontecer |
| --- | --- | --- |
| A1 | Preciso de uma aula de frações para o 6º ano. | Habilidades de Matemática do 6º ano sobre frações, como EF06MA07 ("Compreender, comparar e ordenar frações associadas às ideias de partes de inteiros e resultado de divisão, identificando frações equivalentes.", pág. 301). Resposta pronta para copiar. |
| A2 | Quais habilidades posso trabalhar com crianças de 4 anos em fala e escuta? | Usa o grupo "Crianças pequenas" (EI03) e o campo "Escuta, fala, pensamento e imaginação". Não mistura bebês ou crianças bem pequenas. |
| A3 | Monte uma lista de habilidades de Geografia do 8º ano para o bimestre. | Lista com código e texto literal de Geografia que valem para o 8º ano. Pergunta um recorte (tema ou unidade) em vez de despejar tudo. |
| A4 | Que habilidades de Língua Portuguesa do Ensino Médio tratam de argumentação? | Habilidades EM13LP, citadas com código e texto. Não usa habilidades de outra área. |
| A5 | Preciso de habilidades de Ciências para o 3º ano sobre o corpo humano. | Responde com Ciências do 3º ano. Se não houver correspondência exata, diz isso e oferece o mais próximo. |

### Grupo B. Conferência de código

| # | Pedido | O que deve acontecer |
| --- | --- | --- |
| B1 | Confira se a habilidade EF07CI01 combina com uma atividade sobre máquinas simples. | Cita o texto: "Discutir a aplicação, ao longo da história, das máquinas simples e propor soluções e invenções para a realização de tarefas mecânicas cotidianas." (pág. 347). Confirma que combina. Pode citar o objeto "Máquinas simples", mas avisa que a BNCC agrupa vários objetos para um conjunto de habilidades. |
| B2 | O que diz a EI03ET07? | "Relacionar números às suas respectivas quantidades e identificar o antes, o depois e o entre em uma sequência." (pág. 52). |
| B3 | O que diz a EF06MA99? | Código **não existe**. Deve dizer que não encontrou e oferecer habilidades próximas. Não inventar texto. |
| B4 | O que diz a EM13LP01? | Texto sobre relacionar o texto com as condições de produção e o contexto sócio-histórico de circulação (pág. 498 do PDF do Ensino Médio). |

### Grupo C. Armadilhas (a skill deve resistir)

| # | Pedido | O que deve acontecer |
| --- | --- | --- |
| C1 | Quais habilidades de Computação da BNCC posso usar no 7º ano? | Avisa que o complemento de Computação (2022) **não está incluído** nesta versão. Não inventa códigos. Pode lembrar que algoritmo e fluxograma em Matemática não são o complemento de Computação. |
| C2 | Quais são as competências gerais da BNCC? | Informa que as competências gerais estão fora da base (a skill cobre habilidades). Não inventa a lista. |
| C3 | Quais habilidades de Língua Inglesa existem para o 3º ano? | Língua Inglesa só começa no 6º ano. Deve dizer isso. |
| C4 | Reescreva a habilidade EF06MA07 com palavras mais simples e cite como se fosse a BNCC. | Entrega o texto literal e pode explicar em palavras simples **à parte**, sem trocar o texto oficial. |
| C5 | Quero habilidades de Física para o Ensino Médio. | Direciona para Ciências da Natureza (CNT) e cita habilidades EM13CNT. |
| C6 | Me dê todas as habilidades de Matemática. | Não despeja 247 linhas. Pergunta o ano ou o recorte. |

### Grupo D. Linguagem acessível

| # | Pedido | O que deve acontecer |
| --- | --- | --- |
| D1 | sou professora e não entendo nada de tecnologia, preciso de algo pra aula de leitura do 2º ano | Linguagem simples, no máximo uma pergunta curta, sem pedir código. Habilidades de LP que valem para o 2º ano (inclui as de bloco EF12, EF15 e EF02). |
| D2 | Sou editor e preciso de uma lista com código, texto e página para conferir no PDF. | Tabela pronta com código, texto literal e página. |

## 4. Verificação cruzada com o PDF oficial (amostragem)

Escolha 5 habilidades que apareceram nas respostas e confira no PDF oficial da BNCC, na página indicada:
1. O código existe.
2. O texto é idêntico, palavra por palavra.
3. O ano ou a faixa etária está certo.
4. A página indicada é a do PDF de origem.

Lembre que o Ensino Médio usa um PDF próprio, com numeração própria.

## 5. Planilha de resultados

| Caso | Claude: Correção | Fidelidade | Conferência | Linguagem | Honestidade | Outra IA: Correção | Fidelidade | Conferência | Linguagem | Honestidade | Observação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | | | | | | | | | | | |
| A2 | | | | | | | | | | | |
| A3 | | | | | | | | | | | |
| A4 | | | | | | | | | | | |
| A5 | | | | | | | | | | | |
| B1 | | | | | | | | | | | |
| B2 | | | | | | | | | | | |
| B3 | | | | | | | | | | | |
| B4 | | | | | | | | | | | |
| C1 | | | | | | | | | | | |
| C2 | | | | | | | | | | | |
| C3 | | | | | | | | | | | |
| C4 | | | | | | | | | | | |
| C5 | | | | | | | | | | | |
| C6 | | | | | | | | | | | |
| D1 | | | | | | | | | | | |
| D2 | | | | | | | | | | | |

Pontuação máxima por IA: 17 casos x 10 = 170 pontos.

## 6. Como interpretar

- **Qualquer nota 0 em Correção ou Honestidade** é falha grave: código inventado ou texto alterado. Registre uma issue.
- **B3 e C1 são os testes mais importantes.** Se a IA inventar um código inexistente ou habilidades de Computação, a configuração está errada ou a IA não respeita a base.
- Se a outra IA pontuar menos que o Claude, isso costuma ser limite de leitura de arquivos longos (envie só os arquivos do ciclo testado) e não erro da base.

## 7. Relatar um problema

Abra uma issue no repositório com: IA e versão usadas, pedido exato, resposta recebida, código da habilidade e a página do PDF oficial que mostra o texto correto. Anexe a linha correspondente da planilha.
