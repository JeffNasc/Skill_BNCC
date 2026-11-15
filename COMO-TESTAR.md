# Como instalar e testar a Skill BNCC

Qualquer pessoa pode testar. Escolha a plataforma que você usa.

## Claude (skill nativa)

1. Baixe o repositório: botão verde "Code", depois "Download ZIP".
2. Compacte a pasta do repositório em um arquivo `.zip` que tenha `SKILL.md` na raiz da pasta da skill (a pasta deve se chamar `bncc`, ou `skill-bncc`).
3. No Claude, abra Configurações, Capacidades, Skills, e envie o `.zip`.
4. Ative a skill e peça, por exemplo: "Preciso de uma aula de frações para o 6º ano."

## GPT personalizado

Siga `adapters/gpt/instrucoes.md`. Você vai montar um pacote de 16 arquivos com `scripts/empacotar_gpt.py` (ou usar os arquivos de `references/` diretamente) e colar as instruções no campo do GPT.

## Microsoft Copilot (agentes)

Siga `adapters/copilot/instrucoes.md`.

## Pedidos para testar

- "Preciso de uma aula de frações para o 6º ano."
- "Quais habilidades posso trabalhar com crianças de 4 anos em Escuta, fala, pensamento e imaginação?"
- "A habilidade EF07CI01 combina com uma atividade sobre máquinas simples?"
- "Monte uma lista de habilidades de Geografia do 8º ano para o bimestre."
- "Que habilidades de Língua Portuguesa do Ensino Médio tratam de argumentação?"
- "Quais habilidades de Computação da BNCC posso usar?" (a skill deve avisar que Computação 2022 não está incluída)

## O que conferir

- O código e o texto da habilidade batem com o PDF oficial da BNCC na página indicada.
- A skill avisa quando nenhuma habilidade corresponde ao pedido, em vez de inventar uma.
- A linguagem é simples, sem exigir códigos de quem pergunta.

## Encontrou um erro?

Abra uma issue neste repositório com: o pedido feito, a resposta recebida, o código da habilidade e a página do PDF oficial que mostra o texto correto.

## Conferir a base por conta própria

Os scripts em `scripts/` regeneram a base a partir dos PDFs oficiais do MEC e validam contagem, páginas e ligação entre objeto e habilidade. Veja a seção de validação do `README.md`.
